from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction

import random
import json
from django.templatetags.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_POST

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


# ログアウト処理
def logout_view(request):
    logout(request)
    return redirect("list_page")


# 一覧ページ表示
def list_page_view(request, custom_id=None):
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
        ).order_by('-updated_at')
        ).order_by("-saved_at")
    else:
        custom_items = []

    return render(request, "Favorite_List.html", {
        "custom_items": custom_items
    })

# 新規登録ページ表示

# 新規登録（メール認証コード送信）
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

                return redirect("verify")

            except Exception as e:
                print(f"メール送信エラー: {e}")
                form.add_error(None, "メール送信に失敗しました。")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# 認証コード入力画面
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

    return render(request, "verify_code.html", {"form": form, "message": message})


# ダッシュボード（urls.py にあるので最低限用意）
@login_required(login_url="/login/")
def dashboard_view(request):
    return render(request, "dashboard.html", {"user": request.user})


# アカウント表示
@login_required(login_url="/login/")
def account_view(request):
    user = request.user
    return render(request, "account.html", {
        "nickname": getattr(user, "nickname", ""),
        "email": user.email,
        "password": ""
    })


# アカウント情報更新表示
@login_required(login_url="/login/")
def account_update_view(request):
    user = request.user
    return render(request, "account_update.html", {
        "nickname": getattr(user, "nickname", ""),
        "email": user.email,
        "password": ""
    })


# アカウント情報保存処理
@login_required(login_url="/login/")
def account_save_view(request):
    if request.method == "POST":
        user = request.user
        user.nickname = request.POST.get("nickname")
        user.email = request.POST.get("email")

        password = request.POST.get("password")
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
    elif request.GET.get("car_id"):
        car_id = request.GET.get("car_id")
        vehicle = get_object_or_404(Vehicle, id=car_id)
        request.session["custom_data"] = {"vehicle_id": vehicle.id}

    custom_data = request.session.get("custom_data", {})
    vehicle_id = custom_data.get("vehicle_id")

    vehicle = None
    if vehicle_id:
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data["vehicle_id"] = vehicle.id
            request.session["custom_data"] = custom_data

    return render(request, "custom_menu.html", {"vehicle": vehicle})


        request.session["editing_custom_id"] = saved.id
        
        request.session["custom_data"] = {
            "vehicle_id": saved.vehicle.id if saved.vehicle else None,
            "color_id": saved.color.id if saved.color else None,
            "wheel_id": saved.wheel.id if saved.wheel else None,
            "bumper_id": saved.bumper.id if saved.bumper else None,
            "light_id": saved.light.id if saved.light else None,
            "aero_id": saved.aero.id if saved.aero else None,
            "is_favorite": saved.is_favorite,
        }
# カスタム中止
def custom_cancel(request):
    if request.method == "POST":
        request.session.pop("custom_data", None)
        return redirect("list_page")

    return render(request, "custom_cancel.html")


    vehicle = Vehicle.objects.filter(id=vehicle_id).first() or Vehicle.objects.first()

# カラー選択
def custom_menu_bodycolor(request, custom_id=None):
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

    context = {
        'colors': colors,
        'color': color,
        'current_color_id': int(current_color_id) if current_color_id else None,
        'vehicle_id': vehicle_id,
        'vehicle':vehicle,
        'vehicles': vehicles, # ← ここが重要
        'is_favorite': custom_data.get('is_favorite', False),
    }
    return render(request, "custom_menu_bodycolor.html", context)


def custom_menu_wheel(request):
    # セッションから現在のカスタムデータを取得
    custom_data = request.session.get('custom_data', {})
    
    # お気に入り状態を取得（なければFalse）
    is_favorite = custom_data.get('is_favorite', False)

    # ...既存の車両取得ロジックなど...

    context = {
        'is_favorite': is_favorite, # これをテンプレートに渡す
        # ...他のデータ...
    }
    return render(request, "custom_menu_wheel.html", context)
 
def custom_menu_bumper(request):
    # セッションから現在のカスタムデータを取得
    custom_data = request.session.get('custom_data', {})
    
    # お気に入り状態を取得（なければFalse）
    is_favorite = custom_data.get('is_favorite', False)

    # ...既存の車両取得ロジックなど...

    context = {
        'is_favorite': is_favorite, # これをテンプレートに渡す
        # ...他のデータ...
    }
    return render(request, "custom_menu_bumper.html", context)
 
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

    # 2. custom_id が渡された場合、そのデータをセッションに展開する
    if custom_id:
        saved = get_object_or_404(SavedCustom, id=custom_id, user=request.user)
        # セッションをこの保存データの内容で上書き
        custom_data = {
            'vehicle_id': saved.vehicle.id if saved.vehicle else None,
            'color_id': saved.color.id if saved.color else None,
            'wheel_id': saved.wheel.id if saved.wheel else None,
            'bumper_id': saved.bumper.id if saved.bumper else None,
            'light_id': saved.light.id if saved.light else None,
            'aero_id': saved.aero.id if saved.aero else None,
            'is_favorite': saved.is_favorite,
        }
        request.session['custom_data'] = custom_data
        request.session['editing_custom_id'] = saved.id # 編集モードも維持

# 車種選択ページ
def car_select(request):
    vehicles = Vehicle.objects.all().order_by("id")
    return render(request, "car_select.html", {"vehicles": vehicles})

    is_favorite = custom_data.get('is_favorite', False)

    # 3. 車両の特定
    vehicle_id = custom_data.get('vehicle_id')
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    if not vehicle:
        vehicle = Vehicle.objects.first()

    # 4. パーツの取得（セッションにあるIDに基づいて取得）
    color = Color.objects.filter(id=custom_data.get('color_id'), vehicle=vehicle).first()
    wheel = Wheel.objects.filter(id=custom_data.get('wheel_id'), vehicle=vehicle).first()
    bumper = Bumper.objects.filter(id=custom_data.get('bumper_id'), vehicle=vehicle).first()
    light = Light.objects.filter(id=custom_data.get('light_id'), vehicle=vehicle).first()
    aero = Aero.objects.filter(id=custom_data.get('aero_id'), vehicle=vehicle).first()

    # 5. カラーが取れない場合の補正（画像表示エラー防止）
    if not color:
        color = Color.objects.filter(vehicle=vehicle).first()
        if color:
            custom_data['color_id'] = color.id
            request.session['custom_data'] = custom_data

    context = {
        'vehicle': vehicle,
        'color': color,
        'wheel': wheel,
        'bumper': bumper,
        'light': light,
        'aero': aero,
        'color_name': color.name if color else '未設定',
        'wheel_name': wheel.name if wheel else '未設定',
        'bumper_name': bumper.name if bumper else '未設定',
        'vehicles': Vehicle.objects.all().order_by('id'),
        'editing_id': editing_id,
        'current_custom_id': request.session.get('editing_custom_id'),
        'is_favorite': is_favorite,
    }
    return render(request, "auto_custom.html", context)

def auto_custom_api(request):
    try:
        # セッション取得（なければ新規）
        custom_data = request.session.get('custom_data', {})

        current_is_favorite = custom_data.get('is_favorite', False)

        # 車両選択
        vehicle = Vehicle.objects.order_by('?').first()

        # 各パーツを必ず vehicle 条件付きで取得
        color  = Color.objects.filter(vehicle=vehicle).order_by('?').first()
        wheel  = Wheel.objects.filter(vehicle=vehicle).order_by('?').first()
        bumper = Bumper.objects.filter(vehicle=vehicle).order_by('?').first()
        light  = Light.objects.filter(vehicle=vehicle).order_by('?').first()
        aero   = Aero.objects.filter(vehicle=vehicle).order_by('?').first()

        custom_data.update({
            'vehicle_id': vehicle.id,
            'color_id': color.id if color else None,
            'wheel_id': wheel.id if wheel else None,
            'bumper_id': bumper.id if bumper else None,
            'light_id': light.id if light else None,
            'aero_id': aero.id if aero else None,
            'is_favorite': current_is_favorite,
        })
        request.session['custom_data'] = custom_data
        request.session.modified = True  # ← 念のため

        return JsonResponse({
            'carFolder': vehicle.name_en,
            'carName': vehicle.name,
            'color': color.rotation_image_folder if color else 'black',
            'color_name': color.name if color else 'ブラック',
            'wheel_name': wheel.name if wheel else 'ホイール',
            'bumper_name': bumper.name if bumper else 'バンパー',
            'is_favorite': current_is_favorite,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def car_view(request):
    images = [
        "https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x2.jpg",
        "https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x3.jpg",
        "https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_XH32TC_x1.jpg"
    ]
    return render(request, "car.html", {"images": images})


# 自動カスタムページ
def auto_custom(request, custom_id=None):
    return render(request, "auto_custom.html")


# お気に入り切替機能
@login_required
@require_POST
def toggle_favorite(request, item_id):
    """お気に入りの状態を切り替える(AJAX用)"""
    item = get_object_or_404(SavedCustom, id=item_id, user=request.user)
    
    # 状態を反転
    item.is_favorite = not item.is_favorite
    item.save()
    
    return JsonResponse({
        'status': 'success',
        'is_favorite': item.is_favorite
    })

# セッション内のお気に入り状態更新機能
@require_POST
def update_session_favorite(request):
    """ページ遷移しても状態を保持するためにセッションのみ更新する"""
    try:
        data = json.loads(request.body)
        is_fav = data.get('is_favorite', False)
        
        custom_data = request.session.get('custom_data', {})
        custom_data['is_favorite'] = is_fav
        request.session['custom_data'] = custom_data
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
@require_POST
def update_session_favorite(request):
    import json
    try:
        data = json.loads(request.body)
        is_fav = data.get('is_favorite', False)
        
        # セッションから現在のカスタムデータを取得
        custom_data = request.session.get('custom_data', {})
        
        # お気に入り状態を更新してセッションに戻す
        custom_data['is_favorite'] = is_fav
        request.session['custom_data'] = custom_data
        
        # 明示的にセッションの変更を保存
        request.session.modified = True
        
        return JsonResponse({'status': 'success', 'is_favorite': is_fav})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# 自動カスタムAPI（urls.py にあるので最低限用意）
def auto_custom_api(request):
    # ここは本来ロジックが必要だが、まず起動優先で最低限返す
    return JsonResponse({"ok": True})


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

    custom_data = request.session.get('custom_data', {})
    if not custom_data:
        return redirect('custom_menu')

    # ===== is_favorite を取得 =====
    is_favorite_str = request.POST.get('is_favorite', 'false')
    is_favorite = (is_favorite_str.lower() == 'true')
        
        # 確認用：ターミナルに表示されます（不要になったら消してOK）
    print(f"--- DEBUG --- 届いた値: {is_favorite_str}, 判定結果: {is_favorite}")
    # IDからオブジェクト取得
    vehicle = Vehicle.objects.filter(id=custom_data.get('vehicle_id')).first()
    color   = Color.objects.filter(id=custom_data.get('color_id')).first()
    wheel   = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    bumper  = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()
    light   = Light.objects.filter(id=custom_data.get('light_id')).first()
    aero    = Aero.objects.filter(id=custom_data.get('aero_id')).first()

    # 合計計算
    total = Decimal('0.00')
    total = Decimal("0.00")
    for part in [color, wheel, bumper, light, aero]:
        if part and part.price:
            total += part.price

    editing_id = request.session.get('editing_custom_id')

    if editing_id:
        # ===== 更新 =====
        saved = get_object_or_404(
            SavedCustom, id=editing_id, user=request.user
        )

        saved.vehicle = vehicle
        saved.color = color
        saved.wheel = wheel
        saved.bumper = bumper
        saved.light = light
        saved.aero = aero
        saved.total_price = total
        saved.is_favorite = is_favorite
        saved.save()

    else:
        # ===== 新規作成 =====
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
            is_favorite=is_favorite,
            preview_image_url='uploads/previews/default.png',
        )

    request.session.pop('editing_custom_id', None)
    return redirect('list_page')
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
