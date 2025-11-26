from django import forms
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.models import User

from .models import User
from django.contrib.auth.hashers import make_password

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

# 新規登録
class RegisterForm(forms.Form):
    nickname = forms.CharField(
        max_length=30,
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
