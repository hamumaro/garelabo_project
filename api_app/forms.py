from django import forms
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.models import User

from .models import User
from django.contrib.auth.hashers import make_password
import re

# ログイン
class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={
            "class" : "underline-input",
            "placeholder" : "メールアドレスを入力してください",
            "autocomplete": "email",
            "id": "email"
        })
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            "class" : "underline-input",
            "placeholder" : "パスワードを入力してください",
            "autocomplete" : "current-password",
            "id" : "password",
        })
    )
    error_messages = {
        "invalid_login": "メールアドレス または パスワードが正しくありません。",
        "inactive": "このアカウントは無効です。",
    }

# 新規登録
class RegisterForm(forms.Form):
    nickname = forms.CharField(
        required=True,
        label='ニックネーム',
        widget=forms.TextInput(attrs={
            "placeholder": "ニックネーム",
            "id": "nickname",
        })
    )
    email = forms.EmailField(
        required=True,
        label='メールアドレス',
        widget=forms.EmailInput(attrs={
            "placeholder" : "メールアドレス",
            "id" : "email",
        })
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            "placeholder" : "パスワード",
            "id" : "password",
        })
    )
    # ニックネーム文字数チェック
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']

        if len(nickname) > 20:
            raise forms.ValidationError("ニックネームは20文字以内で入力してください。")

        return nickname
    
    # パスワード形式チェック
    def clean_password(self):
        password = self.cleaned_data['password']

        # ★ 半角英数字チェック
        if not re.fullmatch(r'[a-zA-Z0-9]+', password):
            raise forms.ValidationError("パスワードは半角英数字で入力してください。")

        # ★ 念のため最大文字数チェック（UI bypass対策）
        if len(password) > 64:
            raise forms.ValidationError("パスワードは64文字以内で入力してください。")

        return password

    def save(self, commit=True):
        user = User(
            # 修正2: カスタムユーザーモデルには 'username' がないので 'nickname' に変更
            nickname=self.cleaned_data["nickname"],
            email=self.cleaned_data["email"],
            password=make_password(self.cleaned_data["password"])
        )
        if commit:
            user.save()
        return user

    # メアド重複チェック
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは既に登録されています。")
        else:
                # 仮登録（is_active=False）の場合は、再登録を許容するためエラーにしない
                pass
        return email
    
# 認証
class VerificationForm(forms.Form):
    # 定義書 No.3 に合わせて変数名・name属性を authCode に設定
    authCode = forms.CharField(
        required=True,
        label='認証コード',
        widget=forms.TextInput(attrs={
            "placeholder": "認証コード",
            "class": "verification-input",
            "name": "authCode", 
            "id": "authCode"
        })
    )

# アカウント情報更新
class AccountUpdateForm(forms.Form):
    nickname = forms.CharField(
        required=True,
        label='ニックネーム',
        widget=forms.TextInput(attrs={
            "id": "nickname", 
        })
    )

    password = forms.CharField(
        required=False,
        label='パスワード',
        widget=forms.PasswordInput(attrs={
            "id": "password", 
        })
    )

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']

        if len(nickname) > 20:
            raise forms.ValidationError("ニックネームは20文字以内で入力してください。")
        
        return nickname
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        # 未変更(空)の場合はOK
        if not password:
            return password

        # ★ 半角英数字チェック
        if not re.fullmatch(r'[a-zA-Z0-9]+', password):
            raise forms.ValidationError("パスワードは半角英数字で入力してください。")
        
        # ★ 最大文字数チェック
        if len(password) > 64:
            raise forms.ValidationError("パスワードは64文字以内で入力してください。")
        
        return password