from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginViewTests(TestCase):
    def setUp(self):
        self.password = "pass1234"
        self.email = "test@example.com"

        # email必須のカスタムユーザー
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

    def test_login_page_get_ok(self):
        """ログイン画面が表示できる（GETで200）"""
        res = self.client.get(reverse("login"))
        self.assertEqual(res.status_code, 200)

    def test_login_success_redirects(self):
        """正しい情報でログインでき、list_pageへリダイレクトされる"""
        res = self.client.post(
            reverse("login"),
            data={
                "username": self.email,   # フィールド名は username
                "password": self.password
            },
            follow=False
        )

        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("list_page"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_login_fail_stays_on_page(self):
        """誤ったパスワードの場合、ログインできずページに留まる"""
        res = self.client.post(
            reverse("login"),
            data={
                "username": self.email,
                "password": "wrongpass"
            },
            follow=True
        )

        self.assertEqual(res.status_code, 200)
        self.assertFalse("_auth_user_id" in self.client.session)


class LoginAuthAccessTests(TestCase):
    def setUp(self):
        self.password = "pass1234"
        self.email = "test@example.com"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

    def test_favorite_access_without_login_ok(self):
        """未ログインでもお気に入りページにアクセスできる（仕様B）"""
        res = self.client.get(reverse("favorite_page"))
        self.assertEqual(res.status_code, 200)

    def test_favorite_access_with_login_ok(self):
        """ログイン後もお気に入りページにアクセスできる"""
        self.client.post(
            reverse("login"),
            data={
                "username": self.email,
                "password": self.password
            }
        )

        res = self.client.get(reverse("favorite_page"))
        self.assertEqual(res.status_code, 200)
