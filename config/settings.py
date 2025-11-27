from pathlib import Path
import os
import environ  # django-environを使用

# 1. 環境変数の初期設定
# -----------------------------------------------------------------------------
# プロジェクトのルートディレクトリ
BASE_DIR = Path(__file__).resolve().parent.parent

# envオブジェクトの作成
env = environ.Env()

# .env ファイルを読み込む
# (ファイルがない場合でもエラーにならないよう、存在チェックを入れるか、
#  もしくは開発環境ならエラーになっても良いのでそのまま読み込みます)
env_file = os.path.join(BASE_DIR, '.env')
environ.Env.read_env(env_file)
# -----------------------------------------------------------------------------


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# .env から読み込み（なければデフォルト値を使用）
SECRET_KEY = env('SECRET_KEY', default="django-insecure-@4*bvgd%$*ks2(7k3_bw@v(2%xj3_#$^(!2@xr_kag0t^q%ne#")

# SECURITY WARNING: don't run with debug turned on in production!
# .env から読み込み（なければ True）
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    # "django.contrib.admin", # 重複していたので整理
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.admin',  # 管理画面用（マイグレーションエラー回避のため必須）

    # appsをアプリとして設定
    'api_app.apps.ApiAppConfig',

    # サードパーティ製アプリ
    'rest_framework',
    'corsheaders',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware", # CORSミドルウェア
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# .env に DATABASE_URL があればそれを使い、なければSQLiteを使用する設定
DATABASES = {
    "default": env.db(default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# カスタムUserモデルの指定
AUTH_USER_MODEL = 'api_app.User'

# メディアファイル設定
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS設定
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


# メール送信設定 (Gmail)
# -----------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# 環境変数から読み込み（.envに記述すること）
EMAIL_HOST_USER = 'test.games.12356@gmail.com'  # ここも.envにするのが理想ですが、一旦このままでOK
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ★最重要修正: env() を使って読み込む（os.getenvではない）
# .env に EMAIL_HOST_PASSWORD=abcdefghijklmnop と書かれている前提
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# デバッグ用（本番では消してください）
print("--------------------------------------------------")
print("メールパスワード読み込み確認:", EMAIL_HOST_PASSWORD)
print("--------------------------------------------------")