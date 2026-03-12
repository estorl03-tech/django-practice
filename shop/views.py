from typing import Dict, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction  # 🛡️ 排他制御用
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from .models import Order, Product
from .services import (
    add_item_to_cart,
    clear_cart,
    create_order,
    get_cart_count,
    get_cart_details,
)


def product_list(request: HttpRequest) -> HttpResponse:
    """商品一覧を表示（検索機能 & HTMX部分更新対応）"""
    query = request.GET.get("q")
    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    cart_count = get_cart_count(request.session)
    context = {
        "products": products,
        "cart_count": cart_count,
        "query": query,
    }

    if request.headers.get("HX-Request") and not request.headers.get("HX-Boosted"):
        return render(request, "shop/partials/product_grid.html", context)

    return render(request, "shop/product_list.html", context)


@require_POST
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """カート追加：最新の在庫状況をDBから直接チェック（排他制御付き）"""

    # 🛡️ セキュリティ対策：トランザクション内でDB行をロックし、連打による在庫計算の狂いを防ぐ
    with transaction.atomic():
        # select_for_update() により、処理が終わるまで他からの更新を待機させる
        product = get_object_or_404(Product.objects.select_for_update(), id=product_id)

        cart: Dict[str, int] = request.session.get("cart", {})
        current_qty = cart.get(str(product_id), 0)

        # 在庫不足の判定
        if current_qty + 1 > product.stock:
            available_qty = max(0, product.stock - current_qty)
            messages.error(request, f"{product.name} の在庫不足（残り: {available_qty}個）")

            if request.headers.get("HX-Request"):
                current_total = get_cart_count(request.session)
                msg_html = render_to_string("shop/partials/messages.html", request=request)
                cart_html = f'<span id="cart-count" class="badge" hx-swap-oob="true">{current_total}</span>'
                return HttpResponse(msg_html + cart_html)
            return redirect("shop:product_list")

        # 正常な追加処理
        total_quantity = add_item_to_cart(request.session, product_id)

    # HTMXレスポンス生成
    if request.headers.get("HX-Request"):
        # カート個数バッジの更新（OOB）
        cart_html = f'<span id="cart-count" class="badge" hx-swap-oob="true">{total_quantity}</span>'

        # 在庫表示のリアルタイム更新（OOB）
        updated_cart = request.session.get("cart", {})
        item_qty = updated_cart.get(str(product_id), 0)
        display_stock = product.stock - item_qty

        if display_stock > 0:
            stock_text = f"残り {display_stock} 個"
            stock_style = "color: var(--pico-muted-color);"
        else:
            stock_text = "在庫切れ"
            stock_style = "color: var(--pico-danger-color); font-weight: bold;"

        stock_html = format_html(
            '<span id="stock-{}" hx-swap-oob="true" style="{}">{}</span>', product.id, stock_style, stock_text
        )

        return HttpResponse(cart_html + stock_html)

    return redirect("shop:product_list")


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """チェックアウト（カート画面表示・注文確定処理）"""
    user = cast(User, request.user)
    cart_items, total_price, cart_count = get_cart_details(request.session)

    if request.method == "POST" and "submit_order" in request.POST and cart_items:
        try:
            # 🛡️ 注文作成サービス内でも在庫減算処理に atomic/select_for_update を使うことを推奨
            create_order(user, cart_items, total_price)
            request.session["cart"] = {}
            request.session.modified = True
            messages.success(request, "注文が完了しました！")

            if request.headers.get("HX-Request"):
                msg_html = render_to_string("shop/partials/messages.html", request=request)
                cart_zero_html = '<span id="cart-count" class="badge" hx-swap-oob="true">0</span>'
                complete_html = (
                    "<h2>ご注文ありがとうございました！</h2>"
                    "<p>注文処理が完了しました。</p>"
                    "<a href='/' class='outline'>トップページへ戻る</a>"
                )
                return HttpResponse(complete_html + msg_html + cart_zero_html)

            return render(request, "shop/complete.html")
        except ValidationError as e:
            messages.error(request, str(e))

    context = {"cart_items": cart_items, "total_price": total_price, "cart_count": cart_count}

    if request.headers.get("HX-Request"):
        table_html = render_to_string("shop/partials/cart_details.html", context, request=request)
        msg_html = render_to_string("shop/partials/messages.html", request=request)
        cart_count_html = f'<span id="cart-count" class="badge" hx-swap-oob="true">{cart_count}</span>'
        return HttpResponse(table_html + msg_html + cart_count_html)

    return render(request, "shop/checkout.html", context)


@require_POST
def update_cart_item(request: HttpRequest, product_id: int) -> HttpResponse:
    """カート内数量を操作（プラス・マイナス・削除ボタン）"""
    cart: Dict[str, int] = request.session.get("cart", {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        action = request.POST.get("action")
        try:
            with transaction.atomic():
                product = get_object_or_404(Product.objects.select_for_update(), id=product_id)
                if action == "add":
                    if product.stock <= cart[product_id_str]:
                        raise ValidationError(f"{product.name}の在庫不足（残り: {product.stock}個）")
                    cart[product_id_str] += 1
                elif action == "remove":
                    cart[product_id_str] -= 1
                elif action == "delete":
                    cart[product_id_str] = 0

                if cart[product_id_str] <= 0:
                    del cart[product_id_str]

                request.session["cart"] = cart
                request.session.modified = True
        except ValidationError as e:
            messages.error(request, str(e))

    return checkout(request)


@login_required
@require_POST
def empty_cart(request: HttpRequest) -> HttpResponse:
    # ... (クリア処理はそのまま) ...
    clear_cart(request.session)
    request.session["cart"] = {}
    request.session.modified = True
    messages.success(request, "カートを空にしました。")

    if request.headers.get("HX-Request"):
        # 1. メッセージ (これが hx-target="#messages-container" に入る)
        msg_html = render_to_string("shop/partials/messages.html", request=request)

        # 2. バッジ更新 (OOB)
        cart_badge = '<span id="cart-count" class="badge" hx-swap-oob="true">0</span>'

        # 3. カートエリア更新 (OOB)
        cart_area_html = ""
        referer = request.META.get("HTTP_REFERER", "")
        if "checkout" in referer:
            context = {"cart_items": [], "total_price": 0, "cart_count": 0}
            content = render_to_string("shop/partials/cart_details.html", context, request=request)
            cart_area_html = content.replace('id="cart-area"', 'id="cart-area" hx-swap-oob="true"')

        # 🛡️ まとめて返却
        return HttpResponse(f"{msg_html}\n{cart_badge}\n{cart_area_html}")

    return redirect("shop:checkout")


@login_required
def order_history(request: HttpRequest) -> HttpResponse:
    """注文履歴を表示"""
    user = cast(User, request.user)
    orders = Order.objects.filter(user=user).prefetch_related("items__product").order_by("-created_at")
    return render(request, "shop/order_history.html", {"orders": orders})


def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    """商品詳細を表示"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart_count = get_cart_count(request.session)
    return render(request, "shop/product_detail.html", {"product": product, "cart_count": cart_count})


def load_image(request: HttpRequest) -> HttpResponse:
    """外部画像の読み込み（HTMX遅延読み込み用）：XSS対策済み"""
    image_url = request.GET.get("image_url", "")
    if not image_url:
        return HttpResponse("")

    return HttpResponse(
        format_html(
            '<img src="{}" style="max-width: 100%; height: auto; border-radius: 4px;"'
            " onerror=\"this.src='/static/img/no-image.png'\">",
            image_url,
        )
    )
