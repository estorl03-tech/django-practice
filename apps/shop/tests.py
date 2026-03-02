from decimal import Decimal
from typing import Any

import pytest
from django.core.exceptions import ValidationError

from .models import Product
from .services import create_order

# 🧩 pytest-django を使用するためのマーク（DB接続を許可）
pytestmark = pytest.mark.django_db


class TestProductModel:
    """🧪 品質保証: 商品モデルのバリデーションと整合性テスト"""

    @pytest.fixture
    def product(self) -> Product:
        """正常系データのセットアップ"""
        return Product.objects.create(
            name="テスト商品", description="テスト説明", price=Decimal("1000"), stock=10
        )

    def test_str_method(self, product: Product) -> None:
        assert str(product) == product.name

    def test_validation_constraints(self) -> None:
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
        # 1. 準備
        product = Product.objects.create(
            name="在庫テスト品", price=Decimal("1000"), stock=10
        )
        # 🚀 修正: services.py の item["product"] というアクセス方法に合わせる
        cart_items = [{"product": product, "quantity": 3}]

        # 2. 実行
        order = create_order(admin_user, cart_items, Decimal("3000"))

        # 3. 検証
        product.refresh_from_db()
        assert order.status == "pending"
        assert product.stock == 7

    def test_order_fails_with_insufficient_stock(self, admin_user: Any) -> None:
        """🧪 リスク管理: 在庫不足時に注文が失敗し、在庫が保護されるか"""
        # 1. 準備
        product = Product.objects.create(
            name="在庫不足テスト", price=Decimal("1000"), stock=2
        )
        # 🚀 修正: services.py に合わせて辞書にする
        cart_items = [{"product": product, "quantity": 3}]

        # 2. 実行 & 検証
        with pytest.raises(ValidationError):
            create_order(admin_user, cart_items, Decimal("3000"))

        # 3. 事実確認
        product.refresh_from_db()
        assert product.stock == 2
