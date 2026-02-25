from typing import Any

from django.contrib.auth.models import User
from django.db import transaction

from .models import Order, OrderItem


def add_item_to_cart(session: dict, product_id: int) -> int:
    """
    カートに商品を追加し、現在の合計個数を返す
    - session: request.session を渡す
    - product_id: 追加する商品のID
    """
    # セッションから 'cart' を取得（なければ空の辞書）
    cart = session.get("cart", {})

    # 商品IDを文字列キーとして個数をカウントアップ
    p_id = str(product_id)
    cart[p_id] = cart.get(p_id, 0) + 1

    # セッションを更新
    session["cart"] = cart

    # 全アイテムの合計個数を計算して返す
    return sum(cart.values())


def get_cart_count(session: dict) -> int:
    """現在のカート内の合計個数を取得"""
    cart = session.get("cart", {})
    return sum(cart.values())


def create_order(user: User, cart_items: Any) -> Order:
    """
    注文作成ロジック: トランザクションでデータの整合性を保証
    - transaction.atomic(): 処理の途中でエラーが起きたら全てロールバック
    - ビジネス価値: 購入時の価格を OrderItem に記録（価格変動対策）
    """
    with transaction.atomic():
        # 1. 親となる Order レコードを作成
        order = Order.objects.create(user=user, status="pending")

        # 2. カート内の各アイテムを OrderItem として保存
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                # モデル設計通り、その時点の商品の値段を保存
                price=item.product.price,
            )

        return order


def clear_cart(session: dict) -> None:
    """カートを完全に空にする [cite: 2026-02-21]"""
    if "cart" in session:
        session["cart"] = {}
