from django.contrib import admin

from .models import Order, OrderItem, Product


# 商品管理の設定
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # 一覧画面に表示する項目
    list_display = ["name", "price", "stock", "is_active", "created_at"]
    # 右側のフィルター機能
    list_filter = ["is_active", "created_at"]
    # 一覧画面でそのまま編集できる項目
    list_editable = ["price", "stock", "is_active"]
    # 検索窓の対象
    search_fields = ["name"]


# 注文詳細を注文画面に埋め込むための設定 (Inline)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # デフォルトの空行を0にする
    readonly_fields = [
        "product",
        "quantity",
        "price",
    ]  # 注文後の書き換え防止（読み取り専用）


# 注文管理の設定
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "created_at", "status"]
    list_filter = ["status", "created_at"]
    # 注文画面の下部に明細を表示
    inlines = [OrderItemInline]


# OrderItem単体での登録は不要（Order内で管理するため）
