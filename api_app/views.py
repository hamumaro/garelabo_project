from decimal import Decimal
import json
import random

from django.conf import settings
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
    get_user_model,
)
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

# モデルとフォームのインポート
from .forms import LoginForm, RegisterForm, VerificationForm
from .models import SavedCustom, Vehicle, Wheel, Aero, Bumper, Color, Light  # ★追加: パーツモデルをインポート

# ユーザーモデルを取得
User = get_user_model()


# 動作確認用
def test_view(request):
    return HttpResponse("API is working!")


# ログイン処理
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('list_page')
        else:
            print("--------------------------------------------------")
            print("ログインエラー:", form.errors)
            print("送信されたデータ:", request.POST)
            print("--------------------------------------------------")
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})


# 一覧ページ表示
def list_page_view(request):
    if request.user.is_authenticated:
        custom_items = SavedCustom.objects.filter(
            user=request.user
        ).select_related(
            "vehicle"
        ).order_by('-updated_at')
    else:
        custom_items = []
    return render(request, 'List.html', {
        'custom_items': custom_items,
        'user': request.user,
    })


# お気に入りページ表示
def favorite_page_view(request):
    if request.user.is_authenticated:
        custom_items = SavedCustom.objects.filter(
            user=request.user,
            is_favorite=True
        ).order_by('-updated_at')
    else:
        custom_items = []

    return render(request, 'Favorite_List.html', {
        'custom_items': custom_items
    })


# 新規登録ページ表示
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 同じメールアドレスの「仮登録データ」が残っていたら削除して上書き
                    email = form.cleaned_data['email']
                    User.objects.filter(email=email, is_active=False).delete()

                    # 1. ユーザーを仮保存
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()

                    # 2. 認証コード(6桁)生成
                    code = str(random.randint(100000, 999999))

                    # ★★★ 開発用ログ出力 ★★★
                    print("--------------------------------------------------")
                    print(f"【開発用】認証コード: {code}")
                    print("--------------------------------------------------")

                    # 3. セッションに保存
                    request.session['verification_code'] = code
                    request.session['verification_user_id'] = user.id

                    # 4. メール送信（失敗しても無視して進むように変更！）
                    subject = "【GARELABO+】認証コードのお知らせ"
                    message = f"以下の認証コードを入力して登録を完了してください。\n\n認証コード: {code}"
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [user.email]

                    try:
                        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
                    except Exception as e:
                        # メール失敗時はコンソールに表示して、処理は続行する
                        print(f"★メール送信失敗（開発用ログでコードを確認してください）: {e}")

                # メールが失敗しても、ここに来るので次の画面へ行ける
                return redirect('verify')

            except Exception as e:
                # データベース保存など、致命的なエラーだけここでキャッチ
                print(f"システムエラー: {e}")
                form.add_error(None, "登録処理に失敗しました。")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


# 認証コード入力画面
def verify_code_view(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        return redirect('register')

    form = VerificationForm()
    message = None

    if request.method == 'POST':
        # キャンセルボタン
        if 'cancelAuthbtn' in request.POST:
            User.objects.filter(id=user_id, is_active=False).delete()
            request.session.pop('verification_code', None)
            request.session.pop('verification_user_id', None)
            return redirect('register')

        # 再送信ボタン
        if 'resendCodebtn' in request.POST:
            code = str(random.randint(100000, 999999))
            request.session['verification_code'] = code

            # ★追加: 再送信時も開発用ログにコードを出す（メール失敗時用）
            print("--------------------------------------------------")
            print(f"【開発用(再送信)】認証コード: {code}")
            print("--------------------------------------------------")

            user = User.objects.get(id=user_id)
            try:
                send_mail(
                    "【GARELABO+】認証コードのお知らせ（再送信）",
                    f"認証コード: {code}",
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False  # エラーが見えるようにFalse推奨
                )
            except Exception as e:
                print(f"メール送信エラー: {e}")

            message = 'コードを再送信しました。'
            return render(request, 'verify_code.html', {'form': form, 'message': message})

        # 確認ボタン
        form = VerificationForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data['authCode']
            session_code = request.session.get('verification_code')

            print(f"入力コード: {input_code}, 正解コード: {session_code}")

            if input_code == session_code:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()

                # ★修正: 手動ログインの場合、バックエンドを指定する必要がある
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)

                request.session.pop('verification_code', None)
                request.session.pop('verification_user_id', None)

                return redirect('list_page')
            else:
                form.add_error('authCode', '認証コードが間違っています。')
                form.fields['authCode'].widget.attrs.update({
                    'class': 'verification-input error-input',
                    'placeholder': '再入力してください。',
                    'value': ''
                })

    return render(request, 'verify_code.html', {'form': form, 'message': message})


# アカウント表示
@login_required(login_url='/login/')
def account_view(request):
    user = request.user
    return render(request, "account.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": ""
    })


# アカウント情報更新表示
@login_required(login_url='/login/')
def account_update_view(request):
    user = request.user
    return render(request, "account_update.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": ""
    })


# アカウント情報保存処理
@login_required(login_url='/login/')
def account_save_view(request):
    if request.method == 'POST':
        user = request.user
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user.nickname = nickname
        user.email = email
        if password and password.strip() != "":
            user.set_password(password)

        update_session_auth_hash(request, user)
        user.save()

        return redirect('account')
    else:
        return redirect('account_update')


# ログアウト
def logout_view(request):
    logout(request)
    return redirect('list_page')


# テスト用ページ
def dashboard_view(request):
    return render(request, 'dashboard.html')


# 削除機能
@login_required(login_url='/login/')
def delete_item(request, item_id):
    item = get_object_or_404(SavedCustom, id=item_id, user=request.user)
    item.delete()
    return redirect('list_page')


# カスタムメニュー
def custom_menu(request, custom_id=None):
    # --- パターンA: 編集モード ---
    if custom_id:
        saved_item = get_object_or_404(SavedCustom, pk=custom_id, user=request.user)
        request.session['editing_custom_id'] = saved_item.id

        request.session['custom_data'] = {
            'vehicle_id': saved_item.vehicle.id if saved_item.vehicle else None,
            'color_id': saved_item.color.id if saved_item.color else None,
            'wheel_id': saved_item.wheel.id if saved_item.wheel else None,
            'bumper_id': saved_item.bumper.id if saved_item.bumper else None,
            'light_id': saved_item.light.id if saved_item.light else None,
            'aero_id': saved_item.aero.id if saved_item.aero else None,
        }

    # --- パターンB: 新規作成モード ---
    elif request.GET.get('car_id'):
        car_id = request.GET.get('car_id')
        vehicle = get_object_or_404(Vehicle, id=car_id)

        # 3. 新しいセッションを開始（前のカスタム情報をリセットして、選んだ車だけセット）
        request.session['custom_data'] = {
            'vehicle_id': vehicle.id
        }

    # --- 共通処理: 画面表示 ---
    # 4. セッションから現在の車両情報を取得して表示
    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')

    vehicle = None
    if vehicle_id:
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

    # 万が一車両データがない場合（セッション切れなど）は、DBの先頭の車をデフォルトにする
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data

    context = {
        "vehicle": vehicle,
    }
    return render(request, "custom_menu.html", context)


def restore_session_backup(request):
    """セッションのバックアップがあれば復元する（前の画面に戻った時用）※今は未実装"""
    return


def custom_menu_bodycolor(request, custom_id=None):
    restore_session_backup(request)

    # ===== 初期化 (編集モード) =====
    if custom_id:
        saved = SavedCustom.objects.filter(id=custom_id, user=request.user).first()

        # ★ここが重要: データが見つかった場合のみ読み込む
        if saved:
            request.session["custom_data"] = {
                'vehicle_id': saved.vehicle.id if saved.vehicle else None,
                'color_id': saved.color.id if saved.color else None,
                'wheel_id': saved.wheel.id if saved.wheel else None,
                'bumper_id': saved.bumper.id if saved.bumper else None,
                'light_id': saved.light.id if saved.light else None,
                'aero_id': saved.aero.id if saved.aero else None,
                'is_favorite': saved.is_favorite,
            }
            request.session['editing_custom_id'] = saved.id
            request.session.modified = True
        else:
            request.session.pop('editing_custom_id', None)
            # ここで get_object_or_404 しない（削除済みで落ちるため）

    custom_data = request.session.get('custom_data', {})

    # ▼▼▼▼▼ 修正箇所 ▼▼▼▼▼
    req_car_name = request.GET.get('car')
    req_reset = request.GET.get('reset')  # ★リセットフラグ取得

    # reset が来たら「車は残してパーツだけ初期化」みたいな動きにする（最小で事故りにくい）
    if req_reset:
        keep_vehicle_id = custom_data.get('vehicle_id')
        custom_data = {
            'vehicle_id': keep_vehicle_id,
            'is_favorite': custom_data.get('is_favorite', False),
        }
        request.session['custom_data'] = custom_data
        request.session.modified = True

    if req_car_name:
        vehicle_obj = Vehicle.objects.filter(name_en=req_car_name).first()
        if vehicle_obj:
            # セッションを更新
            custom_data['vehicle_id'] = vehicle_obj.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    vehicle_id = custom_data.get('vehicle_id')

    vehicle = Vehicle.objects.filter(id=vehicle_id).first() or Vehicle.objects.first()

    # 車両リストを必ず取得（これがないとJSがエラーになります）
    vehicles = Vehicle.objects.all().order_by('id')

    # vehicle が None の可能性を潰す
    if not vehicle and vehicles.exists():
        vehicle = vehicles.first()
        vehicle_id = vehicle.id
        custom_data['vehicle_id'] = vehicle_id
        request.session['custom_data'] = custom_data
        request.session.modified = True

    # vehicle_id が未セットなら先頭に寄せる
    if not vehicle_id and vehicles.exists():
        vehicle_id = vehicles.first().id
        custom_data['vehicle_id'] = vehicle_id
        request.session['custom_data'] = custom_data
        request.session.modified = True

    # カラー
    colors = Color.objects.filter(vehicle_id=vehicle_id)
    color = Color.objects.filter(id=custom_data.get('color_id'), vehicle=vehicle).first() if vehicle else None
    current_color = color  # ★未定義を潰す

    # wheel/bumper（フォルダ抽出用）
    current_wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    current_bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()

    def get_folder(obj, attr_name):
        if obj and getattr(obj, attr_name):
            return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
        return ""

    # フォルダ名
    car_folder = vehicle.name_en if vehicle else "CompactSedan"
    current_color_folder = get_folder(current_color, 'rotation_image_folder')
    current_wheel_folder = get_folder(current_wheel, 'image_url')
    current_bumper_folder = get_folder(current_bumper, 'image_url')

    context = {
        'colors': colors,
        'color': current_color,
        'current_color_id': int(custom_data.get('color_id')) if custom_data.get('color_id') else None,
        'vehicle_id': vehicle_id,
        'vehicle': vehicle,
        'vehicles': vehicles,  # ← ここが重要
        'is_favorite': custom_data.get('is_favorite', False),
        'car_folder': car_folder,
        'current_color_folder': current_color_folder,
        'current_wheel_folder': current_wheel_folder,
        'current_bumper_folder': current_bumper_folder,
    }
    return render(request, "custom_menu_bodycolor.html", context)


# ✅ 修正版（最小変更で未定義を潰す）
def custom_menu_wheel(request):
    restore_session_backup(request)
    custom_data = request.session.get('custom_data', {})

    # ★追加: vehicle_id をちゃんと取る（未定義エラー回避）
    vehicle_id = custom_data.get('vehicle_id')

    # 1. 車両の取得
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    # 2. ホイール一覧の取得
    wheels = Wheel.objects.filter(vehicle=vehicle) if vehicle else Wheel.objects.none()

    color_id = custom_data.get('color_id')
    current_color = Color.objects.filter(id=color_id).first()

    # フォルダ名（white, black等）を抽出
    current_color_folder = ""

    if current_color and current_color.rotation_image_folder:
        clean_path = str(current_color.rotation_image_folder).replace('\\', '/').rstrip('/')
        current_color_folder = clean_path.split('/')[-1]

    # もし色が未設定なら、デフォルト色を取得
    if not current_color_folder and vehicle:
        default_c = Color.objects.filter(vehicle=vehicle).first()
        if default_c and default_c.rotation_image_folder:
            clean_path = str(default_c.rotation_image_folder).replace('\\', '/').rstrip('/')
            current_color_folder = clean_path.split('/')[-1]

    # お気に入り状態を取得（なければFalse）
    is_favorite = custom_data.get('is_favorite', False)

    # ★追加: car_folder をちゃんと定義（未定義エラー回避）
    car_folder = vehicle.name_en if vehicle else "CompactSedan"

    context = {
        'vehicle': vehicle,
        'wheels': wheels,
        'is_favorite': is_favorite,
        'current_color_folder': current_color_folder,  # ★これをHTMLに渡します
        'car_folder': car_folder,
    }
    return render(request, "custom_menu_wheel.html", context)


# ✅ custom_menu_bumper 二重定義を解消して1つに統一（最小修正）
def custom_menu_bumper(request):
    restore_session_backup(request)

    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')

    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    # 3. この車両に紐づくバンパー一覧を取得
    bumpers = Bumper.objects.filter(vehicle=vehicle) if vehicle else Bumper.objects.none()

    current_color = Color.objects.filter(id=custom_data.get('color_id')).first()
    current_wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    current_bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()

    def get_folder(obj, attr_name):
        if obj and getattr(obj, attr_name):
            return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
        return ""

    car_folder = vehicle.name_en if vehicle else "CompactSedan"
    current_color_folder = get_folder(current_color, 'rotation_image_folder')
    current_wheel_folder = get_folder(current_wheel, 'image_url')
    current_bumper_folder = get_folder(current_bumper, 'image_url')

    is_favorite = custom_data.get('is_favorite', False)

    context = {
        'vehicle': vehicle,   # ★重要
        'bumpers': bumpers,   # ★重要
        'is_favorite': is_favorite,
        'car_folder': car_folder,
        'current_color_folder': current_color_folder,
        'current_wheel_folder': current_wheel_folder,
        'current_bumper_folder': current_bumper_folder,
    }
    return render(request, "custom_menu_bumper.html", context)


def custom_menu_light(request):
    return render(request, "custom_menu_light.html")


def custom_menu_aeroparts(request):
    return render(request, "custom_menu_aeroparts.html")


# # 自動カスタムページ
@never_cache
def auto_custom(request, custom_id=None):
    custom_data = request.session.get('custom_data', {})

    if custom_id:
        saved = get_object_or_404(SavedCustom, id=custom_id, user=request.user)
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
        request.session['editing_custom_id'] = saved.id
        request.session.modified = True

    editing_id = request.session.get('editing_custom_id')
    is_favorite = custom_data.get('is_favorite', False)

    # --- ★重要: URLパラメータによる強制上書き ---
    req_vehicle_id = request.GET.get('vehicle_id')
    req_color = request.GET.get('color')
    req_wheel = request.GET.get('wheel')
    req_bumper = request.GET.get('bumper')

    # (1) 車両IDの上書き
    if req_vehicle_id:
        vehicle_obj = Vehicle.objects.filter(id=req_vehicle_id).first()
        if vehicle_obj:
            custom_data['vehicle_id'] = vehicle_obj.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    vehicle_id = custom_data.get('vehicle_id')
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()

    # 車両がない場合のフォールバック
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    # (2) カラーの上書き
    if req_color and vehicle:
        temp_color = Color.objects.filter(vehicle=vehicle, rotation_image_folder__endswith=req_color).first()
        if temp_color:
            custom_data['color_id'] = temp_color.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    # (3) ホイールの上書き
    if req_wheel and vehicle:
        temp_wheel = Wheel.objects.filter(vehicle=vehicle, image_url__endswith=req_wheel).first()
        if temp_wheel:
            custom_data['wheel_id'] = temp_wheel.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    # (4) バンパーの上書き
    if req_bumper and vehicle:
        temp_bumper = Bumper.objects.filter(vehicle=vehicle, image_url__endswith=req_bumper).first()
        if temp_bumper:
            custom_data['bumper_id'] = temp_bumper.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    color = Color.objects.filter(id=custom_data.get('color_id'), vehicle=vehicle).first()
    wheel = Wheel.objects.filter(id=custom_data.get('wheel_id'), vehicle=vehicle).first()
    bumper = Bumper.objects.filter(id=custom_data.get('bumper_id'), vehicle=vehicle).first()
    light = Light.objects.filter(id=custom_data.get('light_id'), vehicle=vehicle).first()
    aero = Aero.objects.filter(id=custom_data.get('aero_id'), vehicle=vehicle).first()

    # パーツがない場合のデフォルト補正
    if not color and vehicle:
        color = Color.objects.filter(vehicle=vehicle).first()
        if color:
            custom_data['color_id'] = color.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    # --- パス整形処理 (強化) ---
    color_folder_name = "black"
    if color and color.rotation_image_folder:
        clean_path = str(color.rotation_image_folder).replace('\\', '/').rstrip('/')
        color_folder_name = clean_path.split('/')[-1]

    wheel_folder_name = "wheel1"
    if wheel and wheel.image_url:
        clean_path = str(wheel.image_url).replace('\\', '/').rstrip('/')
        wheel_folder_name = clean_path.split('/')[-1]

    bumper_folder_name = "bumper1"
    if bumper and bumper.image_url:
        clean_path = str(bumper.image_url).replace('\\', '/').rstrip('/')
        bumper_folder_name = clean_path.split('/')[-1]

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
        'light_name': light.name if light else '未設定',
        'aero_name': aero.name if aero else '未設定',
        'vehicles': Vehicle.objects.all().order_by('id'),
        'editing_id': editing_id,
        'current_custom_id': request.session.get('editing_custom_id'),
        'is_favorite': is_favorite,
        'color_rotation_folder': color_folder_name,
        'wheel_folder': wheel_folder_name,
        'bumper_folder': bumper_folder_name,
    }

    print(color)
    return render(request, "auto_custom.html", context)


def auto_custom_api(request):
    try:
        custom_data = request.session.get('custom_data', {})
        current_is_favorite = custom_data.get('is_favorite', False)

        vehicle = Vehicle.objects.order_by('?').first()

        # vehicleに紐づくパーツを取得
        color = Color.objects.filter(vehicle=vehicle).order_by('?').first()
        wheel = Wheel.objects.filter(vehicle=vehicle).order_by('?').first()
        bumper = Bumper.objects.filter(vehicle=vehicle).order_by('?').first()
        light = Light.objects.filter(vehicle=vehicle).order_by('?').first()
        aero = Aero.objects.filter(vehicle=vehicle).order_by('?').first()

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
        request.session.modified = True

        color_folder_name = "black"
        if color and color.rotation_image_folder:
            clean_path = str(color.rotation_image_folder).replace('\\', '/').rstrip('/')
            color_folder_name = clean_path.split('/')[-1]

        wheel_folder_name = "wheel1"
        if wheel and wheel.image_url:
            clean_path = str(wheel.image_url).replace('\\', '/').rstrip('/')
            wheel_folder_name = clean_path.split('/')[-1]

        return JsonResponse({
            'carFolder': vehicle.name_en,
            'carName': vehicle.name,
            'color': color_folder_name,
            'wheel': wheel_folder_name,
            'color_name': color.name if color else 'ブラック',
            'wheel_name': wheel.name if wheel else 'ホイール',
            'bumper_name': bumper.name if bumper else 'バンパー',
            'is_favorite': current_is_favorite,
        })

    except Exception as e:
        # エラー発生時はエラー内容をコンソールに出力しつつJSONを返す
        print(f"API Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def car_select(request):
    """車種選択画面を表示する"""
    vehicles = Vehicle.objects.all()
    return render(request, 'car_select.html', {'vehicles': vehicles})


def custom_cancel(request):
    """カスタムを中止してリダイレクトする"""
    return render(request, 'custom_canceled.html')


# お気に入り切替機能
@login_required(login_url='/login/')
@require_POST
def toggle_favorite(request, item_id):
    item = get_object_or_404(SavedCustom, id=item_id, user=request.user)

    # 状態を反転
    item.is_favorite = not item.is_favorite
    item.save()

    return JsonResponse({
        'status': 'success',
        'is_favorite': item.is_favorite
    })


# ✅ 二重定義を解消（これ1個に統一）
@require_POST
def update_session_favorite(request):
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


# ✅ urls.py が参照してるのに無いと落ちるやつ（update_session_parts）
@require_POST
def update_session_parts(request):
    try:
        data = json.loads(request.body)
        custom_data = request.session.get("custom_data", {})

        for key in ["vehicle_id", "color_id", "wheel_id", "bumper_id", "light_id", "aero_id"]:
            if key in data:
                custom_data[key] = data[key]

        request.session["custom_data"] = custom_data
        request.session.modified = True
        return JsonResponse({"status": "success", "custom_data": custom_data})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


# --- ★重要: 見積もり計算機能 ---
def estimate_view(request):
    restore_session_backup(request)
    custom_data = request.session.get('custom_data', {})

    # 2. 各IDの取得
    vehicle_id = custom_data.get('vehicle_id')
    color_id = custom_data.get('color_id')
    wheel_id = custom_data.get('wheel_id')
    bumper_id = custom_data.get('bumper_id')
    light_id = custom_data.get('light_id')
    aero_id = custom_data.get('aero_id')

    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    color = Color.objects.filter(id=color_id).first()
    wheel = Wheel.objects.filter(id=wheel_id).first()
    bumper = Bumper.objects.filter(id=bumper_id).first()
    light = Light.objects.filter(id=light_id).first()
    aero = Aero.objects.filter(id=aero_id).first()

    total = Decimal('0.00')

    # 合計に含めたいパーツをリスト化
    parts_list = [color, wheel, bumper, light, aero]

    for part in parts_list:
        if part and part.price:
            total += part.price

    context = {
        "vehicle": vehicle,
        "color": color,
        "wheel": wheel,
        "bumper": bumper,
        "light": light,
        "aero": aero,
        "total_price": total,
    }
    return render(request, "estimate.html", context)


# --- 見積もり保存機能 (新規追加) ---
@login_required(login_url='/login/')
def save_estimate_view(request):
    if request.method == 'POST':
        custom_data = request.session.get('custom_data', {})
        if not custom_data:
            return redirect('custom_menu')

        # IDからオブジェクトを取得
        vehicle = Vehicle.objects.filter(id=custom_data.get('vehicle_id')).first()
        color = Color.objects.filter(id=custom_data.get('color_id')).first()
        wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
        bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()
        light = Light.objects.filter(id=custom_data.get('light_id')).first()
        aero = Aero.objects.filter(id=custom_data.get('aero_id')).first()

        # 合計金額計算
        total = Decimal('0.00')
        parts_list = [color, wheel, bumper, light, aero]
        for part in parts_list:
            if part and part.price:
                total += part.price

        return redirect('custom_menu')
    return redirect('estimate')


# カスタム保存
@login_required(login_url='/login/')
def custom_save(request):
    if request.method != 'POST':
        return redirect('custom_menu')

    custom_data = request.session.get('custom_data', {})
    if not custom_data:
        return redirect('custom_menu')

    is_favorite_str = request.POST.get('is_favorite', 'false')
    is_favorite = (is_favorite_str.lower() == 'true')

    # 確認用：ターミナルに表示されます（不要になったら消してOK）
    print(f"--- DEBUG --- 届いた値: {is_favorite_str}, 判定結果: {is_favorite}")

    # IDからオブジェクト取得
    vehicle = Vehicle.objects.filter(id=custom_data.get('vehicle_id')).first()
    color = Color.objects.filter(id=custom_data.get('color_id')).first()
    wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()
    light = Light.objects.filter(id=custom_data.get('light_id')).first()
    aero = Aero.objects.filter(id=custom_data.get('aero_id')).first()

    total = Decimal('0.00')
    for part in [color, wheel, bumper, light, aero]:
        if part and part.price:
            total += part.price

    editing_id = request.session.get('editing_custom_id')

    saved = None
    if editing_id:
        saved = SavedCustom.objects.filter(id=editing_id, user=request.user).first()

    if saved:
        # ===== 更新 =====
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
        )

    request.session.pop('editing_custom_id', None)
    request.session.modified = True
    return redirect('list_page')


# エラーページ
def menu_error_view(request):
    return render(request, "menu_error.html", status=500)


def surroundings_error_view(request):
    return render(request, "surroundings_error.html", status=500)


def save_custom_content_error_view(request):
    return render(request, "save_custom_content_error.html", status=500)


def list_management_delection_error_view(request):
    return render(request, "list_management_delection_error.html", status=500)
