# api_app内のURL


from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用

    path('list/', views.list_page_view, name='list_page'),

    path('favorite/', views.favorite_page_view, name='favorite_page'),

    path('', views.list_page_view, name='list_page'),  # 追加

    path('login/', views.login_page_view, name='login_page'),  # 追加
]
