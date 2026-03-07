import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False

# 接続エラーを防ぐためすべて許可
ALLOWED_HOSTS = ["*"]

# --- 静的ファイル・メディアファイルの設定 ---
# MIDDLEWAREの存在を確認しつつ挿入（Ruff警告対策済み）
if "MIDDLEWARE" in globals():
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

if "BASE_DIR" in globals():
    # 静的ファイルとメディアのルート設定
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405

    # WhiteNoiseにmediaフォルダをスキャンさせる（ここが画像表示の鍵）
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "media"),  # noqa: F405
    ]

MEDIA_URL = "/media/"

# 静的ファイルの圧縮・配信設定
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 本番環境でメディアファイルを配信するためのスイッチ
WHITENOISE_INDEX_FILE = True
WHITENOISE_USE_FINDERS = True

# セキュリティ設定：RenderのSSLと衝突しないようFalse
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# データベース設定
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}
