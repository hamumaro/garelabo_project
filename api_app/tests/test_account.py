from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterViewTests(TestCase):
    def test_register_page_get_ok(self):
        """新規登録画面が表示できる（GETで200）"""
        res = self.client.get(reverse("register"))
        self.assertEqual(res.status_code, 200)

    def test_register_fail_when_required_missing(self):
        """必須項目未入力なら登録できず、画面に留まる"""
        res = self.client.post(reverse("register"), data={}, follow=False)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(User.objects.count(), 0)

    def test_register_success_creates_user(self):
        """正しい入力でユーザーが作成される"""
        data = {
            "email": "new@example.com",
            "nickname": "テストユーザー",
            "password": "Pass12345!",
            "password_confirm": "Pass12345!",
        }

        res = self.client.post(reverse("register"), data=data, follow=False)

        self.assertTrue(
            User.objects.filter(email="new@example.com").exists()
        )
        self.assertIn(res.status_code, [200, 302])


class AccountValidationTests(TestCase):
    def test_register_fail_when_password_mismatch(self):
        """パスワード不一致なら登録できない"""
        data = {
            "email": "new@example.com",
            "nickname": "テストユーザー",
            "password": "Pass12345!",
            "password_confirm": "DIFF12345!",
        }

        res = self.client.post(reverse("register"), data=data, follow=False)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(
            User.objects.filter(email="new@example.com").exists()
        )

    def test_register_fail_when_email_duplicate(self):
        """同一メールアドレスは登録できない"""
        User.objects.create_user(
            email="dup@example.com",
            password="Pass12345!",
            nickname="既存ユーザー"
        )

        data = {
            "email": "dup@example.com",
            "nickname": "テストユーザー",
            "password": "Pass12345!",
            "password_confirm": "Pass12345!",
        }

        res = self.client.post(reverse("register"), data=data, follow=False)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            User.objects.filter(email="dup@example.com").count(),
            1
        )


class EmailVerificationFlowTests(TestCase):
    def test_unverified_user_can_login_current_spec(self):
        """現状仕様：認証未完了ユーザーでもログイン可能"""
        User.objects.create_user(
            email="v@example.com",
            password="Pass12345!",
            nickname="未認証ユーザー"
        )

        res = self.client.post(
            reverse("login"),
            data={
                "username": "v@example.com",
                "password": "Pass12345!"
            },
            follow=False,
        )

        self.assertEqual(res.status_code, 302)
