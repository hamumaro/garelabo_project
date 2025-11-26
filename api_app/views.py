from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm
from .models import Vehicle
import random
from django.core.mail import send_mail
from .forms import LoginForm, RegisterForm, VerificationForm
from .models import SavedCustom, Vehicle
from django.db import transaction


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
            return redirect('list_page')  # ログイン後のリダイレクト先 (一覧画面が出来たら変える)
        else:
            print("--------------------------------------------------")
            print("ログインエラー:", form.errors)
            print("送信されたデータ:", request.POST)
            print("--------------------------------------------------")
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})

# def list_page_view(request):
#     return render(request, 'list.html')
#             # ログイン成功後は一覧ページへ
#             return redirect('list_page')
#     else:
#         form = LoginForm()
#     return render(request, "login.html", {'form': form})

# 一覧ページ表示
def list_page_view(request):
    #ログイン済み
    if request.user.is_authenticated:
        custom_items = SavedCustom.objects.filter(
            user=request.user
        ).order_by('-saved_at')
    # 未ログイン
    else:
        custom_items = []
    return render(request, 'List.html', {
        'custom_items': custom_items,
        'user': request.user,
    })

# お気に入りページ表示
def favorite_page_view(request):
    #ログイン済み
    if request.user.is_authenticated:
        custom_items = SavedCustom.objects.filter(
            user=request.user,
            is_favorite=True
        ).order_by('-saved_at')
    # 未ログイン
    else:
        custom_items = []

    return render(request, 'Favorite_List.html', {
        'custom_items': custom_items
    })

    # return render(request, "login.html", {'form': form})

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

                    # ★追加 2. 認証コード(6桁)をここで生成する！
                    code = str(random.randint(100000, 999999))

                    # ★追加 3. セッションに保存（これがないと次の画面で弾かれます）
                    request.session['verification_code'] = code
                    request.session['verification_user_id'] = user.id

                    # 4. メール送信 (生成したコードを本文に入れる)
                    subject = "【GARELABO+】認証コードのお知らせ"
                    message = f"以下の認証コードを入力して登録を完了してください。\n\n認証コード: {code}"
                    from_email = "no-reply@garelabo.com" # または settings.DEFAULT_FROM_EMAIL
                    recipient_list = [user.email]
                    
                    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

                # エラーがなければ認証画面へ
                return redirect('verify')

            except Exception as e:
                print(f"メール送信エラー: {e}")
                form.add_error(None, "メール送信に失敗しました。")
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})

# 認証コード入力画面 (定義書のボタン仕様に対応)
def verify_code_view(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        return redirect('register')

    form = VerificationForm()
    message = None

    if request.method == 'POST':
        # --- 定義書 No.6 キャンセルボタン (cancelAuthbtn) ---
        if 'cancelAuthbtn' in request.POST:
            # セッションクリアして登録画面へ
            request.session.pop('verification_code', None)
            request.session.pop('verification_user_id', None)
            return redirect('register')

        # --- 定義書 No.4 再送信ボタン (resendCodebtn) ---
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
                print(f"DEBUG: 再送信コード {code}")
            except Exception as e:
                print(f"メール送信エラー: {e}")
                
            message = 'コードを再送信しました。'
            return render(request, 'verify_code.html', {'form': form, 'message': message})

        # --- 定義書 No.5 確認ボタン (confirmbtn) ---
        # フォーム送信自体は confirmbtn で行われる前提
        form = VerificationForm(request.POST)
        if form.is_valid():
            # 定義書に合わせて authCode を取得
            input_code = form.cleaned_data['authCode']
            session_code = request.session.get('verification_code')

            if input_code == session_code:
                # 認証成功
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                
                login(request, user)
                
                # セッション掃除
                request.session.pop('verification_code', None)
                request.session.pop('verification_user_id', None)
                
                return redirect('list_page')
            else:
                # 認証失敗
                form.add_error('authCode', '認証コードが間違っています。')
                form.fields['authCode'].widget.attrs.update({
                    'class': 'verification-input error-input',
                    'placeholder': '再入力してください。',
                    'value': ''
                })

    return render(request, 'verify_code.html', {'form': form, 'message': message})



# アカウント表示
def account_view(request):
    user = request.user  # ログイン中のユーザー
    return render(request, "account.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": "********"  # パスワードは実際には直接取得不可
    })

# アカウント情報更新表示
def account_update_view(request):
    user = request.user  # ログイン中のユーザー
    return render(request, "account_update.html", {
        "nickname": user.nickname,
        "email": user.email,
        "password": "********"  # パスワードは実際には直接取得不可
    })

# アカウント情報保存処理
def account_save_view(request):
    if request.method == 'POST':
        user = request.user  # ログイン中のユーザー
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # ユーザー情報の更新
        user.nickname = nickname
        user.email = email
        password != "********"
        user.set_password(password)
        
        update_session_auth_hash(request, user)
        
        user.save()

        return redirect('account')  # アカウントページへリダイレクト
    else:
        return redirect('account_update')  # 更新ページへリダイレクト

# ログアウト
def logout_view(request):
    logout(request)
    return redirect('list_page')

# テスト用ページ
def dashboard_view(request):
    """ログイン後のテスト用ページ"""
    return render(request, 'dashboard.html')
# 削除機能
def delete_item(request, item_id):
    item = get_object_or_404(SavedCustom, id=item_id, user=request.user)
    # 削除
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


# カラー
def custom_menu_bodycolor(request):
    return render(request, "custom_menu_bodycolor.html")

def car_view(request):
    images = [
        'https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x2.jpg',
        'https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_S42_x3.jpg',
        'https://3des.daihatsu.co.jp/images/car/rocky/rocky2021/rocky_603502_XH32TC_x1.jpg'
    ]
    return render(request, 'car.html', {'images': images})

def car_select(request):
    vehicles = Vehicle.objects.all().order_by('id')
    return render(request, 'carselect.html', {'vehicles': vehicles})

# def custom_menu_view(request, car_id):
#     car = get_object_or_404(Vehicle, id=car_id)

#     context = {
#         "car_image_url": "/media/" + car.base_image_path,
#         "car_name": car.name,
#     }
#     return render(request, 'custom_menu.html', context)


