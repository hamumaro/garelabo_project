from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LoginForm, RegisterForm

def test_view(request):
    return HttpResponse("API is working!")

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  # ログイン後のリダイレクト先 (一覧画面が出来たら変える)
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})

def list_page_view(request):
    return render(request, 'list.html')

def favorite_page_view(request):
    return render(request, 'Favorite_List.html')

    # return render(request, "login.html", {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})


def dashboard_view(request):
    """ログイン後のテスト用ページ"""
    return render(request, 'dashboard.html')
