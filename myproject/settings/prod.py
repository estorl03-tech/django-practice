import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False
ALLOWED_HOSTS = ["*"]

# --- 静的ファイル・配信設定 ---
# Ruffの警告(F405)を抑制しつつMIDDLEWAREにWhiteNoiseを挿入
try:
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
except NameError:
    # MIDDLEWAREが定義されていない場合の安全策
    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.middleware.common.CommonMiddleware",
    ]

if "BASE_DIR" in globals() or "BASE_DIR" in locals():
    # 配信用の集約先
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405

    # 修正：'static' フォルダを読み込ませる
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),  # noqa: F405
    ]

# 配信用のストレージ設定
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# データベース設定
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}

# セキュリティ設定
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
