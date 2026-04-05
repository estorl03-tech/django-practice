from typing import Any

from django.http import HttpRequest

from .services import get_cart_count


def cart_count_processor(request: HttpRequest) -> dict[str, Any]:
    """すべてのテンプレートで cart_count を利用可能にする。"""
    return {"cart_count": get_cart_count(request.session)}
