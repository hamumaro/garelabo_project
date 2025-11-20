from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
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
            "id" : "password"
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
            username=self.cleaned_data["nickname"],
            email=self.cleaned_data["email"],
            password=make_password(self.cleaned_data["password"])
        )
        if commit:
            user.save()
        return user

        


