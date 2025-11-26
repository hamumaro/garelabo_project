from decimal import Decimal  # ★追加: 計算用
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from .models import Vehicle
import random
from django.core.mail import send_mail
from django.db import transaction
import random


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
# views.py の register_view をこれに差し替え
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. ユーザーを仮保存
                    user = form.save(commit=False)
                    user.is_active = False  # まだ無効
                    user.save()

                    # 2. 認証コード(6桁)生成
                    code = str(random.randint(100000, 999999))

                    # 3. セッションに保存
                    request.session['verification_code'] = code
                    request.session['verification_user_id'] = user.id

                    # 4. メール送信
                    subject = "【GARELABO+】認証コードのお知らせ"
                    message = f"以下の認証コードを入力して登録を完了してください。\n\n認証コード: {code}"
                    from_email = "no-reply@garelabo.com"
                    recipient_list = [user.email]
                    
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                return redirect('verify')

            except Exception as e:
                print(f"メール送信エラー: {e}")
                form.add_error(None, "メール送信に失敗しました。")
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
            request.session.pop('verification_code', None)
            request.session.pop('verification_user_id', None)
            return redirect('register')

        # 再送信ボタン
        if 'resendCodebtn' in request.POST:
            code = str(random.randint(100000, 999999))
            request.session['verification_code'] = code
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
            message = 'コードを再送信しました。'
            return render(request, 'verify_code.html', {'form': form, 'message': message})

        # 確認ボタン
        form = VerificationForm(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data['authCode']
            session_code = request.session.get('verification_code')

            if input_code == session_code:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
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
# def custom_menu(request, custom_id= None):
#     vehicle = Vehicle.objects.get(pk=custom_id)
#     print("DEBUG:", vehicle.base_image_path.url)
#     return render(request, "custom_menu.html", {"vehicle": vehicle})
def custom_menu(request):
    vehicles = Vehicle.objects.all().order_by('id')  # 全車両取得
    return render(request, "custom_menu.html", {"vehicles": vehicles})

# --- 各パーツ選択画面 ---
def custom_menu_bodycolor(request):
    return render(request, "custom_menu_bodycolor.html")

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

def custom_cancel(request):
    return render(request, "custom_canceled.html")

def carselect(request):
    vehicles = Vehicle.objects.all().order_by('id')
    return render(request, 'carselect.html', {'vehicles': vehicles})



def car_view(request):
    # 画像リストは必要に応じてDBから取得するか、固定にする
    images = [
        'https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x2.jpg',
        'https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x3.jpg',
        'https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_XH32TC_x1.jpg'
    ]
    return render(request, 'car.html', {'images': images})

def car_select(request):
    # carselectと重複しているため、どちらかに統一推奨ですが一旦残します
    vehicles = Vehicle.objects.all().order_by('id')
    return render(request, 'carselect.html', {'vehicles': vehicles})


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
#     context = {
#         "car_image_url": "/media/" + car.base_image_path,
#         "car_name": car.name,
#     }
#     return render(request, 'custom_menu.html', context)


