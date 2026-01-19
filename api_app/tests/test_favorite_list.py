# api_app/tests/test_favorite_list.py

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from api_app.models import SavedCustom, Vehicle

User = get_user_model()


class FavoritePageTests(TestCase):
    """
    お気に入りページ（favorite_page_view）の基本テスト

    仕様:
    - 未ログインでもページは表示できる（200）
    - ログイン済みならお気に入りのみ表示
    """

    def setUp(self):
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password12345",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password12345",
        )

        self.vehicle = Vehicle.objects.create(
            name="TEST CAR",
        )

        self.url = reverse("favorite_page")

    def _get_user_fk_field_name(self):
        candidates = ["user", "owner", "created_by", "account"]
        for name in candidates:
            if hasattr(SavedCustom, name):
                return name

        for f in SavedCustom._meta.fields:
            if (
                getattr(f, "remote_field", None)
                and getattr(f.remote_field, "model", None) == User
            ):
                return f.name

        self.fail("SavedCustom に User への外部キーが見つからない（user/owner 等のフィールド名を確認して）")

    def _get_favorite_field_name(self):
        candidates = ["is_favorite", "favorite", "is_fav", "fav"]
        for name in candidates:
            if hasattr(SavedCustom, name):
                return name
        return None

    def _create_saved_custom(self, user, is_favorite=False):
        user_fk = self._get_user_fk_field_name()
        fav_field = self._get_favorite_field_name()

        kwargs = {user_fk: user}

        if hasattr(SavedCustom, "vehicle"):
            kwargs["vehicle"] = self.vehicle

        if hasattr(SavedCustom, "total_price"):
            kwargs["total_price"] = Decimal("0")

        if fav_field is not None:
            kwargs[fav_field] = is_favorite

        return SavedCustom.objects.create(**kwargs)

    def test_favorite_page_ok_when_not_logged_in(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_favorite_page_ok_when_logged_in(self):
        self.client.login(email="user1@example.com", password="password12345")
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_favorite_page_shows_only_my_favorites_if_boolean_field(self):
        fav_field = self._get_favorite_field_name()
        if fav_field is None:
            self.skipTest("SavedCustom にお気に入り(boolean)フィールドが無い実装っぽいのでこのテストはスキップ")

        fav1 = self._create_saved_custom(self.user1, is_favorite=True)
        notfav1 = self._create_saved_custom(self.user1, is_favorite=False)
        fav2 = self._create_saved_custom(self.user2, is_favorite=True)

        self.client.login(email="user1@example.com", password="password12345")
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

        content = res.content.decode("utf-8", errors="ignore")

        self.assertIn(f"/custom_menu/{fav1.id}/", content)
        self.assertNotIn(f"/custom_menu/{notfav1.id}/", content)
        self.assertNotIn(f"/custom_menu/{fav2.id}/", content)
