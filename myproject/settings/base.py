import os
from pathlib import Path
from typing import Any, Dict, List

import dj_database_url  # type: ignore
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# 1. パスの設定 (uv 環境のプロジェクト構造)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. django-environ の初期設定 (Python 3.14.3 / Django 6.0.2 準拠)
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    SENTRY_DSN=(str, ""),
    SECRET_KEY=(str, "django-insecure-key"),
    DATABASE_URL=(str, ""),
    # Cloudinary 用のデフォルト設定を追加
    CLOUDINARY_CLOUD_NAME=(str, ""),
    CLOUDINARY_API_KEY=(str, ""),
    CLOUDINARY_API_SECRET=(str, ""),
)

# .env ファイルの読み込み (12-factor app)
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# --- 🚀 Sentry の初期化 (省略なし) ---
SENTRY_DSN: str = env.str("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
    print("✅ Sentry is active")
else:
    print("⚠️ SENTRY_DSN not found: Sentry is disabled")

# 3. 基本設定
SECRET_KEY: str = env.str("SECRET_KEY")
DEBUG: bool = env.bool("DEBUG")
ALLOWED_HOSTS: List[str] = env.list("ALLOWED_HOSTS")

# --- 本番環境（Render等）特有の設定 ---
if os.environ.get("RENDER"):
    DEBUG = False

    ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", ".onrender.com"])

    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        ALLOWED_HOSTS.append(render_host)

    # セキュリティ ベストプラクティス
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"

# --- アプリケーション定義 (モジュラモノリス設計) ---
INSTALLED_APPS = [
    "cloudinary_storage",  # staticfiles より前に配置（KISS原則）
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",  # 追加
    "django.contrib.humanize",
    "shop",
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
                "shop.context_processors.cart_count_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

# --- 🛰️ データベース設定 (Supabase 接続強制ロジック) ---
db_url_env: str = env.str("DATABASE_URL")
if db_url_env and db_url_env.startswith("postgres"):
    print("🚀 DATABASE_URL detected: Using Supabase (PostgreSQL)")
    DATABASES: Dict[str, Any] = {
        "default": dj_database_url.config(
            default=db_url_env,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
else:
    print("🏠 DATABASE_URL not detected: Using local SQLite")
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Cloudinary 設定 (12-factor app) ---
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env.str("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env.str("CLOUDINARY_API_KEY"),
    "API_SECRET": env.str("CLOUDINARY_API_SECRET"),
}

# --- 静的ファイル & メディアファイル設定 (Django 6.0 準拠) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STORAGES = {
    "default": {
        # メディアファイルを Cloudinary に向ける
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True
WHITENOISE_KEEP_FILES_ON_DISK = True

# --- 国際化・パスワード設定 (省略なし) ---
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": ("django.contrib.auth.password_validation.UserAttributeSimilarityValidator")},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- 認証リダイレクト設定 ---
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "login"
