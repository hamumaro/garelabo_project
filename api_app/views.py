from decimal import Decimal

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction

import random

from .forms import LoginForm, RegisterForm, VerificationForm
from .models import SavedCustom, Vehicle, Wheel, Aero, Bumper, Color, Light

User = get_user_model()


# 動作確認用
def test_view(request):
    return HttpResponse("API is working!")


# ログイン処理
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("list_page")
        else:
            print("--------------------------------------------------")
            print("ログインエラー:", form.errors)
            print("送信されたデータ:", request.POST)
            print("--------------------------------------------------")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


# 一覧ページ表示
def list_page_view(request):
    if request.user.is_authenticated:
        custom_items = SavedCustom.objects.filter(user=request.user).order_by("-saved_at")
    else:
        custom_items = []

    return render(request, "List.html", {
        "custom_items": custom_items,
        "user": request.user,
    })


# お気に入りページ表示

def favorite_page_view(request):
    if request.user.is_authenticated:
        custom_items = SavedCustom.objects.filter(
            user=request.user,
            is_favorite=True
        ).order_by("-saved_at")
    else:
        custom_items = []

    return render(request, "Favorite_List.html", {
        "custom_items": custom_items
    })


# 新規登録ページ表示（メール認証コード送信）
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    code = str(random.randint(100000, 999999))
                    request.session["verification_code"] = code
                    request.session["verification_user_id"] = user.id

                    subject = "【GARELABO+】認証コードのお知らせ"
                    message = f"以下の認証コードを入力して登録を完了してください。\n\n認証コード: {code}"
                    from_email = "no-reply@garelabo.com"
                    recipient_list = [user.email]

                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                # NOTE:
                # urls.py にこれを追加してないと NoReverseMatch になる
                # path('verify/', views.verify_code_view, name='verify'),
                return redirect("verify")

            except Exception as e:
                print(f"メール送信エラー: {e}")
                form.add_error(None, "メール送信に失敗しました。")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# 認証コード入力画面（register_view が redirect("verify") する先）
def verify_code_view(request):
    user_id = request.session.get("verification_user_id")
    if not user_id:
        return redirect("register")

    form = VerificationForm()
    message = None

    if request.method == "POST":
        # キャンセル
        if "cancelAuthbtn" in request.POST:
            request.session.pop("verification_code", None)
            request.session.pop("verification_user_id", None)
            return redirect("register")

        # 再送信
        if "resendCodebtn" in request.POST:
            code = str(random.randint(100000, 999999))
            request.session["verification_code"] = code
            user = User.objects.get(id=user_id)
            try:
                send_mail(
                    "【GARELABO+】認証コードのお知らせ（再送信）",
                    f"認証コード: {code}",
                    "no-reply@garelabo.com",
                    [user.email]
                )
            except Exception as e:
                print(f"メール送信エラー: {e}")

            message = "コードを再送信しました。"
            return render(request, "verify_code.html", {"form": form, "message": message})

        # 確認
        form = VerificationForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data["authCode"]
            session_code = request.session.get("verification_code")

            if input_code == session_code:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()

                login(request, user)

                request.session.pop("verification_code", None)
                request.session.pop("verification_user_id", None)

                return redirect("list_page")
            else:
                form.add_error("authCode", "認証コードが間違っています。")
                form.fields["authCode"].widget.attrs.update({
                    "class": "verification-input error-input",
                    "placeholder": "再入力してください。",
                    "value": ""
                })

    return render(request, "verify_code.html", {"form": form, "message": message})


# アカウント表示
@login_required(login_url="/login/")
def account_view(request):
    user = request.user
    return render(request, "account.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": ""
    })


# アカウント情報更新表示
@login_required(login_url="/login/")
def account_update_view(request):
    user = request.user
    return render(request, "account_update.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": ""
    })


# アカウント情報保存処理
@login_required(login_url="/login/")
def account_save_view(request):
    if request.method == "POST":
        user = request.user
        nickname = request.POST.get("nickname")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user.nickname = nickname
        user.email = email
        if password and password.strip() != "":
            user.set_password(password)

        user.save()
        update_session_auth_hash(request, user)

        return redirect("account")

    return redirect("account_update")


# 削除機能
@login_required(login_url="/login/")
def delete_item(request, item_id):
    item = get_object_or_404(SavedCustom, id=item_id, user=request.user)
    item.delete()
    return redirect("list_page")


# カスタムメニュー（新規 / 既存編集）
def custom_menu(request, custom_id=None):
    # 編集モード
    if custom_id:
        saved_item = get_object_or_404(SavedCustom, pk=custom_id, user=request.user)
        request.session["custom_data"] = {
            "vehicle_id": saved_item.vehicle.id if saved_item.vehicle else None,
            "color_id": saved_item.color.id if saved_item.color else None,
            "wheel_id": saved_item.wheel.id if saved_item.wheel else None,
            "bumper_id": saved_item.bumper.id if saved_item.bumper else None,
            "light_id": saved_item.light.id if saved_item.light else None,
            "aero_id": saved_item.aero.id if saved_item.aero else None,
        }

    # 新規作成（車種選択から来る想定：?car_id=）
    elif request.GET.get("car_id"):
        car_id = request.GET.get("car_id")
        vehicle = get_object_or_404(Vehicle, id=car_id)
        request.session["custom_data"] = {
            "vehicle_id": vehicle.id
        }

    custom_data = request.session.get("custom_data", {})
    vehicle_id = custom_data.get("vehicle_id")

    vehicle = None
    if vehicle_id:
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

    # セッション切れ等の保険
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data["vehicle_id"] = vehicle.id
            request.session["custom_data"] = custom_data

    return render(request, "custom_menu.html", {"vehicle": vehicle})


# カスタム中止（確認ページ → POSTで中止確定）
def custom_cancel(request):
    if request.method == "POST":
        request.session.pop("custom_data", None)
        return redirect("list_page")

    return render(request, "custom_cancel.html")


# カラー選択
def custom_menu_bodycolor(request):
    custom_data = request.session.get("custom_data", {})

    vehicle_id = custom_data.get("vehicle_id")
    if not vehicle_id:
        first_vehicle = Vehicle.objects.first()
        if first_vehicle:
            vehicle_id = first_vehicle.id
            custom_data["vehicle_id"] = vehicle_id
            request.session["custom_data"] = custom_data
        else:
            return render(request, "custom_menu_bodycolor.html", {"colors": []})

    colors = Color.objects.filter(vehicle_id=vehicle_id)

    if request.method == "POST":
        selected_id = request.POST.get("color_id")
        if selected_id:
            custom_data["color_id"] = selected_id
            request.session["custom_data"] = custom_data
            return redirect("custom_menu_bodycolor")

    current_color_id = custom_data.get("color_id")

    return render(request, "custom_menu_bodycolor.html", {
        "colors": colors,
        "current_color_id": int(current_color_id) if current_color_id else None,
    })


def custom_menu_wheel(request):
    return render(request, "custom_menu_wheel.html")


def custom_menu_bumper(request):
    return render(request, "custom_menu_bumper.html")


def custom_menu_light(request):
    return render(request, "custom_menu_light.html")


def custom_menu_aeroparts(request):
    return render(request, "custom_menu_aeroparts.html")


def auto_custom(request):
    return render(request, "auto_custom.html")


# 車種選択ページ
def car_select(request):
    vehicles = Vehicle.objects.all().order_by("id")
    return render(request, "car_select.html", {"vehicles": vehicles})


def car_view(request):
    images = [
        "https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x2.jpg",
        "https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x3.jpg",
        "https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_XH32TC_x1.jpg"
    ]
    return render(request, "car.html", {"images": images})


# 見積もり
def estimate_view(request):
    custom_data = request.session.get("custom_data", {})

    vehicle_id = custom_data.get("vehicle_id")
    color_id = custom_data.get("color_id")
    wheel_id = custom_data.get("wheel_id")
    bumper_id = custom_data.get("bumper_id")
    light_id = custom_data.get("light_id")
    aero_id = custom_data.get("aero_id")

    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    color = Color.objects.filter(id=color_id).first()
    wheel = Wheel.objects.filter(id=wheel_id).first()
    bumper = Bumper.objects.filter(id=bumper_id).first()
    light = Light.objects.filter(id=light_id).first()
    aero = Aero.objects.filter(id=aero_id).first()

    total = Decimal("0.00")
    for part in [color, wheel, bumper, light, aero]:
        if part and part.price:
            total += part.price

    return render(request, "estimate.html", {
        "vehicle": vehicle,
        "color": color,
        "wheel": wheel,
        "bumper": bumper,
        "light": light,
        "aero": aero,
        "total_price": total,
    })


# 見積もり保存
@login_required(login_url="/login/")
def save_estimate_view(request):
    if request.method != "POST":
        return redirect("estimate")

    custom_data = request.session.get("custom_data", {})
    if not custom_data:
        return redirect("custom_menu")

    vehicle = Vehicle.objects.filter(id=custom_data.get("vehicle_id")).first()
    color = Color.objects.filter(id=custom_data.get("color_id")).first()
    wheel = Wheel.objects.filter(id=custom_data.get("wheel_id")).first()
    bumper = Bumper.objects.filter(id=custom_data.get("bumper_id")).first()
    light = Light.objects.filter(id=custom_data.get("light_id")).first()
    aero = Aero.objects.filter(id=custom_data.get("aero_id")).first()

    total = Decimal("0.00")
    for part in [color, wheel, bumper, light, aero]:
        if part and part.price:
            total += part.price

    with transaction.atomic():
        SavedCustom.objects.create(
            user=request.user,
            vehicle=vehicle,
            color=color,
            wheel=wheel,
            bumper=bumper,
            light=light,
            aero=aero,
            total_price=total,
            preview_image_url="uploads/previews/default.png",
            display_mode=False,
            is_favorite=False
        )

    return redirect("list_page")


# カスタム保存
@login_required(login_url="/login/")
def custom_save(request):
    if request.method != "POST":
        return redirect("custom_menu")

    custom_data = request.session.get("custom_data", {})
    if not custom_data:
        return redirect("custom_menu")

    vehicle = Vehicle.objects.filter(id=custom_data.get("vehicle_id")).first()
    color = Color.objects.filter(id=custom_data.get("color_id")).first()
    wheel = Wheel.objects.filter(id=custom_data.get("wheel_id")).first()
    bumper = Bumper.objects.filter(id=custom_data.get("bumper_id")).first()
    light = Light.objects.filter(id=custom_data.get("light_id")).first()
    aero = Aero.objects.filter(id=custom_data.get("aero_id")).first()

    total = Decimal("0.00")
    for part in [color, wheel, bumper, light, aero]:
        if part and part.price:
            total += part.price

    SavedCustom.objects.create(
        user=request.user,
        vehicle=vehicle,
        color=color,
        wheel=wheel,
        bumper=bumper,
        light=light,
        aero=aero,
        total_price=total,
        preview_image_url="uploads/previews/default.png",
        display_mode=False,
        is_favorite=False
    )

    return redirect("list_page")


# エラーページ
def menu_error_view(request):
    return render(request, "menu_error.html", status=500)


def surroundings_error_view(request):
    return render(request, "surroundings_error.html", status=500)


def save_custom_content_error_view(request):
    return render(request, "save_custom_content_error.html", status=500)


def list_management_delection_error_view(request):
    return render(request, "list_management_delection_error.html", status=500)
