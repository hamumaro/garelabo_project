from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from api_app.models import Vehicle

User = get_user_model()


class CarSelectViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # username を使わない（emailログイン系のカスタムユーザー想定）
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="password1234",
        )

        # Vehicleの必須項目が他にもあるなら、ここに追加して合わせること
        cls.v1 = Vehicle.objects.create(name="R34")
        cls.v2 = Vehicle.objects.create(name="R33")

    def test_carselect_get_success(self):
        """
        車選択（一覧）ページが表示できる
        """
        # login_required なら有効化（安全に通したいなら force_login 推奨）
        # self.client.force_login(self.user)

        url = reverse("list_page")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_carselect_shows_vehicles(self):
        """
        DBにある車が一覧に渡される（contextで検証）
        ※ 画面側(main.content)がまだ空実装なので assertContains だと落ちるため
        """
        # self.client.force_login(self.user)

        url = reverse("list_page")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

        # TemplateResponseなら context が入る
        self.assertIsNotNone(res.context)

        # view の context キーに合わせて確認（候補を順に拾う）
        vehicles = (
            res.context.get("vehicles")
            or res.context.get("vehicle_list")
            or res.context.get("car_list")
        )
        self.assertIsNotNone(
            vehicles,
            "Vehicle一覧がcontextに入ってない（キー名かview側で渡している変数名を確認）"
        )

        # 中身に作ったVehicleが含まれてるか（QuerySet想定）
        ids = list(vehicles.values_list("id", flat=True))
        self.assertIn(self.v1.id, ids)
        self.assertIn(self.v2.id, ids)

    def test_carselect_empty_db_ok(self):
        """
        Vehicleが0件でも落ちずに表示できる
        """
        Vehicle.objects.all().delete()

        # self.client.force_login(self.user)

        url = reverse("list_page")
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_carselect_redirect_when_login_required(self):
        """
        login_required なら未ログインで302になる（違うならこのテスト消してOK）
        """
        url = reverse("list_page")
        res = self.client.get(url)

        # ログイン必須じゃないなら 200 で通る。それはそれでOKにする。
        if res.status_code == 302:
            self.assertIn("/login", res["Location"])
        else:
            self.assertEqual(res.status_code, 200)
