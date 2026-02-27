from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.core.exceptions import (
    ValidationError,  # 👈 追加: 在庫不足を通知するために必要
)
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


def create_order(user: User, cart_items: Any, total_price: Decimal) -> Order:
    """
    注文作成ロジック: 在庫を減らし、トランザクションで整合性を保証 [cite: 2026-02-21]

    【修正ポイント】: 在庫不足時に ValidationError を発生させ、
    transaction.atomic() によって注文作成自体をロールバックさせます。
    """
    with transaction.atomic():
        # 1. 注文親レコードの作成
        order = Order.objects.create(
            user=user, status="pending", total_price=total_price
        )

        # 2. 明細の作成と在庫の減算 [cite: 2026-02-21]
        for item in cart_items:
            product = item.product

            # 🛡️ 在庫チェックの追加 [cite: 2026-02-21]
            if product.stock < item.quantity:
                raise ValidationError(
                    f"{product.name} の在庫が不足しています（残り: {product.stock}）"
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price,
            )

            # 在庫を減らす
            product.stock -= item.quantity
            # save() 内でバリデーションが走るよう更新
            product.save()

        return order


def clear_cart(session: dict[str, Any]) -> None:
    """カートを完全に空にする [cite: 2026-02-21]"""
    if "cart" in session:
        session["cart"] = {}
