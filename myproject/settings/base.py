from pathlib import Path
from typing import Any, Dict

import dj_database_url  # type: ignore
import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

# --- 1. パスの設定 (uv 環境: settings/base.py から 3つ上がプロジェクトルート) ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- 2. django-environ の初期設定 (12-factor app) ---
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    SENTRY_DSN=(str, ""),
    SECRET_KEY=(str, "django-insecure-key"),
    DATABASE_URL=(str, ""),
    CLOUDINARY_CLOUD_NAME=(str, ""),
    CLOUDINARY_API_KEY=(str, ""),
    CLOUDINARY_API_SECRET=(str, ""),
)

# .env ファイルの読み込み (ローカル開発用)
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# --- 🚀 Sentry の初期化 (エラー追跡) ---
SENTRY_DSN: str = env.str("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
    print("✅ Sentry is active")

# --- 3. 基本設定 ---
SECRET_KEY = env.str("SECRET_KEY")
DEBUG = env.bool("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# --- アプリケーション定義 ---
INSTALLED_APPS = [
    "cloudinary_storage",  # staticfiles より前に配置 (重要)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",
    "django.contrib.humanize",
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # SecurityMiddleware の直後
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

# --- 🛰️ データベース設定 ---
db_url_env = env.str("DATABASE_URL")
if db_url_env and db_url_env.startswith("postgres"):
    DATABASES: Dict[str, Any] = {
        "default": dj_database_url.config(
            default=db_url_env,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- ☁️ Cloudinary 設定 ---
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env.str("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env.str("CLOUDINARY_API_KEY"),
    "API_SECRET": env.str("CLOUDINARY_API_SECRET"),
}

# --- 📦 静的ファイル & ストレージ設定 (Django 6.0 準拠) ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        # デフォルト設定。本番 (prod.py) で WhiteNoise ストレージに上書きされる
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# --- 🛰️ 互換性維持のための設定 (Cloudinary ライブラリ対策) ---
# django-cloudinary-storage が内部で古い変数を参照するための回避策
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

# --- 国際化・パスワード設定 ---
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 認証リダイレクト設定
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "login"
