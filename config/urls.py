"""
URL configuration for garelabo_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# # プロジェクト全体のURLを管理

# urlpatterns = [
#     path("admin/", admin.site.urls),
# ]

#修正版
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # API用のURLを追加
    path('admin/', admin.site.urls),
    path('', include('api_app.urls')),  # ← api_app/urls.py を読み込む

    
]

# メディアファイルの配信設定（開発環境のみ）画像をファイルやブラウザで表示させる
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
