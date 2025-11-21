from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from .forms import LoginForm, RegisterForm

from .forms import LoginForm
from .models import SavedCustom

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
        items = SavedCustom.objects.filter(
            user=request.user,
            is_favorite=True
        ).order_by('-saved_at')
    # 未ログインならログイン画面へ
    else:
        items = []
    return render(request, 'Favorite_List.html', {'items': items})

    # return render(request, "login.html", {'form': form})

# 新規登録ページ表示
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})


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
