# api_app内のURL


from django.urls import path
from .views import login_view
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),  # ログイン
]
