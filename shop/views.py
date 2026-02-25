from dataclasses import dataclass
from decimal import Decimal  # Decimal の追加 [cite: 2026-02-21]

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product
from .services import add_item_to_cart, clear_cart, get_cart_count


@dataclass
class CartItem:
    """カート内の各商品を扱うための型定義 [cite: 2026-02-21]"""

    product: Product
    quantity: int


@login_required
def product_list(request: HttpRequest) -> HttpResponse:
    """商品一覧を表示 [cite: 2026-02-21]"""
    products = Product.objects.filter(is_active=True)
    cart_count = get_cart_count(request.session)
    return render(
        request,
        "shop/product_list.html",
        {"products": products, "cart_count": cart_count},
    )


@login_required
def add_to_cart(request: HttpRequest, product_id: int) -> HttpResponse:
    """カートに追加（htmx対応） [cite: 2026-02-21]"""
    get_object_or_404(Product, id=product_id)
    total_quantity = add_item_to_cart(request.session, product_id)

    if request.headers.get("HX-Request"):
        return render(
            request, "shop/partials/cart_counter.html", {"cart_count": total_quantity}
        )

    # 【修正】ifの外側にも return を配置し、mypyエラーを解消 [cite: 2026-02-21]
    return redirect("shop:product_list")


@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """チェックアウト・注文確定 [cite: 2026-02-21]"""
    assert isinstance(request.user, User)

    cart: dict[str, int] = request.session.get("cart", {})
    cart_items: list[CartItem] = []

    # 【修正】0 ではなく Decimal で初期化して型エラーを解消 [cite: 2026-02-21]
    total_price = Decimal("0")

    for product_id_str, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append(CartItem(product=product, quantity=quantity))

    if request.method == "POST":
        if cart_items:
            from .services import create_order

            create_order(request.user, cart_items)

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


@login_required
def empty_cart(request: HttpRequest) -> HttpResponse:
    """
    カートを空にする
    - urls.py の attr-defined エラーを解消するために確実に定義 [cite: 2026-02-21]
    """
    clear_cart(request.session)
    return redirect("shop:product_list")
