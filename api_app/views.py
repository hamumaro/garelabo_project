from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from .models import Vehicle
import random
from django.core.mail import send_mail
from django.db import transaction
import random
import json
from django.templatetags.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
# モデルとフォームのインポート
from .forms import LoginForm, RegisterForm, VerificationForm
from .models import SavedCustom, Vehicle, Wheel, Aero, Bumper, Color, Light
import os
from django.db.models import Q

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
        # 関連パーツを一括取得
        custom_items = SavedCustom.objects.filter(
            user=request.user
        ).select_related(
            "vehicle", "color", "wheel", "bumper", "light", "aero"
        ).order_by('-updated_at')

        for item in custom_items:
            def get_folder(obj, attr_name, default=""):
                if obj and getattr(obj, attr_name):
                    return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
                return default

            car_folder = item.vehicle.name_en if item.vehicle else "CompactSedan"
            color_folder = get_folder(item.color, 'rotation_image_folder', "black")
            wheel_folder = get_folder(item.wheel, 'image_url', "wheel1")
            bumper_folder = get_folder(item.bumper, 'image_url', "bumper1")
            # ★追加: エアロフォルダの取得 (デフォルトは aero1 または normal など環境に合わせてください)
            aero_folder = get_folder(item.aero, 'image_url', "normal")

            # ★修正: パス構成を変更 (.../wheel/bumper/aero/...)
            item.generated_image_url = (
                f"/media/uploads/vehicles/{car_folder}/"
                f"{color_folder}/{wheel_folder}/{bumper_folder}/{aero_folder}/front.png"
            )
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

    if request.user.is_authenticated:
        # 関連パーツを一括取得
        custom_items = SavedCustom.objects.filter(
            user=request.user,
            is_favorite=True
            
        ).select_related(
            "vehicle", "color", "wheel", "bumper", "light", "aero"
        ).order_by('-updated_at')

        for item in custom_items:
            def get_folder(obj, attr_name, default=""):
                if obj and getattr(obj, attr_name):
                    return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
                return default

            car_folder = item.vehicle.name_en if item.vehicle else "CompactSedan"
            color_folder = get_folder(item.color, 'rotation_image_folder', "black")
            wheel_folder = get_folder(item.wheel, 'image_url', "wheel1")
            bumper_folder = get_folder(item.bumper, 'image_url', "bumper1")
            # ★追加: エアロフォルダの取得 (デフォルトは aero1 または normal など環境に合わせてください)
            aero_folder = get_folder(item.aero, 'image_url', "normal")

            # ★修正: パス構成を変更 (.../wheel/bumper/aero/...)
            item.generated_image_url = (
                f"/media/uploads/vehicles/{car_folder}/"
                f"{color_folder}/{wheel_folder}/{bumper_folder}/{aero_folder}/front.png"
            )
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
                        #
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
                    fail_silently=False 
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
                
                # 手動ログインの場合、バックエンドを指定する必要がある
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
def account_update_view(request):
    user = request.user
    return render(request, "account_update.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": ""
    })

# アカウント情報保存処理
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
        
        request.session['custom_data'] = {
            'vehicle_id': vehicle.id
        }

    # --- 共通処理 ---
    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')
    
    vehicle = None
    if vehicle_id:
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data

    context = {
        "vehicle": vehicle,
    }
    return render(request, "custom_menu.html", context)


# カラー (★ここを修正: リセットロジック追加)
# def custom_menu_bodycolor(request, custom_id=None):
#     restore_session_backup(request)

#     # ===== 初期化 (編集モード) =====
#     if custom_id:
#         saved = SavedCustom.objects.filter(id=custom_id, user=request.user).first()
#         if saved:
#             request.session["custom_data"] = {
#                 'vehicle_id': saved.vehicle.id if saved.vehicle else None,
#                 'color_id': saved.color.id if saved.color else None,
#                 'wheel_id': saved.wheel.id if saved.wheel else None,
#                 'bumper_id': saved.bumper.id if saved.bumper else None,
#                 'light_id': saved.light.id if saved.light else None,
#                 'aero_id': saved.aero.id if saved.aero else None,
#                 'is_favorite': saved.is_favorite,
#             }
#             request.session['editing_custom_id'] = saved.id
#         else:
#             request.session.pop('editing_custom_id', None)

#     custom_data = request.session.get('custom_data', {})

#     # ▼▼▼▼▼ 修正箇所 ▼▼▼▼▼
#     req_car_name = request.GET.get('car')
#     req_reset = request.GET.get('reset') # ★リセットフラグ取得

#     if req_car_name:
#         vehicle_obj = Vehicle.objects.filter(name_en=req_car_name).first()
#         if vehicle_obj:
#             current_vid = custom_data.get('vehicle_id')
            
#             # 車両が違う場合、または「reset=true」がある場合は強制リセット
#             if (current_vid != vehicle_obj.id) or (req_reset == 'true'):
#                 custom_data = {
#                     'vehicle_id': vehicle_obj.id,
#                     'color_id': None,   # 全パーツをリセット
#                     'wheel_id': None,
#                     'bumper_id': None,
#                     'light_id': None,
#                     'aero_id': None,
#                     'is_favorite': False 
#                 }
#                 request.session['custom_data'] = custom_data
#                 request.session.modified = True
#     # ▲▲▲▲▲ 修正箇所ここまで ▲▲▲▲▲
    
#     vehicle_id = custom_data.get('vehicle_id')
#     vehicle = Vehicle.objects.filter(id=vehicle_id).first() or Vehicle.objects.first()
    
#     vehicles = Vehicle.objects.all().order_by('id')
#     if not vehicle_id and vehicles.exists():
#         vehicle_id = vehicles.first().id
#         custom_data['vehicle_id'] = vehicle_id
#         request.session['custom_data'] = custom_data

#     colors = Color.objects.filter(vehicle_id=vehicle_id)
#     current_color = Color.objects.filter(id=custom_data.get('color_id')).first()
#     current_wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
#     current_bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()

#     def get_folder(obj, attr_name):
#         if obj and getattr(obj, attr_name):
#             return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
#         return ""

#     car_folder = vehicle.name_en if vehicle else "CompactSedan"
#     current_color_folder = get_folder(current_color, 'rotation_image_folder')
#     current_wheel_folder = get_folder(current_wheel, 'image_url')
#     current_bumper_folder = get_folder(current_bumper, 'image_url')

#     context = {
#         'colors': colors,
#         'color': current_color,
#         'current_color_id': int(custom_data.get('color_id')) if custom_data.get('color_id') else None,
#         'vehicle_id': vehicle_id,
#         'vehicle': vehicle,
#         'vehicles': vehicles,
#         'is_favorite': custom_data.get('is_favorite', False),
#         'car_folder': car_folder,
#         'current_color_folder': current_color_folder,
#         'current_wheel_folder': current_wheel_folder,
#         'current_bumper_folder': current_bumper_folder,
#     }
#     return render(request, "custom_menu_bodycolor.html", context)

def custom_menu_bodycolor(request, custom_id=None):
    restore_session_backup(request)

    # ===== 初期化 (編集モード) =====
    if custom_id:
        saved = SavedCustom.objects.filter(id=custom_id, user=request.user).first()
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
        else:
            request.session.pop('editing_custom_id', None)

    custom_data = request.session.get('custom_data', {})

    # ===== 車両変更・リセットロジック =====
    req_car_name = request.GET.get('car')
    req_reset = request.GET.get('reset')

    if req_car_name:
        vehicle_obj = Vehicle.objects.filter(name_en=req_car_name).first()
        if vehicle_obj:
            current_vid = custom_data.get('vehicle_id')
            if (current_vid != vehicle_obj.id) or (req_reset == 'true'):
                custom_data = {
                    'vehicle_id': vehicle_obj.id,
                    'color_id': None,
                    'wheel_id': None,
                    'bumper_id': None,
                    'light_id': None,
                    'aero_id': None,
                    'is_favorite': False 
                }
                request.session['custom_data'] = custom_data
                request.session.modified = True
    
    # 車両の確定
    vehicle_id = custom_data.get('vehicle_id')
    vehicles = Vehicle.objects.all().order_by('id')
    vehicle = Vehicle.objects.filter(id=vehicle_id).first() or vehicles.first()
    
    if vehicle and not vehicle_id:
        vehicle_id = vehicle.id
        custom_data['vehicle_id'] = vehicle_id
        request.session['custom_data'] = custom_data

    # --- 【機能修正】DBからカラー一覧を取得してパレット用に整形 ---
    colors_query = Color.objects.filter(vehicle_id=vehicle_id)
    
    # DBにカラーコードがないため、色名からコードへの変換マップを定義
    color_map = {
        '白': '#ffffff', 'ホワイト': '#ffffff', 'White': '#ffffff',
        '黒': '#111111', 'ブラック': '#111111', 'Black': '#111111',
        '赤': '#c40000', 'レッド': '#c40000', 'Red': '#c40000',
        '青': '#2d9cdb', 'ブルー': '#2d9cdb', 'Blue': '#2d9cdb',
        '緑': '#27ae60', 'グリーン': '#27ae60', 'Green': '#27ae60',
        '紫': '#cb4af2', 'パープル': '#cb4af2','Purple' : '#cb4af2',
        '黄': '#f2c94c', 'イエロー': '#f2c94c', 'Yellow': '#f2c94c',
        '橙': '#f2994a','オレンジ':'#f2994a', 'Orange': '#f2994a',
    }

    processed_colors = []
    for c in colors_query:
        # パスからフォルダ名を抽出 (例: "uploads/colors/white" -> "white")
        raw_folder = str(c.rotation_image_folder)
        folder_name = raw_folder.replace('\\', '/').rstrip('/').split('/')[-1]
        
        # テンプレートで使用する一時的な属性を追加
        c.hex_code = color_map.get(c.name, '#888888') # マップになければグレー
        c.folder_name = folder_name
        processed_colors.append(c)
    # ---------------------------------------------------------

    # 各パーツ情報の取得
    current_color = Color.objects.filter(id=custom_data.get('color_id')).first()
    current_wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    current_bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()
    current_aero = Aero.objects.filter(id=custom_data.get('aero_id')).first()

    def get_folder(obj, attr_name):
        if obj and getattr(obj, attr_name):
            return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
        return ""

    context = {
        'colors': processed_colors,  # DBから取得・整形したリスト
        'color': current_color,
        'current_color_id': int(custom_data.get('color_id')) if custom_data.get('color_id') else None,
        'vehicle_id': vehicle_id,
        'vehicle': vehicle,
        'vehicles': vehicles,
        'is_favorite': custom_data.get('is_favorite', False),
        'car_folder': vehicle.name_en if vehicle else "CompactSedan",
        'current_color_folder': get_folder(current_color, 'rotation_image_folder'),
        'current_wheel_folder': get_folder(current_wheel, 'image_url'),
        'current_bumper_folder': get_folder(current_bumper, 'image_url'),
        'current_aero_folder': get_folder(current_aero, 'image_url'),
        'current_custom_id': request.session.get('editing_custom_id'),
    }
    return render(request, "custom_menu_bodycolor.html", context)


def custom_menu_wheel(request):
    restore_session_backup(request)
    custom_data = request.session.get('custom_data', {})
    
    vehicle_id = custom_data.get('vehicle_id')
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
             custom_data['vehicle_id'] = vehicle.id

    wheels = Wheel.objects.filter(vehicle=vehicle)

    color_id = custom_data.get('color_id')
    current_color = Color.objects.filter(id=color_id).first()
    
    current_color_folder = "" 
    if current_color and current_color.rotation_image_folder:
        clean_path = str(current_color.rotation_image_folder).replace('\\', '/').rstrip('/')
        current_color_folder = clean_path.split('/')[-1]
    
    if not current_color_folder:
         default_c = Color.objects.filter(vehicle=vehicle).first()
         if default_c and default_c.rotation_image_folder:
             clean_path = str(default_c.rotation_image_folder).replace('\\', '/').rstrip('/')
             current_color_folder = clean_path.split('/')[-1]

    is_favorite = custom_data.get('is_favorite', False)
    car_folder = vehicle.name_en if vehicle else "CompactSedan"
    
    context = {
        'vehicle': vehicle,
        'wheels': wheels,
        'is_favorite': is_favorite,
        'current_color_folder': current_color_folder,
        'car_folder': car_folder,
    }
    return render(request, "custom_menu_wheel.html", context)


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

    bumpers = Bumper.objects.filter(vehicle=vehicle)

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
        'vehicle': vehicle,
        'bumpers': bumpers,
        'is_favorite': is_favorite,
        'car_folder': car_folder,
        'current_color_folder': current_color_folder,
        'current_wheel_folder': current_wheel_folder,
        'current_bumper_folder': current_bumper_folder,
    }
    return render(request, "custom_menu_bumper.html", context)

# ライトパーツ
def custom_menu_light(request):
    return render(request, "custom_menu_light.html")
 

# エアロパーツ
def custom_menu_aeroparts(request):
    restore_session_backup(request)
    
    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')

    # 車両情報の取得・検証
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data

    # ★ここが重要：エアロパーツのデータをDBから取得
    aeros = Aero.objects.filter(vehicle=vehicle)

    # 現在選択されている各パーツのオブジェクトを取得
    current_color = Color.objects.filter(id=custom_data.get('color_id')).first()
    current_wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    current_bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()
    current_aero = Aero.objects.filter(id=custom_data.get('aero_id')).first()

    # フォルダ名抽出用ヘルパー
    def get_folder(obj, attr_name):
        if obj and getattr(obj, attr_name):
            return str(getattr(obj, attr_name)).replace('\\', '/').rstrip('/').split('/')[-1]
        return ""

    # フロントエンド用のフォルダ名を作成
    car_folder = vehicle.name_en if vehicle else "CompactSedan"
    current_color_folder = get_folder(current_color, 'rotation_image_folder')
    current_wheel_folder = get_folder(current_wheel, 'image_url')
    current_bumper_folder = get_folder(current_bumper, 'image_url')
    current_aero_folder = get_folder(current_aero, 'image_url')

    is_favorite = custom_data.get('is_favorite', False)
    
    context = {
        'vehicle': vehicle,
        'aeros': aeros, # テンプレートの {% for aero in aeros %} に渡されます
        'is_favorite': is_favorite,
        'car_folder': car_folder,
        'current_color_folder': current_color_folder,
        'current_wheel_folder': current_wheel_folder,
        'current_bumper_folder': current_bumper_folder,
        'current_aero_folder': current_aero_folder,
    }
    return render(request, "custom_menu_aeroparts.html", context)

 
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
    
    if 'pre_auto_custom_backup' not in request.session:
        request.session['pre_auto_custom_backup'] = custom_data.copy()

    editing_id = request.session.get('editing_custom_id')
    is_favorite = custom_data.get('is_favorite', False)

    req_vehicle_id = request.GET.get('vehicle_id')
    req_color = request.GET.get('color')
    req_wheel = request.GET.get('wheel')
    req_bumper = request.GET.get('bumper')
    req_aero = request.GET.get('aero')
    
    if req_vehicle_id:
        vehicle_obj = Vehicle.objects.filter(id=req_vehicle_id).first()
        if vehicle_obj:
            custom_data['vehicle_id'] = vehicle_obj.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    vehicle_id = custom_data.get('vehicle_id')
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    
    if not vehicle:
        vehicle = Vehicle.objects.first()
        if vehicle:
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data

    if req_color:
        temp_color = Color.objects.filter(vehicle=vehicle, rotation_image_folder__endswith=req_color).first()
        if temp_color:
            custom_data['color_id'] = temp_color.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    if req_wheel:
        temp_wheel = Wheel.objects.filter(vehicle=vehicle, image_url__endswith=req_wheel).first()
        if temp_wheel:
            custom_data['wheel_id'] = temp_wheel.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    if req_bumper:
        temp_bumper = Bumper.objects.filter(vehicle=vehicle, image_url__endswith=req_bumper).first()
        if temp_bumper:
            custom_data['bumper_id'] = temp_bumper.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    if req_aero:
        temp_aero = Aero.objects.filter(vehicle=vehicle, image_url__endswith=req_aero).first()
        if temp_aero:
            custom_data['aero_id'] = temp_aero.id
            request.session['custom_data'] = custom_data
            request.session.modified = True

    color = Color.objects.filter(id=custom_data.get('color_id'), vehicle=vehicle).first()
    wheel = Wheel.objects.filter(id=custom_data.get('wheel_id'), vehicle=vehicle).first()
    bumper = Bumper.objects.filter(id=custom_data.get('bumper_id'), vehicle=vehicle).first()
    light = Light.objects.filter(id=custom_data.get('light_id'), vehicle=vehicle).first()
    aero = Aero.objects.filter(id=custom_data.get('aero_id'), vehicle=vehicle).first()

    if not color:
        color = Color.objects.filter(vehicle=vehicle).first()
        if color:
            custom_data['color_id'] = color.id

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

    aero_folder_name = "aero1"
    if aero and aero.image_url:
        clean_path = str(aero.image_url).replace('\\', '/').rstrip('/')
        aero_folder_name = clean_path.split('/')[-1]

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
        'bumper': bumper,
        'bumper_folder': bumper_folder_name,
        'aero_folder': aero_folder_name,
    }

    print(color)
    return render(request, "auto_custom.html", context)


def auto_custom_api(request):
    try:
        custom_data = request.session.get('custom_data', {})
        current_is_favorite = custom_data.get('is_favorite', False)

        # ランダムにパーツを取得
        vehicle = Vehicle.objects.order_by('?').first()
        color   = Color.objects.filter(vehicle=vehicle).order_by('?').first()
        wheel   = Wheel.objects.filter(vehicle=vehicle).order_by('?').first()
        bumper  = Bumper.objects.filter(vehicle=vehicle).order_by('?').first()
        light   = Light.objects.filter(vehicle=vehicle).order_by('?').first()
        aero    = Aero.objects.filter(vehicle=vehicle).order_by('?').first()

        # セッション更新
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

        # --- フォルダ名抽出ロジック ---

        # 1. カラー
        color_folder_name = "black"
        if color and color.rotation_image_folder:
            clean_path = str(color.rotation_image_folder).replace('\\', '/').rstrip('/')
            color_folder_name = clean_path.split('/')[-1]

        # 2. ホイール
        wheel_folder_name = "wheel1"
        if wheel and wheel.image_url:
            clean_path = str(wheel.image_url).replace('\\', '/').rstrip('/')
            wheel_folder_name = clean_path.split('/')[-1]

        # 3. バンパー (★ここを追加)
        bumper_folder = "bumper1"
        if bumper and bumper.image_url:
            clean_path = str(bumper.image_url).replace('\\', '/').rstrip('/')
            bumper_folder = clean_path.split('/')[-1]

        # 4. エアロ (★ここを追加)
        aero_folder = "aero1"
        if aero and aero.image_url:
            clean_path = str(aero.image_url).replace('\\', '/').rstrip('/')
            aero_folder = clean_path.split('/')[-1]

        return JsonResponse({
            'carFolder': vehicle.name_en,
            'carName': vehicle.name,
            'color': color_folder_name,
            'wheel': wheel_folder_name,
            'bumper': bumper_folder,    
            'aero': aero_folder,         
            'color_name': color.name if color else 'カラー',
            'wheel_name': wheel.name if wheel else 'ホイール',
            'bumper_name': bumper.name if bumper else 'バンパー',
            'aero_name': aero.name if aero else 'エアロ',  
            'is_favorite': current_is_favorite,
        })

    except Exception as e:
        print(f"API Error: {e}") 
        return JsonResponse({'error': str(e)}, status=500)


def car_select(request):
    from .models import Vehicle
    vehicles = Vehicle.objects.all()
    return render(request, 'car_select.html', {'vehicles': vehicles})

def custom_cancel(request):
    # バックアップがあれば復元
    if 'pre_auto_custom_backup' in request.session:
        request.session['custom_data'] = request.session['pre_auto_custom_backup']
        del request.session['pre_auto_custom_backup']
        request.session.modified = True
    return render(request, 'custom_canceled.html')


# お気に入り切替機能
@login_required
@require_POST
def toggle_favorite(request, item_id):
    item = get_object_or_404(SavedCustom, id=item_id, user=request.user)
    item.is_favorite = not item.is_favorite
    item.save()
    return JsonResponse({
        'status': 'success',
        'is_favorite': item.is_favorite
    })

# セッション内のお気に入り状態更新機能
@require_POST
def update_session_favorite(request):
    import json
    try:
        data = json.loads(request.body)
        is_fav = data.get('is_favorite', False)
        
        custom_data = request.session.get('custom_data', {})
        custom_data['is_favorite'] = is_fav
        request.session['custom_data'] = custom_data
        request.session.modified = True
        
        return JsonResponse({'status': 'success', 'is_favorite': is_fav})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# 見積もり計算機能
def estimate_view(request):
    restore_session_backup(request)
    custom_data = request.session.get('custom_data', {})
    
    vehicle_id = custom_data.get('vehicle_id')
    color_id   = custom_data.get('color_id')
    wheel_id   = custom_data.get('wheel_id')
    bumper_id  = custom_data.get('bumper_id')
    light_id   = custom_data.get('light_id')
    aero_id    = custom_data.get('aero_id')

    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    color   = Color.objects.filter(id=color_id).first()
    wheel   = Wheel.objects.filter(id=wheel_id).first()
    bumper  = Bumper.objects.filter(id=bumper_id).first()
    light   = Light.objects.filter(id=light_id).first()
    aero    = Aero.objects.filter(id=aero_id).first()

    total = Decimal('0.00')
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

# 見積もり保存機能
@login_required(login_url='/login/')
def save_estimate_view(request):
    if request.method == 'POST':
        return redirect('custom_menu')
    return redirect('estimate')


@require_POST
def update_session_parts(request):
    """
    JSからのパーツ選択をセッションに同期するビュー。
    views.py.txt の icontains ロジックを統合。
    """
    try:
        data = json.loads(request.body)
        part_type = data.get('part_type') # 'color', 'wheel', 'bumper'
        val = data.get('folder_name')     # 'black', 'wheel1' 等の名称

        custom_data = request.session.get('custom_data', {})
        vehicle_id = custom_data.get('vehicle_id')

        if not vehicle_id:
            return JsonResponse({'status': 'error', 'message': '車両が選択されていません'}, status=400)
        
        if not val:
            return JsonResponse({'status': 'error', 'message': '値が空です'}, status=400)

        vehicle = Vehicle.objects.filter(id=vehicle_id).first()
        if not vehicle:
            return JsonResponse({'status': 'error', 'message': '該当する車両が見つかりません'}, status=400)

        # 各モデルのフィールド名に合わせて検索条件を切り分け (views.py.txt の icontains を採用)
        obj = None
        if part_type == 'color':
            # Colorモデル: rotation_image_folder に val が含まれるものを検索
            obj = Color.objects.filter(vehicle=vehicle, rotation_image_folder__icontains=val).first()
            if obj: custom_data['color_id'] = obj.id
        
        elif part_type == 'wheel':
            # Wheelモデル: image_url に val が含まれるものを検索
            obj = Wheel.objects.filter(vehicle=vehicle, image_url__icontains=val).first()
            if obj: custom_data['wheel_id'] = obj.id
            
        elif part_type == 'bumper':
            # Bumperモデル: image_url に val が含まれるものを検索
            obj = Bumper.objects.filter(vehicle=vehicle, image_url__icontains=val).first()
            if obj: custom_data['bumper_id'] = obj.id

        if not obj:
            return JsonResponse({
                'status': 'error', 
                'message': f'該当パーツが見つかりませんでした: {part_type}={val}'
            }, status=404)

        # セッションを更新して保存
        request.session['custom_data'] = custom_data
        request.session.modified = True
        
        return JsonResponse({
            'status': 'success', 
            'part_type': part_type, 
            'updated_id': obj.id,
            'current_session': custom_data
        })

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# カスタム保存
@login_required
def custom_save(request):
    if request.method != 'POST':
        return redirect('car_select')

    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')

    if not vehicle_id:
        return redirect('car_select')

    # 1) 必要なオブジェクト取得
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    color  = Color.objects.filter(id=custom_data.get('color_id')).first()
    wheel  = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
    bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()

    # custom_save 内：取得を追加
    aero = Aero.objects.filter(id=custom_data.get('aero_id')).first()

    # 2) 価格計算
    total = Decimal("0")
    if color:  total += Decimal(str(color.price or 0))
    if wheel:  total += Decimal(str(wheel.price or 0))
    if bumper: total += Decimal(str(bumper.price or 0))
    # 価格に加算（必要なら）
    if aero: total += Decimal(str(aero.price or 0))

    is_favorite = (request.POST.get('is_favorite') == 'true')

    # 3) 画像URL生成（JSのルールに合わせて normal を矯正）
    def last_folder(value, default):
        """
        value: 例) 'uploads/xxx/bumper1' や 'bumper1'
        """
        if not value:
            return default
        s = str(value).replace("\\", "/").rstrip("/")
        return s.split("/")[-1] if s else default

    # 車フォルダ（Vehicle に name_en がある想定。無ければ別の字段へ）
    car_folder = getattr(vehicle, "name_en", None) or "CompactSedan"

    color_folder  = last_folder(getattr(color, "rotation_image_folder", None), "white")
    wheel_folder  = last_folder(getattr(wheel, "image_url", None), "wheel1")

    bumper_folder = last_folder(getattr(bumper, "image_url", None), "bumper1")
    if bumper_folder == "normal":
        bumper_folder = "bumper1"

    aero_folder = last_folder(getattr(aero, "image_url", None), "aero1")
    if aero_folder == "normal":
        aero_folder = "aero1"

    preview_url = f"/media/uploads/vehicles/{car_folder}/{color_folder}/{wheel_folder}/{bumper_folder}/{aero_folder}/front.png"

    # 4) DB保存
    editing_id = request.session.get('editing_custom_id')

    try:
        with transaction.atomic():
            if editing_id:
                custom_obj = get_object_or_404(SavedCustom, id=editing_id, user=request.user)
            else:
                custom_obj = SavedCustom(user=request.user)

            custom_obj.vehicle = vehicle
            custom_obj.color = color
            custom_obj.wheel = wheel
            custom_obj.bumper = bumper
            custom_obj.total_price = total
            custom_obj.is_favorite = is_favorite

            # ★ここが重要: URL を保存
            custom_obj.preview_image_url = preview_url  # ← SavedCustom のフィールド名に合わせる

            # DB保存に反映（SavedCustom に aero がある場合）
            if hasattr(custom_obj, "aero"):
                custom_obj.aero = aero

            custom_obj.save()

        # 5) セッションクリア
        request.session.pop('editing_custom_id', None)
        request.session.pop('custom_data', None)
        request.session.modified = True

        return redirect('list_page')

    except Exception as e:
        print(f"SAVE ERROR: {e}")
        return HttpResponse(f"保存失敗: {e}", status=500)



def menu_error_view(request):
    return render(request, "menu_error.html", status=500)

def surroundings_error_view(request):
    return render(request, "surroundings_error.html", status=500)

def save_custom_content_error_view(request):
    return render(request, "save_custom_content_error.html", status=500)

def list_management_delection_error_view(request):
    return render(request, "list_management_delection_error.html", status=500)


def restore_session_backup(request):
    if 'pre_auto_custom_backup' in request.session:
        request.session['custom_data'] = request.session['pre_auto_custom_backup']
        del request.session['pre_auto_custom_backup']
        request.session.modified = True

# セッションの更新
@require_POST
def update_session_parts(request):
    try:
        data = json.loads(request.body)
        part_type = data.get('part_type')
        val = data.get('folder_name')

        custom_data = request.session.get('custom_data', {})
        vehicle_id = custom_data.get('vehicle_id')
        if not vehicle_id: return JsonResponse({'status': 'error'}, status=400)
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

        obj = None
        if part_type == 'color':
            obj = Color.objects.filter(vehicle=vehicle, rotation_image_folder__icontains=val).first()
            if obj: custom_data['color_id'] = obj.id
        elif part_type == 'wheel':
            obj = Wheel.objects.filter(vehicle=vehicle, image_url__icontains=val).first()
            if obj: custom_data['wheel_id'] = obj.id
        elif part_type == 'bumper':
            # normalでもDB検索するよう修正
            obj = Bumper.objects.filter(vehicle=vehicle, image_url__icontains=val).first()
            if obj: custom_data['bumper_id'] = obj.id
        elif part_type == 'aero':
            # ★追加: aero対応
            obj = Aero.objects.filter(vehicle=vehicle, image_url__icontains=val).first()
            if obj: custom_data['aero_id'] = obj.id

        request.session['custom_data'] = custom_data
        request.session.modified = True
        return JsonResponse({'status': 'success', 'updated_id': obj.id if obj else None})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)    



@require_POST
def update_session_selection(request):
    try:
        data = json.loads(request.body)
        part_type = data.get('type')
        folder_name = data.get('value')

        custom_data = request.session.get('custom_data', {})
        vehicle_id = custom_data.get('vehicle_id')
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

        if part_type == 'color':
            obj = Color.objects.filter(vehicle=vehicle).filter(Q(rotation_image_folder=folder_name)|Q(name=folder_name)).first()
            if obj: custom_data['color_id'] = obj.id
        elif part_type == 'wheel':
            obj = Wheel.objects.filter(vehicle=vehicle, image_url__icontains=folder_name).first()
            if obj: custom_data['wheel_id'] = obj.id
        elif part_type == 'bumper':
            obj = Bumper.objects.filter(vehicle=vehicle, image_url__icontains=folder_name).first()
            if obj: custom_data['bumper_id'] = obj.id
        elif part_type == 'aero':
            obj = Aero.objects.filter(vehicle=vehicle, image_url__icontains=folder_name).first()
            if obj: custom_data['aero_id'] = obj.id

        request.session['custom_data'] = custom_data
        request.session.modified = True
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
