from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from .models import Product


class ProductModelTest(TestCase):
    def setUp(self):
        """
        🧩 ベストプラクティス: 正常系データのセットアップ
        各テスト実行前にクリーンな状態でDBに作成されます。
        """
        self.valid_data = {
            "name": "テスト商品",
            "description": "これはテスト用の説明文です。",
            "price": Decimal("1000"),  # decimal_places=0 に合わせ整数
            "stock": 10,
        }
        self.product = Product.objects.create(**self.valid_data)

    def test_str_method(self):
        """🔍 コード規約: 視認性のための文字列表現（__str__）の確認"""
        self.assertEqual(str(self.product), self.product.name)

    def test_validation_constraints(self):
        """
        🧪 品質保証: 異常系・境界値バリデーションの網羅
        """
        invalid_cases = [
            # 1. 負の値（重要ロジック・バリデーション）
            {"name": "負の価格", "price": Decimal("-1"), "stock": 10},
            {"name": "負の在庫", "price": Decimal("100"), "stock": -1},
            # 2. 空文字・None（DB整合性・バリデーションレベル）
            {"name": "", "price": Decimal("100"), "stock": 1},
            {"name": None, "price": Decimal("100"), "stock": 1},
            # 3. 桁数あふれ (max_digits=10, decimal_places=0)
            # 11桁以上はNG
            {"name": "価格過大", "price": Decimal("10000000000"), "stock": 1},
            # 4. 最大文字数超過 (max_length=200)
            {"name": "a" * 201, "price": Decimal("100"), "stock": 1},
        ]

        for case in invalid_cases:
            with self.subTest(case=case.get("name", "Unnamed Case")):
                product = Product(**case)
                with self.assertRaises(ValidationError):
                    product.full_clean()

    def test_price_arithmetic_precision(self):
        """🧭 重要ロジック: 整数演算の保証（円単位の想定）"""
        total = self.product.price * 3
        self.assertEqual(total, Decimal("3000"))
        self.assertIsInstance(total, Decimal)

    def test_price_max_boundary(self):
        """🧭 アーキテクチャ原則: max_digits=10 の許容限界（9,999,999,999）"""
        self.product.price = Decimal("9999999999")
        try:
            self.product.full_clean()
        except ValidationError:
            self.fail("Price 9,999,999,999 should be allowed within max_digits=10.")

    def test_stock_edge_case_zero(self):
        """🧪 品質保証: 在庫 0（境界値）が正常に許容されるか"""
        self.product.stock = 0
        # 他の項目でバリデーションエラーが出ないように再セット
        self.product.price = Decimal("1000")
        try:
            self.product.full_clean()
        except ValidationError as e:
            self.fail(f"Stock 0 should be allowed. Error: {e}")

    def test_database_integrity(self):
        """🧭 アーキテクチャ原則: DBレベルでの非NULL制約の確認"""
        with self.assertRaises(IntegrityError):
            # full_cleanを介さず直接保存しようとした際にDBレベルで弾かれるか
            Product.objects.create(name=None, price=100, stock=10)

    def test_auto_timestamp_update(self):
        """🧭 アーキテクチャ原則: システムによるcreated_at/updated_atの自動更新"""
        old_updated_at = self.product.updated_at
        self.product.name = "名前を変更しました"
        self.product.save()

        self.assertNotEqual(self.product.updated_at, old_updated_at)
        self.assertIsNotNone(self.product.created_at)

    def test_default_values(self):
        """🧩 ベストプラクティス: モデル定義のデフォルト値（is_active=True）の保証"""
        # available を is_active に修正 [cite: 2026-02-21]
        self.assertTrue(self.product.is_active)
