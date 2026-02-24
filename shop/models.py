from django.core.validators import MinValueValidator  # 1. これが必要
from django.db import models


class Product(models.Model):
    # 2. blank=False (デフォルト) で空文字を禁止
    name = models.CharField(max_length=200, verbose_name="商品名")

    description = models.TextField(blank=True, verbose_name="商品説明")

    # 3. 小数点2位まで、負の値は禁止
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],  # 負数を弾く
        verbose_name="価格",
    )

    # 負の在庫は禁止
    stock = models.IntegerField(
        validators=[MinValueValidator(0)],  # 負数を弾く
        verbose_name="在庫数",
    )

    available = models.BooleanField(default=True, verbose_name="販売可能")

    # auto_now_add / auto_now でタイムスタンプテストをパス
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品一覧"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # 「-> str」を追加
        return self.name
