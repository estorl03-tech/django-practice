from django.urls import path

from . import views

app_name = "shop"  # 名前空間を分離（モジュラモノリスの基本）

urlpatterns = [
    path("", views.product_list, name="product_list"),
]
