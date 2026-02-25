from typing import Any

from django.contrib.auth.models import User
from django.db import transaction

from .models import Order, OrderItem


def add_item_to_cart(session: dict[str, Any], product_id: int) -> int:
    """カートに商品を追加し、合計個数を返す [cite: 2026-02-21]"""
    cart: dict[str, int] = session.get("cart", {})

    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    session["cart"] = cart

    return sum(cart.values())


def get_cart_count(session: dict[str, Any]) -> int:
    """現在の合計個数を取得 [cite: 2026-02-21]"""
    cart: dict[str, int] = session.get("cart", {})
    return sum(cart.values())


def create_order(user: User, cart_items: Any) -> Order:
    """注文作成ロジック: トランザクションでデータの整合性を保証 [cite: 2026-02-21]"""
    with transaction.atomic():
        order = Order.objects.create(user=user, status="pending")

        for item in cart_items:
            # mypyに属性の存在を確信させる [cite: 2026-02-21]
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        return order


def clear_cart(session: dict[str, Any]) -> None:
    """カートを完全に空にする [cite: 2026-02-21]"""
    if "cart" in session:
        session["cart"] = {}
