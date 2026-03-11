import threading
from decimal import Decimal
from typing import Any

import pytest
from django.core.exceptions import ValidationError
from django.db import connection

from .models import Order, Product
from .services import create_order

# 🧩 修正: transaction=True を追加
# これにより、別スレッドのDB接続からもテストデータが見えるようになり、実弾テストが可能になります。
pytestmark = pytest.mark.django_db(transaction=True)


class TestProductModel:
    """🧪 品質保証: 商品モデルのバリデーションと整合性テスト"""

    @pytest.fixture
    def product(self) -> Product:
        """正常系データのセットアップ"""
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
    """🧭 重要ロジック: 注文処理と在庫管理の統合テスト"""

    def test_order_creation_reduces_stock(self, admin_user: Any) -> None:
        """🧪 ビジネス価値: 正常な注文で在庫が正しく減算されるか"""
        product = Product.objects.create(name="在庫テスト品", price=Decimal("1000"), stock=10)
        cart_items = [{"product": product, "quantity": 3}]

        order = create_order(admin_user, cart_items, Decimal("3000"))

        product.refresh_from_db()
        assert order.status == "pending"
        assert product.stock == 7

    def test_order_fails_and_rolls_back_with_insufficient_stock(self, admin_user: Any) -> None:
        """🧪 リスク管理: 在庫不足時に注文が失敗し、ロールバックされるか"""
        product = Product.objects.create(name="在庫不足テスト", price=Decimal("1000"), stock=2)
        cart_items = [{"product": product, "quantity": 3}]

        # 1. ValidationError が発生することを確認
        with pytest.raises(ValidationError):
            create_order(admin_user, cart_items, Decimal("3000"))

        # 2. 在庫が減っていないことを確認
        product.refresh_from_db()
        assert product.stock == 2

        # 3. 🚀 追加検証: Orderレコードが作成されていない（ロールバックされている）こと
        assert Order.objects.filter(user=admin_user).count() == 0

    @pytest.mark.skipif(
        connection.vendor == "sqlite", reason="SQLite does not support select_for_update well in threads"
    )
    def test_concurrent_order_for_last_item(self, admin_user: Any) -> None:
        """🧪 セキュリティ対策: 同時注文時に在庫がマイナスにならないか（競合状態のシミュレート）"""
        # transaction=True により、このデータは DB に即時コミットされ、別スレッドから見えます。
        product = Product.objects.create(name="最後の一つ", price=Decimal("100"), stock=1)
        cart_items = [{"product": product, "quantity": 1}]

        results = []

        def place_order():
            # 各スレッドで個別の接続を確保
            from django.db import connections

            try:
                # 実際の並列実行を模倣
                create_order(admin_user, cart_items, Decimal("100"))
                results.append("success")
            except ValidationError:
                results.append("failed")
            finally:
                connections["default"].close()

        # 2つのスレッドで同時に注文を試みる
        t1 = threading.Thread(target=place_order)
        t2 = threading.Thread(target=place_order)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # 検証: 一方は成功し、もう一方は失敗（ValidationError）しているはず
        assert "success" in results
        assert "failed" in results

        product.refresh_from_db()
        assert product.stock == 0  # 在庫は 0 で止まり、-1 にはならない
