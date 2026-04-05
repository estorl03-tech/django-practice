from decimal import Decimal
from typing import TYPE_CHECKING

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    if TYPE_CHECKING:
        id: int

    name = models.CharField(max_length=200, verbose_name="商品名")
    description = models.TextField(blank=True, verbose_name="商品説明")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
        verbose_name="価格",
    )
    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="在庫数")
    is_active = models.BooleanField(default=True, verbose_name="販売可能")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    image = CloudinaryField(
        "商品画像",
        folder="products",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品一覧"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name="price_not_negative"),
            models.CheckConstraint(condition=models.Q(stock__gte=0), name="stock_not_negative"),
        ]

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    """注文モデル: Service層を通じてビジネスロジックを実行"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="購入者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="注文日時")
    status = models.CharField(max_length=20, default="pending", verbose_name="ステータス")
    total_price = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="合計金額")

    class Meta:
        verbose_name = "注文"
        verbose_name_plural = "注文一覧"


class OrderItem(models.Model):
    """注文明細モデル: 購入時の価格を固定保存"""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.PositiveIntegerField(default=1, verbose_name="数量")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="購入時価格")

    class Meta:
        verbose_name = "注文明細"
        verbose_name_plural = "注文明細一覧"

    @property
    def subtotal(self) -> Decimal:
        return Decimal(self.price * self.quantity)

    def __str__(self) -> str:
        return f"{self.product.name} ({self.quantity})"

class ProductImage(models.Model):
    """商品サブ画像モデル"""

    product = models.ForeignKey(
        Product, related_name="additional_images", on_delete=models.CASCADE, verbose_name="商品"
    )
    image = CloudinaryField("サブ画像", folder="products/gallery", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "商品サブ画像"
        verbose_name_plural = "商品サブ画像一覧"
