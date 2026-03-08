import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]

# --- MIDDLEWARE設定 (WhiteNoiseの挿入) ---
try:
    # Python 3 の正しい例外キャッチ構文に修正
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
except NameError, AttributeError:
    # MIDDLEWAREが定義されていない場合のフォールバック
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
    ]

# --- 静的ファイル設定 (BASE_DIRの安全な取得) ---
# globals()から取得し、パス計算でのエラーを物理的に防ぎます
current_base_dir = globals().get("BASE_DIR")

if current_base_dir:
    STATIC_ROOT = os.path.join(current_base_dir, "staticfiles")
    # ls で確認した static フォルダを読み込み対象にします
    STATICFILES_DIRS = [os.path.join(current_base_dir, "static")]
    # ストレージ設定
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# データベース設定
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# セキュリティ設定
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
