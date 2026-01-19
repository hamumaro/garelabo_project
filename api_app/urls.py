from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用
    
    path('login/', login_view, name='login'),  # ログイン

    path('list/<int:custom_id>', views.list_page_view, name='list_page'), # 一覧

    path('custom/save/', views.custom_save, name='save_custom'), # カスタム保存
    
    path('delete/<int:item_id>/',views.delete_item, name='delete_item'), #削除

    path('update_session_favorite/', views.update_session_favorite, name='update_session_favorite'), # セッションのお気に入り更新
    path('favorite/', views.favorite_page_view, name='favorite_page'),# お気に入り

    path('', views.list_page_view, name='list_page'),  # 追加

    path('register/',  views.register_view, name='register'),  # 新規登録
    path('verify/', views.verify_code_view, name='verify'), # 認証

    path('dashboard/',  views.dashboard_view, name='dashboard'),  # ログイン後ページ
    
    path("custom_menu/", views.custom_menu, name="custom_menu"),#カスタムメニュー画面 (新規作成)
    
    path("custom_menu/<int:custom_id>/", views.custom_menu, name="custom_menu"),#カスタムメニュー画面 (既存編集)
    
    path("custom_menu/bodycolor/", views.custom_menu_bodycolor, name="custom_menu_bodycolor"),#ボディーカラー選択画面
    path("test/", views.test_view, name="test"),

    # auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    path("verify/", views.verify_code_view, name="verify"),

    # list / favorite / delete
    path("", views.list_page_view, name="list_page"),
    path("list/<int:custom_id>", views.list_page_view, name="list_page"),
    path("favorite/", views.favorite_page_view, name="favorite_page"),
    path("delete/<int:item_id>/", views.delete_item, name="delete_item"),

    # custom flow
    path("custom_menu/", views.custom_menu, name="custom_menu"),
    path("custom_menu/<int:custom_id>/", views.custom_menu, name="custom_menu"),
    path("custom_menu/bodycolor/", views.custom_menu_bodycolor, name="custom_menu_bodycolor"),
    path("custom_menu/bodycolor/<int:custom_id>/", views.custom_menu_bodycolor, name="custom_menu_bodycolor"),
    path("custom_menu/wheel/", views.custom_menu_wheel, name="custom_menu_wheel"),
    path("custom_menu/bumper/", views.custom_menu_bumper, name="custom_menu_bumper"),
    path("custom_menu/light/", views.custom_menu_light, name="custom_menu_light"),
    path("custom_menu/aeroparts/", views.custom_menu_aeroparts, name="custom_menu_aeroparts"),

    path("custom/save/", views.custom_save, name="save_custom"),

    # car select / auto / estimate
    path("car_select/", views.car_select, name="car_select"),
    path("auto_custom/", views.auto_custom, name="auto_custom"),
    path("auto_custom/<int:custom_id>/", views.auto_custom, name="auto_custom"),

    path("estimate/", views.estimate_view, name="estimate"),
    path("estimate/save/", views.save_estimate_view, name="save_estimate"),

    path("custom_cancel/", views.custom_cancel, name="custom_cancel"),

    # account
    path("account/", views.account_view, name="account"),
    path("account_update/", views.account_update_view, name="account_update"),
    path("account_save/", views.account_save_view, name="account_save"),

    # misc
    path("car/", views.car_view, name="car"),

    # errors
    path("menu_error/", views.menu_error_view, name="menu_error"),
    path("surroundings_error/", views.surroundings_error_view, name="surroundings_error"),
    path("save_custom_content_error/", views.save_custom_content_error_view, name="save_custom_content_error"),
    path("list_management_delection_error/", views.list_management_delection_error_view, name="list_management_delection_error"),
]
