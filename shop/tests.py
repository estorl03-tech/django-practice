import threading
from decimal import Decimal
from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.db import connection

from .models import Order, Product
from .services import create_order

# 別スレッドの DB 接続からもテストデータを参照できるようにする
pytestmark = pytest.mark.django_db(transaction=True)


class TestProductModel:
    """商品モデルのバリデーションと整合性テスト。"""

    @pytest.fixture
    def product(self) -> Product:
        """正常系データを用意する。"""
        return Product.objects.create(name="テスト商品", description="テスト説明", price=Decimal("1000"), stock=10)

    def test_str_method(self, product: Product) -> None:
        assert str(product) == product.name

    def test_validation_constraints(self) -> None:
        """負の値が許可されないことを Django のバリデーションレベルで確認"""
        p_price = Product(name="負の価格", price=Decimal("-1"), stock=10)
        with pytest.raises(ValidationError):
            p_price.full_clean()

        p_stock = Product(name="負の在庫", price=Decimal("100"), stock=-1)
        with pytest.raises(ValidationError):
            p_stock.full_clean()


class TestOrderService:
    """注文処理と在庫管理の統合テスト。"""

    def test_order_creation_reduces_stock(self, admin_user: Any) -> None:
        """正常な注文で在庫が正しく減算されるかを確認する。"""
        product = Product.objects.create(name="在庫テスト品", price=Decimal("1000"), stock=10)
        cart_items = [{"product": product, "quantity": 3}]

        order = create_order(admin_user, cart_items, Decimal("3000"))

        product.refresh_from_db()
        assert order.status == "pending"
        assert product.stock == 7

    def test_order_fails_and_rolls_back_with_insufficient_stock(self, admin_user: Any) -> None:
        """在庫不足時に注文が失敗し、ロールバックされるかを確認する。"""
        product = Product.objects.create(name="在庫不足テスト", price=Decimal("1000"), stock=2)
        cart_items = [{"product": product, "quantity": 3}]

        with pytest.raises(ValidationError):
            create_order(admin_user, cart_items, Decimal("3000"))

        product.refresh_from_db()
        assert product.stock == 2

        assert Order.objects.filter(user=admin_user).count() == 0

    @pytest.mark.skipif(
        connection.vendor == "sqlite", reason="SQLite does not support select_for_update well in threads"
    )
    def test_concurrent_order_for_last_item(self, admin_user: Any) -> None:
        """同時注文時に在庫がマイナスにならないかを確認する。"""
        product = Product.objects.create(name="最後の一つ", price=Decimal("100"), stock=1)
        cart_items = [{"product": product, "quantity": 1}]

        results = []

        def place_order():
            from django.db import connections

            try:
                create_order(admin_user, cart_items, Decimal("100"))
                results.append("success")
            except ValidationError:
                results.append("failed")
            finally:
                connections["default"].close()

        t1 = threading.Thread(target=place_order)
        t2 = threading.Thread(target=place_order)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert "success" in results
        assert "failed" in results

        product.refresh_from_db()
        assert product.stock == 0
