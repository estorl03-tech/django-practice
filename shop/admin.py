from typing import TYPE_CHECKING

from django.contrib import admin

from .models import Order, OrderItem, Product, ProductImage

# 実行時のクラッシュを防ぎつつ、mypyに型を認識させるための分岐
if TYPE_CHECKING:
    ProductAdminBase = admin.ModelAdmin[Product]
    ProductImageInlineBase = admin.TabularInline[ProductImage, Product]
    OrderAdminBase = admin.ModelAdmin[Order]
    OrderItemInlineBase = admin.TabularInline[OrderItem, Order]
else:
    ProductAdminBase = admin.ModelAdmin
    ProductImageInlineBase = admin.TabularInline
    OrderAdminBase = admin.ModelAdmin
    OrderItemInlineBase = admin.TabularInline


class ProductImageInline(ProductImageInlineBase):
    """
    商品サブ画像を商品編集画面にインライン表示 [cite: 2026-03-09]
    """

    model = ProductImage
    extra = 3  # デフォルトの空枠数
    fields = ("image",)


@admin.register(Product)
class ProductAdmin(ProductAdminBase):
    """
    商品管理の設定
    - list_editable により一覧画面からクイック編集が可能
    - ProductImageInline により複数画像を管理
    """

    list_display = ["id", "name", "price", "stock", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    list_editable = ["price", "stock", "is_active"]
    search_fields = ["name"]
    fields = ("name", "description", "price", "image", "stock", "is_active")

    # 🔽 ここでサブ画像のインラインを登録
    inlines = [ProductImageInline]


class OrderItemInline(OrderItemInlineBase):
    """
    注文詳細を注文編集画面にインライン表示
    """

    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "price"]


@admin.register(Order)
class OrderAdmin(OrderAdminBase):
    """
    注文管理の設定
    """

    list_display = ["id", "user", "created_at", "status"]
    list_filter = ["status", "created_at"]
    inlines = [OrderItemInline]
