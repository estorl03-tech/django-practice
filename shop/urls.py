from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    # 商品一覧
    path("", views.product_list, name="product_list"),
    # カート追加（product_id を受け取る）
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    # チェックアウト
    path("checkout/", views.checkout, name="checkout"),
    # 【重要】カートを空にするパス
    path("cart/empty/", views.empty_cart, name="empty_cart"),
]
