import os
from pathlib import Path
from typing import List, cast

import dj_database_url  # type: ignore
import environ

# 1. パスの設定
# myproject/settings/base.py から 3つ遡って プロジェクトルート (django-practice) を指定
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. django-environ の初期化
env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []))

# .env ファイルの読み込み
# 階層ズレを防ぐため、絶対パスで確実に指定
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# 3. 基本設定
SECRET_KEY = cast(str, env("SECRET_KEY", default="django-insecure-key"))  # type: ignore
DEBUG = cast(bool, env("DEBUG"))
ALLOWED_HOSTS = cast(List[str], env("ALLOWED_HOSTS"))

# --- 本番環境（Render等）特有の設定 ---
if os.environ.get("RENDER"):
    DEBUG = False
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        ALLOWED_HOSTS.append(render_host)

    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# --- アプリケーション定義 ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "shop",  # ここを shop に統一
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

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
                "shop.context_processors.cart_count_processor",  # apps.shop から修正
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

# --- データベース設定 (環境変数優先ロジック) ---
db_url = env.str("DATABASE_URL", default="")

if db_url.startswith("postgres"):
    print("🚀 DATABASE_URL detected: Using Supabase (PostgreSQL)")
    DATABASES = {
        "default": dj_database_url.config(
            default=db_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    print("🏠 DATABASE_URL not detected: Using local SQLite")
    sqlite_path = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    DATABASES = {"default": dj_database_url.config(default=sqlite_path)}

# PostgreSQL接続時は SSL を強制
if DATABASES["default"].get("ENGINE") == "django.db.backends.postgresql":
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# --- パスワードバリデーション ---
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- 国際化設定 ---
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# --- 静的ファイル設定 ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- メディアファイル設定 ---
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- 認証リダイレクト設定 ---
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "login"
