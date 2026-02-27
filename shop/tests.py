from decimal import Decimal
from typing import Any

import pytest
from django.core.exceptions import ValidationError

from .models import Product
from .services import create_order
from .views import CartItem

# 🧩 pytest-django を使用するためのマーク（DB接続を許可）
pytestmark = pytest.mark.django_db


class TestProductModel:
    """
    🧪 品質保証: 商品モデルのバリデーションと整合性テスト [cite: 2026-02-21]
    """

    @pytest.fixture
    def product(self) -> Product:
        """正常系データのセットアップ [cite: 2026-02-21]"""
        return Product.objects.create(
            name="テスト商品", description="テスト説明", price=Decimal("1000"), stock=10
        )

    def test_str_method(self, product: Product) -> None:
        """🔍 コード規約: 文字列表現の確認 [cite: 2026-02-21]"""
        assert str(product) == product.name

    def test_validation_constraints(self) -> None:
        """🧪 品質保証: 異常系バリデーションの網羅 [cite: 2026-02-21]"""
        invalid_cases = [
            {"name": "負の価格", "price": Decimal("-1"), "stock": 10},
            {"name": "負の在庫", "price": Decimal("100"), "stock": -1},
            {"name": "", "price": Decimal("100"), "stock": 1},
        ]
        for case in invalid_cases:
            p = Product(**case)
            with pytest.raises(ValidationError):
                # Djangoモデルのバリデーションを明示的に実行 [cite: 2026-02-21]
                p.full_clean()

    def test_auto_timestamp_update(self, product: Product) -> None:
        """🧭 アーキテクチャ原則: タイムスタンプの自動更新 [cite: 2026-02-21]"""
        old_updated_at = product.updated_at
        product.name = "名前変更"
        product.save()
        assert product.updated_at > old_updated_at


class TestOrderService:
    """
    🧭 重要ロジック: 注文処理と在庫管理の統合テスト [cite: 2026-02-21]
    """

    def test_order_creation_reduces_stock(self, admin_user: Any) -> None:
        """
        🧪 ビジネス価値: 正常な注文で在庫が正しく減算されるか [cite: 2026-02-21]
        """
        # 1. 準備
        product = Product.objects.create(
            name="在庫テスト品", price=Decimal("1000"), stock=10
        )
        cart_items = [CartItem(product=product, quantity=3)]

        # 2. 実行: Service層を通じて注文 [cite: 2026-02-21]
        order = create_order(admin_user, cart_items, Decimal("3000"))

        # 3. 検証: 事実確認 [cite: 2026-02-21]
        product.refresh_from_db()
        assert order.status == "pending"
        assert product.stock == 7  # 10 - 3 = 7

    def test_order_fails_with_insufficient_stock(self, admin_user: Any) -> None:
        """
        🧪 リスク管理: 在庫不足時に注文が失敗し、在庫が保護されるか [cite: 2026-02-21]
        """
        # 1. 準備 (在庫 2 に対して 3 個の注文) [cite: 2026-02-21]
        product = Product.objects.create(
            name="在庫不足テスト", price=Decimal("1000"), stock=2
        )
        cart_items = [CartItem(product=product, quantity=3)]

        # 2. 実行 & 検証: ValidationError が発生することを期待 [cite: 2026-02-21]
        with pytest.raises(ValidationError):
            create_order(admin_user, cart_items, Decimal("3000"))

        # 3. 事実確認: 在庫が減っていないことを確認 [cite: 2026-02-21]
        product.refresh_from_db()
        assert product.stock == 2
