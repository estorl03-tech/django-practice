# Create your models here.
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="商品名")
    description = models.TextField(blank=True, verbose_name="商品説明")
    price = models.PositiveIntegerField(verbose_name="価格")
    stock = models.IntegerField(default=0, verbose_name="在庫数")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
