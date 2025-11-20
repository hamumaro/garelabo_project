# api_app内のURL


from django.urls import path
from .views import login_view
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用
    path('', login_view, name='login'),
    path('login/', login_view, name='login'),  # ログイン

    path('list/', views.list_page_view, name='list_page'),

    path('favorite/', views.favorite_page_view, name='favorite_page'),

    path('', views.list_page_view, name='list_page'),  # 追加

]
