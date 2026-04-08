import threading
from decimal import Decimal
from typing import Any

import pytest
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import connection
from django.urls import reverse

from .models import Order, Product
from .services import create_order

# 別スレッドの DB 接続からもテストデータを参照できるようにする
pytestmark = pytest.mark.django_db(transaction=True)


class TestProductModel:
    """商品モデルのバリデーションと整合性テスト。"""

    @pytest.fixture
    def product(self) -> Product:
        """正常系データを用意する。"""
        return Product.objects.create(name="テスト商品", description="テスト説明", price=Decimal("1000"), stock=10)

    def test_str_method(self, product: Product) -> None:
        assert str(product) == product.name

    def test_validation_constraints(self) -> None:
        """負の値が許可されないことを Django のバリデーションレベルで確認"""
        p_price = Product(name="負の価格", price=Decimal("-1"), stock=10)
        with pytest.raises(ValidationError):
            p_price.full_clean()

        p_stock = Product(name="負の在庫", price=Decimal("100"), stock=-1)
        with pytest.raises(ValidationError):
            p_stock.full_clean()


class TestOrderService:
    """注文処理と在庫管理の統合テスト。"""

    def test_order_creation_reduces_stock(self, admin_user: Any) -> None:
        """正常な注文で在庫が正しく減算されるかを確認する。"""
        product = Product.objects.create(name="在庫テスト品", price=Decimal("1000"), stock=10)
        cart_items = [{"product": product, "quantity": 3}]

        order = create_order(admin_user, cart_items, Decimal("3000"))

        product.refresh_from_db()
        assert order.status == "pending"
        assert product.stock == 7

    def test_order_fails_and_rolls_back_with_insufficient_stock(self, admin_user: Any) -> None:
        """在庫不足時に注文が失敗し、ロールバックされるかを確認する。"""
        product = Product.objects.create(name="在庫不足テスト", price=Decimal("1000"), stock=2)
        cart_items = [{"product": product, "quantity": 3}]

        with pytest.raises(ValidationError):
            create_order(admin_user, cart_items, Decimal("3000"))

        product.refresh_from_db()
        assert product.stock == 2

        assert Order.objects.filter(user=admin_user).count() == 0

    @pytest.mark.skipif(
        connection.vendor == "sqlite", reason="SQLite does not support select_for_update well in threads"
    )
    def test_concurrent_order_for_last_item(self, admin_user: Any) -> None:
        """同時注文時に在庫がマイナスにならないかを確認する。"""
        product = Product.objects.create(name="最後の一つ", price=Decimal("100"), stock=1)
        cart_items = [{"product": product, "quantity": 1}]

        results = []

        def place_order():
            from django.db import connections

            try:
                create_order(admin_user, cart_items, Decimal("100"))
                results.append("success")
            except ValidationError:
                results.append("failed")
            finally:
                connections["default"].close()

        t1 = threading.Thread(target=place_order)
        t2 = threading.Thread(target=place_order)

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        assert "success" in results
        assert "failed" in results

        product.refresh_from_db()
        assert product.stock == 0


class TestShopViews:
    """主要画面の表示とアクセス制御を確認する。"""

    @pytest.fixture(autouse=True)
    def clear_cache(self) -> None:
        cache.clear()

    def test_product_list_is_public(self, client: Any) -> None:
        Product.objects.create(name="公開商品", description="一覧表示テスト", price=Decimal("1200"), stock=5)

        response = client.get(reverse("shop:product_list"))

        assert response.status_code == 200
        assert "公開商品" in response.content.decode("utf-8")

    def test_checkout_requires_login(self, client: Any) -> None:
        response = client.get(reverse("shop:checkout"))

        assert response.status_code == 302
        assert reverse("login") in response.url

    def test_order_history_shows_only_logged_in_users_orders(self, client: Any) -> None:
        owner = User.objects.create_user(username="owner", password="pass12345")
        other_user = User.objects.create_user(username="other", password="pass12345")
        owner_order = Order.objects.create(user=owner, status="pending", total_price=Decimal("1500"))
        Order.objects.create(user=other_user, status="pending", total_price=Decimal("2800"))

        logged_in = client.login(username="owner", password="pass12345")
        response = client.get(reverse("shop:order_history"))
        page = response.content.decode("utf-8")

        assert logged_in is True
        assert response.status_code == 200
        assert str(owner_order.total_price) not in page
        assert "1,500" in page or "1500" in page
        assert "2,800" not in page and "2800" not in page

    def test_checkout_post_creates_order_and_clears_cart(self, client: Any) -> None:
        user = User.objects.create_user(username="buyer", password="pass12345")
        product = Product.objects.create(name="購入商品", description="checkout test", price=Decimal("2000"), stock=4)

        client.force_login(user)
        session = client.session
        session["cart"] = {str(product.id): 2}
        session.save()

        response = client.post(reverse("shop:checkout"), {"submit_order": "1"})

        product.refresh_from_db()
        orders = Order.objects.filter(user=user)

        assert response.status_code == 200
        assert orders.count() == 1
        assert orders.first().total_price == Decimal("4000")
        assert product.stock == 2
        assert client.session.get("cart", {}) == {}

    def test_load_image_rejects_non_cloudinary_url(self, client: Any) -> None:
        response = client.get(reverse("shop:load_image"), {"image_url": "https://example.com/image.png"})

        assert response.status_code == 200
        assert response.content == b""

    def test_login_is_rate_limited_after_repeated_failures(self, client: Any) -> None:
        User.objects.create_user(username="locked", password="pass12345")

        for _ in range(5):
            response = client.post(reverse("login"), {"username": "locked", "password": "wrong-password"})
            assert response.status_code == 200

        blocked = client.post(reverse("login"), {"username": "locked", "password": "wrong-password"})

        assert blocked.status_code == 429
        assert "ログイン試行回数が上限に達しました".encode("utf-8") in blocked.content
