# api_app内のURL


from django.urls import path
from .views import login_view,logout_view #logout_view #, register_view, dashboard_view
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用
    
    # path('', login_view, name='login'),

    path('login/', login_view, name='login'),  # ログイン

    path('list/<int:custom_id>', views.list_page_view, name='list_page'), # 一覧

    path('delete/<int:item_id>/',views.delete_item, name='delete_item'), #削除

    path('favorite/', views.favorite_page_view, name='favorite_page'),# お気に入り

    path('', views.list_page_view, name='list_page'),  # 追加

    path('register/',  views.register_view, name='register'),  # 新規登録

    path('dashboard/',  views.dashboard_view, name='dashboard'),  # ログイン後ページ
    
    path("custom_menu/", views.custom_menu, name="custom_menu"),#カスタムメニュー画面 (新規作成)
    
    # path("custom_menu/<int:custom_id>/", views.custom_menu, name="custom_menu"),#カスタムメニュー画面 (既存編集)
    
    path("custom_menu/bodycolor/", views.custom_menu_bodycolor, name="custom_menu_bodycolor"),#ボディーカラー選択画面
    path("custom_menu/wheel/", views.custom_menu_wheel, name="custom_menu_wheel"),#ホイール選択画面
    path("custom_menu/bumper/", views.custom_menu_bumper, name="custom_menu_bumper"),#バンパー選択画面
    path("custom_menu/light/", views.custom_menu_light, name="custom_menu_light"),#ライト選択画面
    path("custom_menu/aeroparts/", views.custom_menu_aeroparts, name="custom_menu_aeroparts"),#エアロパーツ選択画面
    path('carselect/', views.car_select, name='car_select'),  # 車種選択ページ
    path('custom_menu/auto_custom/', views.auto_custom, name='auto_custom'),  # 自動カスタムページ
    path('estimate/', views.estimate_view, name='estimate'),  # 見積りページ
    path('custom_cancel/', views.custom_cancel, name='custom_cancel'),  # カスタム中止ページ
    path('account/',views.account, name='account'),# アカウント情報ページ
    path('account/update/', views.account_update, name='account_update'),  # アカウント情報更新ページ


    path('car/', views.car_view, name='car'),

    path('account/', views.account_view, name='account'), #アカウント

    path('account_update/', views.account_update_view, name='account_update'), #アカウント編集

    path('account_save/', views.account_save_view, name='account_save'), #アカウント保存

    path('logout/', logout_view, name='logout'), #ログアウト
]
