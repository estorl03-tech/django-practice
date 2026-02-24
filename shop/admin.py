from __future__ import annotations  # これを必ず1行目に入れる

from django.contrib import admin

from .models import Product


@admin.register(Product)
# [] を使わず、コメントで型を教える。
# これなら実行時に TypeError にならず、かつ mypy も納得します。
class ProductAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ("name", "price")  # 一覧に表示する項目
