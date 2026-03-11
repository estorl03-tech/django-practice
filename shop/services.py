from decimal import Decimal
from typing import Any

from django.contrib.auth.models import User
from django.contrib.sessions.backends.base import SessionBase
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, Product

# 🚀 Redundant エラーが出たので、TYPE_CHECKING ブロックごと削除！ [cite: 2026-02-21]


def get_cart_details(
    session: SessionBase,
) -> tuple[list[dict[str, Any]], Decimal, int]:
    """セッションからカート詳細を生成 [cite: 2026-02-21]"""
    cart: dict[str, int] = session.get("cart", {})
    cart_items = []
    total_price = Decimal("0")

    for product_id_str, quantity in cart.items():
        product = get_object_or_404(Product, id=int(product_id_str))
        item_total = product.price * quantity
        total_price += item_total
        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "item_total": item_total,
            }
        )

    cart_count = sum(cart.values())
    return cart_items, total_price, cart_count


def add_item_to_cart(session: SessionBase, product_id: int) -> int:
    """カートに商品を追加し、総数を返す [cite: 2026-02-21]"""
    cart: dict[str, int] = session.get("cart", {})
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1
    session["cart"] = cart
    return sum(cart.values())


def get_cart_count(session: dict[str, Any]) -> int:
    """現在のカート内合計個数を取得 [cite: 2026-02-21]"""
    cart: dict[str, int] = session.get("cart", {})
    return sum(cart.values())


def create_order(user: User, cart_items: list[dict[str, Any]], total_price: Decimal) -> Order:
    """注文作成: トランザクション・行ロック・Fクエリで整合性を保証 [cite: 2026-02-21]"""
    with transaction.atomic():
        # 🚀 cast 無しで Order が返ることが認識されています [cite: 2026-02-21]
        order = Order.objects.create(user=user, status="pending", total_price=total_price)

        for item in cart_items:
            # 🚀 ここも cast 無しで Product として扱えます [cite: 2026-02-21]
            product_in_cart = item["product"]
            product = Product.objects.select_for_update().get(id=product_in_cart.id)
            quantity = int(item["quantity"])

            if product.stock < quantity:
                raise ValidationError(f"{product.name} の在庫が不足しています（残り: {product.stock}）")

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            product.stock = F("stock") - quantity
            product.save(update_fields=["stock"])
            product.refresh_from_db()

        return order  # 🚀 cast 削除！ [cite: 2026-02-21]


def clear_cart(session: SessionBase) -> None:
    """カートを完全に空にする [cite: 2026-02-21]"""
    if "cart" in session:
        session["cart"] = {}
        session.modified = True
