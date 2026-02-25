from typing import TYPE_CHECKING

from django.contrib import admin

from .models import Order, OrderItem, Product

# 実行時のクラッシュを防ぎつつ、mypyに型を認識させるための分岐
if TYPE_CHECKING:
    # mypy用: ジェネリクスとして定義
    ProductAdminBase = admin.ModelAdmin[Product]
    OrderAdminBase = admin.ModelAdmin[Order]
    OrderItemInlineBase = admin.TabularInline[OrderItem, Order]
else:
    # 実行時用: 通常のクラスとして定義
    ProductAdminBase = admin.ModelAdmin
    OrderAdminBase = admin.ModelAdmin
    OrderItemInlineBase = admin.TabularInline


@admin.register(Product)
class ProductAdmin(ProductAdminBase):
    """
    商品管理の設定
    - list_editable により一覧画面からクイック編集が可能
    """

    list_display = ["name", "price", "stock", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    list_editable = ["price", "stock", "is_active"]
    search_fields = ["name"]


class OrderItemInline(OrderItemInlineBase):
    """
    注文詳細を注文編集画面にインライン表示
    - 注文確定後の不慮の書き換えを防ぐため readonly を設定
    """

    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "price"]


@admin.register(Order)
class OrderAdmin(OrderAdminBase):
    """
    注文管理の設定
    - インライン表示により注文内容を一元管理
    """

    list_display = ["id", "user", "created_at", "status"]
    list_filter = ["status", "created_at"]
    inlines = [OrderItemInline]
