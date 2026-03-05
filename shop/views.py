from typing import Any, Dict, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
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
    """商品一覧を表示 [cite: 2026-02-21]"""
    products = Product.objects.filter(is_active=True)
    cart_count = get_cart_count(request.session)
    return render(
        request,
        "shop/product_list.html",
        {"products": products, "cart_count": cart_count},
    )


@require_POST
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """カートに追加（投入時の在庫チェック付き） [cite: 2026-02-21]"""
    product = get_object_or_404(Product, id=product_id)
    # 型ヒントを明示して Pylance の Unknown を回避
    cart: Dict[str, int] = request.session.get("cart", {})
    current_qty = cart.get(str(product_id), 0)

    # 🛡️ 在庫判定
    if current_qty + 1 > product.stock:
        available_qty = product.stock - current_qty
        messages.error(
            request,
            f"{product.name} の在庫が不足しています（残り: {available_qty}個）",
        )
        if request.headers.get("HX-Request"):
            current_total = get_cart_count(request.session)
            msg_html = render_to_string("shop/partials/messages.html", request=request)
            cart_html = (
                f'<span id="cart-count" hx-swap-oob="true">{current_total}</span>'
            )
            return HttpResponse(msg_html + cart_html)
        return redirect("shop:product_list")

    # 正常な追加処理
    total_quantity = add_item_to_cart(request.session, product_id)
    messages.success(request, f"{product.name} をカートに追加しました。")

    if request.headers.get("HX-Request"):
        msg_html = render_to_string("shop/partials/messages.html", request=request)
        cart_html = f'<span id="cart-count" hx-swap-oob="true">{total_quantity}</span>'
        return HttpResponse(msg_html + cart_html)

    return redirect("shop:product_list")


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """チェックアウト・注文確定 (Thin View) [cite: 2026-02-21]"""
    # User 型であることを Pylance に確信させる
    user = cast(User, request.user)

    # 1. サービス層からデータを取得
    cart_items, total_price, cart_count = get_cart_details(request.session)

    # 2. 注文確定処理
    if request.method == "POST" and "submit_order" in request.POST and cart_items:
        try:
            create_order(user, cart_items, total_price)
            request.session["cart"] = {}
            request.session.modified = True
            messages.success(request, "注文が完了しました！")

            if request.headers.get("HX-Request"):
                msg_html = render_to_string(
                    "shop/partials/messages.html", request=request
                )
                cart_zero_html = '<span id="cart-count" hx-swap-oob="true">0</span>'
                complete_html = (
                    "<h2>ご注文ありがとうございました！</h2>"
                    "<p>注文処理が完了しました。</p>"
                    "<a href='/' class='outline'>トップページへ戻る</a>"
                )
                return HttpResponse(complete_html + msg_html + cart_zero_html)

            return render(request, "shop/complete.html")
        except ValidationError as e:
            msg = e.messages[0] if hasattr(e, "messages") else str(e)
            messages.error(request, msg)

    # 3. レンダリング用コンテキスト
    context: Dict[str, Any] = {
        "cart_items": cart_items,
        "total_price": total_price,
        "cart_count": cart_count,
    }

    if request.headers.get("HX-Request"):
        table_html = render_to_string(
            "shop/partials/cart_details.html", context, request=request
        )
        msg_html = render_to_string("shop/partials/messages.html", request=request)
        cart_count_html = (
            f'<span id="cart-count" hx-swap-oob="true">{cart_count}</span>'
        )
        return HttpResponse(table_html + msg_html + cart_count_html)

    return render(request, "shop/checkout.html", context)


@require_POST
def update_cart_item(request: HttpRequest, product_id: int) -> HttpResponse:
    """カート内数量を操作し、結果を返す [cite: 2026-02-21]"""
    cart: Dict[str, int] = request.session.get("cart", {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        action = request.POST.get("action")
        try:
            product = get_object_or_404(Product, id=product_id)
            if action == "add":
                if product.stock <= cart[product_id_str]:
                    raise ValidationError(
                        f"{product.name}の在庫が足りません（残り: {product.stock}個）"
                    )
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
def order_history(request: HttpRequest) -> HttpResponse:
    """注文履歴を表示"""
    user = cast(User, request.user)
    orders = (
        Order.objects.filter(user=user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
def empty_cart(request: HttpRequest) -> HttpResponse:
    """カートを空にする"""
    clear_cart(request.session)
    return redirect("shop:product_list")
