from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    # 商品一覧
    path("", views.product_list, name="product_list"),
    # カート追加（htmxから呼ばれる想定）
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    # 注文・完了画面
    path("checkout/", views.checkout, name="checkout"),
    path("empty/", views.empty_cart, name="empty_cart"),
]
