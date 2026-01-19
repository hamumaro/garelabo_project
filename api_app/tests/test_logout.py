from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from api_app.models import SavedCustom

User = get_user_model()


class AuthorizationAfterLogoutTests(TestCase):
    def setUp(self):
        self.password = "pass1234"
        self.email = "test@example.com"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

        # ログイン → ログアウト
        self.client.post(
            reverse("login"),
            data={
                "username": self.email,
                "password": self.password
            }
        )
        self.client.get(reverse("logout"))

    def test_cannot_access_save_custom_after_logout(self):
        """ログアウト後、ログイン必須の custom/save にアクセスできない"""
        res = self.client.post(
            reverse("save_custom"),
            data={},
            follow=False
        )

        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("login"), res.url)


class CustomSaveAuthorizationTests(TestCase):
    def test_custom_save_denied_when_not_logged_in(self):
        """未ログインで custom/save を実行すると拒否される"""
        res = self.client.post(
            reverse("save_custom"),
            data={},
            follow=False
        )

        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse("login"), res.url)


class DeleteAuthorizationTests(TestCase):
    def setUp(self):
        self.password = "pass1234"

        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password=self.password
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password=self.password
        )

        # user1 のデータを作成（total_price は NOT NULL）
        self.item = SavedCustom.objects.create(
            user=self.user1,
            total_price=Decimal("0")
        )

    def test_other_user_cannot_delete_item(self):
        """本人以外は削除できない"""
        self.client.post(
            reverse("login"),
            data={
                "username": self.user2.email,
                "password": self.password
            }
        )

        res = self.client.get(
            reverse("delete_item", args=[self.item.id]),
            follow=False
        )

        # 拒否されること（仕様により 302 / 403 / 404）
        self.assertIn(res.status_code, [302, 403, 404])

        # データが消えていないこと
        self.assertTrue(
            SavedCustom.objects.filter(id=self.item.id).exists()
        )

    def test_owner_can_delete_item(self):
        """本人は削除できる"""
        self.client.post(
            reverse("login"),
            data={
                "username": self.user1.email,
                "password": self.password
            }
        )

        res = self.client.get(
            reverse("delete_item", args=[self.item.id]),
            follow=False
        )

        self.assertIn(res.status_code, [200, 302])
        self.assertFalse(
            SavedCustom.objects.filter(id=self.item.id).exists()
        )
