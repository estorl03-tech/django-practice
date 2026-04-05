from django.urls import path

from . import views

app_name = "shop"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("load-image/", views.load_image, name="load_image"),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:product_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/empty/", views.empty_cart, name="empty_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
]
