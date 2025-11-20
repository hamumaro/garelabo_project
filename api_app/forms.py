from django import forms
from django.contrib.auth.forms import AuthenticationForm

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
            "autocomplete": "current-password",
            "id": "password"
        })   
    )