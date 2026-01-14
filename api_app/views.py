from decimal import Decimal  # ★追加: 計算用
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

# モデルとフォームのインポート
from .forms import LoginForm, RegisterForm, VerificationForm
from .models import SavedCustom, Vehicle, Wheel, Aero, Bumper, Color, Light # ★追加: パーツモデルをインポート

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
        ).order_by('-saved_at')
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
        ).order_by('-saved_at')
    else:
        custom_items = []

    return render(request, 'Favorite_List.html', {
        'custom_items': custom_items
    })

# 新規登録ページ表示
# api_app/views.py

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
        # キャンセルボタン（修正不要だが、HTML側の formnovalidate で動くようになる）
        if 'cancelAuthbtn' in request.POST:
            User.objects.filter(id=user_id, is_active=False).delete()
            request.session.pop('verification_code', None)
            request.session.pop('verification_user_id', None)
            # 登録途中のユーザーを削除する場合（任意）
            # User.objects.filter(id=user_id, is_active=False).delete()
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
                    fail_silently=False # エラーが見えるようにFalse推奨
                )
            except Exception as e:
                print(f"メール送信エラー: {e}")
            
            message = 'コードを再送信しました。'
            # フォームを空で再表示
            return render(request, 'verify_code.html', {'form': form, 'message': message})

        # 確認ボタン
        form = VerificationForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data['authCode']
            session_code = request.session.get('verification_code')

            # デバッグ用
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
    # --- パターンA: 編集モード（一覧画面から custom_id が渡された場合） ---
    if custom_id:
        # 1. 保存データを取得
        saved_item = get_object_or_404(SavedCustom, pk=custom_id, user=request.user)
        
        # 2. データをセッションに展開（続きから編集できるようにする）
        request.session['custom_data'] = {
            'vehicles_id': saved_item.vehicle.id if saved_item.vehicle else None,
            'color_id': saved_item.color.id if saved_item.color else None,
            'wheel_id': saved_item.wheel.id if saved_item.wheel else None,
            'bumper_id': saved_item.bumper.id if saved_item.bumper else None,
            'light_id': saved_item.light.id if saved_item.light else None,
            'aero_id': saved_item.aero.id if saved_item.aero else None,
        }

    # --- パターンB: 新規作成モード（車種選択画面から car_id が渡された場合） ---
    elif request.GET.get('car_id'):
        car_id = request.GET.get('car_id')
        # 車両が存在するか確認
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
            # セッションを修復
            custom_data['vehicle_id'] = vehicle.id
            request.session['custom_data'] = custom_data

    # 5. テンプレートへ渡す
    context = {
        "vehicle": vehicle,
    }
    return render(request, "custom_menu.html", context)



 
# カラー
# --- 各パーツ選択画面 ---
# def custom_menu_bodycolor(request):
#     # 1. セッションデータの準備
#     custom_data = request.session.get('custom_data', {})

#     # 車両IDを取得（なければDBの最初の車両をデフォルトにする）
#     vehicle_id = custom_data.get('vehicle_id')
#     if not vehicle_id:
#         first_vehicle = Vehicle.objects.first()
#         if first_vehicle:
#             vehicle_id = first_vehicle.id
#             # セッションに保存しておく
#             custom_data['vehicle_id'] = vehicle_id
#             request.session['custom_data'] = custom_data
#         else:
#             # 車両データ自体がない場合（seed_data未実行など）
#             return render(request, "custom_menu_bodycolor.html", {'colors': []})
 
#     # この車種のカラー一覧を取得
#     colors = Color.objects.filter(vehicle_id=vehicle_id)
 
#     # 2. POST送信（ボタンクリック）された時の処理
#     if request.method == 'POST':
#         selected_id = request.POST.get('color_id')
       
#         if selected_id:
#             # セッションに保存
#             custom_data['color_id'] = selected_id
#             request.session['custom_data'] = custom_data
           
#             # 保存したらリダイレクト（二重送信防止のため）
#             return redirect('custom_menu_bodycolor')
 
#     # 3. 現在選択されているカラーID（画面表示用）
#     current_color_id = custom_data.get('color_id')
 
#     context = {
#         'colors': colors,
#         'current_color_id': int(current_color_id) if current_color_id else None,
#         'vehicles': vehicles
#     }
#     # インデント（左端）を def と同じ位置に合わせてください
#     return render(request, "custom_menu_bodycolor.html", context)
 

def custom_menu_bodycolor(request):
    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')

    # 車両リストを必ず取得（これがないとJSがエラーになります）
    vehicles = Vehicle.objects.all().order_by('id')
    
    if not vehicle_id and vehicles.exists():
        vehicle_id = vehicles.first().id
        custom_data['vehicle_id'] = vehicle_id
        request.session['custom_data'] = custom_data

    colors = Color.objects.filter(vehicle_id=vehicle_id)
    current_color_id = custom_data.get('color_id')

    context = {
        'colors': colors,
        'current_color_id': int(current_color_id) if current_color_id else None,
        'vehicle_id': vehicle_id,
        'vehicles': vehicles, # ← ここが重要
    }
    return render(request, "custom_menu_bodycolor.html", context)


def custom_menu_wheel(request):
    return render(request, "custom_menu_wheel.html")
 
def custom_menu_bumper(request):
    return render(request, "custom_menu_bumper.html")
 
def custom_menu_light(request):
    return render(request, "custom_menu_light.html")
 
def custom_menu_aeroparts(request):
    return render(request, "custom_menu_aeroparts.html")
 
def auto_custom(request):
    custom_data = request.session.get('custom_data', {})
    vehicle_id = custom_data.get('vehicle_id')
    vehicle = Vehicle.objects.filter(id=vehicle_id).first() or Vehicle.objects.first()

    # セッションから選択済みのカラーを取得
    color_id = custom_data.get('color_id')
    color = Color.objects.filter(id=color_id, vehicle=vehicle).first()
    
    if not color:
        # 【修正】ここも rotation_image_folder に！
        color = Color.objects.filter(vehicle=vehicle, rotation_image_folder='black').first() \
                or Color.objects.filter(vehicle=vehicle).first()

    context = {
        'vehicle': vehicle,
        # 【修正】ここも rotation_image_folder に！
        'color_en': color.rotation_image_folder if color else "black",
        'color_name': color.name if color else "ブラック",
        'vehicles': Vehicle.objects.all().order_by('id'),
    }
    return render(request, "auto_custom.html", context)



def auto_custom_api(request):
    try:
        # セッション取得（なければ新規）
        custom_data = request.session.get('custom_data', {})

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
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def car_select(request):
    """車種選択画面を表示する"""
    from .models import Vehicle
    vehicles = Vehicle.objects.all()
    return render(request, 'car_select.html', {'vehicles': vehicles})

def custom_cancel(request):
    """カスタムを中止してリダイレクトする"""
    
    # 中止した後の遷移先（例: トップページや車種選択）を指定
    return render(request,'custom_canceled.html')


# --- ★重要: 見積もり計算機能 ---
def estimate_view(request):
    # 1. セッションから選択データを取得
    custom_data = request.session.get('custom_data', {})
    
    # 2. 各IDの取得
    vehicle_id = custom_data.get('vehicle_id')
    color_id   = custom_data.get('color_id')
    wheel_id   = custom_data.get('wheel_id')
    bumper_id  = custom_data.get('bumper_id')
    light_id   = custom_data.get('light_id')
    aero_id    = custom_data.get('aero_id')

    # 3. DBからデータ取得 (存在しないIDなら None)
    vehicle = Vehicle.objects.filter(id=vehicle_id).first()
    color   = Color.objects.filter(id=color_id).first()
    wheel   = Wheel.objects.filter(id=wheel_id).first()
    bumper  = Bumper.objects.filter(id=bumper_id).first()
    light   = Light.objects.filter(id=light_id).first()
    aero    = Aero.objects.filter(id=aero_id).first()

    # 4. 合計金額の計算
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
    # 1. POSTメソッドで来たか確認（安全のため）
    if request.method == 'POST':
        
        # 2. セッションデータの取得
        custom_data = request.session.get('custom_data', {})
        if not custom_data:
            return redirect('custom_menu')

        # 3. IDからオブジェクトを取得
        vehicle = Vehicle.objects.filter(id=custom_data.get('vehicle_id')).first()
        color = Color.objects.filter(id=custom_data.get('color_id')).first()
        wheel = Wheel.objects.filter(id=custom_data.get('wheel_id')).first()
        bumper = Bumper.objects.filter(id=custom_data.get('bumper_id')).first()
        light = Light.objects.filter(id=custom_data.get('light_id')).first()
        aero = Aero.objects.filter(id=custom_data.get('aero_id')).first()

        # 4. 合計金額計算
        total = Decimal('0.00')
        parts_list = [color, wheel, bumper, light, aero]
        for part in parts_list:
            if part and part.price:
                total += part.price

        # 5. 保存
        SavedCustom.objects.create(
            user=request.user,
            vehicle=vehicle,
            color=color,
            wheel=wheel,
            bumper=bumper,
            light=light,
            aero=aero,
            total_price=total,
            # ※仮画像を設定（Canvas実装後に修正）
            preview_image_url='uploads/previews/default.png',
            display_mode=False,
            is_favorite=False
        )
        
        # 6. ★重要: 保存後は「一覧ページ」へ戻る
        return redirect('list_page')

    # POST以外（URL直接入力など）で来た場合はカスタム画面へ戻す
    return redirect('custom_menu')