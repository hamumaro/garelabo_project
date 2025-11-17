# api_app内のURL


from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.test_view),  # 動作確認用
]
