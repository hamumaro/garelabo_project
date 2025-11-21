# api_app内のURL


from django.urls import path
from .views import login_view #, register_view, dashboard_view
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用

    # path('', login_view, name='login'),

    path('login/', login_view, name='login'),  # ログイン

    path('list/', views.list_page_view, name='list_page'),

    path('delete/<int:item_id>/',views.delete_item, name='delete_item'), #削除

    path('favorite/', views.favorite_page_view, name='favorite_page'),

    path('', views.list_page_view, name='list_page'),  # 追加

    path('register/',  views.register_view, name='register'),  # 新規登録

    path('dashboard/',  views.dashboard_view, name='dashboard'),  # ログイン後ページ
    path("custom_menu/", views.custom_menu, name="custom_menu"),#カスタムメニュー画面
    path("custom_menu/bodycolor/", views.custom_menu_bodycolor, name="custom_menu_bodycolor"),#ボディーカラー選択画面
    path("custom_menu/wheel/", views.custom_menu_wheel, name="custom_menu_wheel"),#ホイール選択画面
    path("custom_menu/bumper/", views.custom_menu_bumper, name="custom_menu_bumper"),#バンパー選択画面
    path("custom_menu/light/", views.custom_menu_light, name="custom_menu_light"),#ライト選択画面
    path("custom_menu/aeroparts/", views.custom_menu_aeroparts, name="custom_menu_aeroparts"),#エアロパーツ選択画面

]
