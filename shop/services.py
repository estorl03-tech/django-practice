from typing import Iterable

from .models import Product


def get_active_products() -> Iterable[Product]:
    """
    公開中の商品を更新日の降順で取得するビジネスロジック。
    ※ 将来的に複雑な検索ロジックが必要になった際も、ここを拡張するだけでOK。
    """
    return Product.objects.filter(available=True).order_by("-updated_at")
