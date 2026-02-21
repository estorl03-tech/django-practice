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
            "price": Decimal("1000.00"),
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
            {"name": "負の価格", "price": Decimal("-0.01"), "stock": 10},
            {"name": "負の在庫", "price": Decimal("100.00"), "stock": -1},
            # 2. 空文字・None（DB整合性・バリデーションレベル）
            {"name": "", "price": Decimal("100.00"), "stock": 1},
            {"name": None, "price": Decimal("100.00"), "stock": 1},
            # 3. 桁数あふれ (max_digits=10, decimal_places=2)
            # 整数部が8桁、小数部が2桁。1億（9桁）はNG
            {"name": "価格過大", "price": Decimal("100000000.00"), "stock": 1},
            # 4. 最大文字数超過 (max_length=200)
            {"name": "a" * 201, "price": Decimal("100.00"), "stock": 1},
        ]

        for case in invalid_cases:
            with self.subTest(case=case.get("name", "Unnamed Case")):
                product = Product(**case)
                # Djangoレベルのバリデーションを強制実行
                with self.assertRaises(ValidationError):
                    product.full_clean()

    def test_price_precision(self):
        """🧩 ベストプラクティス: 通貨精度のバリデーション（小数点3位以下はNG）"""
        self.product.price = Decimal("10.555")
        with self.assertRaises(ValidationError):
            self.product.full_clean()

    def test_price_arithmetic_precision(self):
        """🧭 重要ロジック: 演算による浮動小数点誤差が発生しないか（Decimalの保証）"""
        # 1000.00円の商品を3個買った時、正確に 3000.00円になるか
        total = self.product.price * 3
        self.assertEqual(total, Decimal("3000.00"))
        self.assertIsInstance(total, Decimal)

    def test_price_max_boundary(self):
        """🧭 アーキテクチャ原則: max_digits=10 の許容限界（99,999,999.99）"""
        self.product.price = Decimal("99999999.99")
        try:
            self.product.full_clean()
        except ValidationError:
            self.fail("Price 99,999,999.99 should be allowed within max_digits=10.")

    def test_stock_edge_case_zero(self):
        """🧪 品質保証: 在庫 0（境界値）が正常に許容されるか"""
        self.product.stock = 0
        try:
            self.product.full_clean()
        except ValidationError:
            self.fail("Stock 0 should be allowed.")

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
        """🧩 ベストプラクティス: モデル定義のデフォルト値（available=True）の保証"""
        self.assertTrue(self.product.available)
