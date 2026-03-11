from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    # 商品一覧・詳細
    path("", views.product_list, name="product_list"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    # ギャラリー画像切り替え用 (HTMX用) [cite: 2026-03-09]
    path("load-image/", views.load_image, name="load_image"),
    # カート操作
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/empty/", views.empty_cart, name="empty_cart"),
    # 注文関連
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
]
