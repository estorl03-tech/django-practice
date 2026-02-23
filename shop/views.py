from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .services import get_active_products


def product_list(request: HttpRequest) -> HttpResponse:
    """商品一覧を表示するView (Thin Viewの維持)"""
    products = get_active_products()
    context = {
        "products": products,
    }
    return render(request, "shop/product_list.html", context)
