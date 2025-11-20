# api_app内のURL


from django.urls import path
from .views import login_view, register_view, dashboard_view
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用
    path('login/',  views.login_view, name='login'),  # ログイン

    path('favorite/', views.favorite_page_view, name='favorite_page'),

    path('', views.list_page_view, name='list_page'),  # 追加
    path('register/',  views.register_view, name='register'),  # 新規登録
    path('dashboard/',  views.dashboard_view, name='dashboard'),  # ログイン後ページ

]
