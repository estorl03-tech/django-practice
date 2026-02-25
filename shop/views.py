from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product
from .services import add_item_to_cart, clear_cart, get_cart_count


@login_required
def product_list(request: HttpRequest) -> HttpResponse:
    """
    商品一覧
    - パフォーマンス対策: select_related/prefetch_related を必要に応じて追記
    - is_active な商品のみを表示
    """
    # 将来的に Category などが増えたら .select_related('category') を追加
    products = Product.objects.filter(is_active=True)
    cart_count = get_cart_count(request.session)
    return render(
        request,
        "shop/product_list.html",
        {"products": products, "cart_count": cart_count},
    )


@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    カートに追加（htmx対応）
    - request.session を Service層に渡し、最新の合計個数を受け取る [cite: 2026-02-21]
    """
    # 存在確認（念のため。なくても動作はしますが丁寧な実装です）
    get_object_or_404(Product, id=product_id)

    # 【ここを修正】Service層に session と product_id を渡して、
    # 最新の合計数を受け取る [cite: 2026-02-21]
    total_quantity = add_item_to_cart(request.session, product_id)

    # htmx リクエスト（部分更新）の判定
    if request.headers.get("HX-Request"):
        # 【ここを修正】テンプレートに最新の個数を渡して返す [cite: 2026-02-21]
        return render(
            request, "shop/partials/cart_counter.html", {"cart_count": total_quantity}
        )

    # 通常リクエストの場合は一覧へリダイレクト
    return redirect("shop:product_list")


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """
    チェックアウト・注文確定
    """
    assert isinstance(request.user, User)

    cart = request.session.get("cart", {})
    cart_items = []
    total_price = 0

    # セッション内の商品ID（文字列）を元にDBから商品情報を取得
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id))
        item_total = product.price * quantity
        total_price += item_total
        # create_order に渡すための簡易的なオブジェクト構造を作る
        cart_items.append(type("Item", (), {"product": product, "quantity": quantity}))

    if request.method == "POST":
        if cart_items:
            from .services import create_order

            # DBに注文を保存（トランザクション処理）
            create_order(request.user, cart_items)

        # 注文完了後はセッションをクリアする
        request.session["cart"] = {}
        return render(request, "shop/complete.html")

    display_items = [
        {
            "product": i.product,
            "quantity": i.quantity,
            "item_total": i.product.price * i.quantity,
        }
        for i in cart_items
    ]

    return render(
        request,
        "shop/checkout.html",
        {
            "cart_items": display_items,
            "total_price": total_price,
        },
    )


# shop/views.py


@login_required
def empty_cart(request: HttpRequest) -> HttpResponse:
    """カートを空にするビュー"""
    # 先ほど service.py に作った（または作る）関数を呼ぶ
    clear_cart(request.session)
    # カートを空にした後は、商品一覧ページに戻す
    return redirect("shop:product_list")
