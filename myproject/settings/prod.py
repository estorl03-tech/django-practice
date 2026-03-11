import os
from typing import Any, Dict, cast

import dj_database_url

from .base import *  # noqa: F403

# --- 🚀 本番環境基本設定 (12-factor app) ---
DEBUG = False

# Render ホストの許可設定
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)

# --- 🛠️ MIDDLEWARE 設定 (WhiteNoise 挿入) ---
try:
    # SecurityMiddleware の直後に WhiteNoise を挿入
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
except NameError, AttributeError:
    # Python 3 の正しい例外キャッチ構文に修正
    pass

# --- 📦 静的ファイル & ストレージ設定 (Django 6.0.2 準拠) ---
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        # 🚀 修正: Cloudinary の FileNotFound エラーを回避するため、
        # 圧縮処理を行わない標準の WhiteNoise ストレージを使用
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

# ホワイトノイズの詳細設定
WHITENOISE_MANIFEST_STRICT = False
# 静的ファイル探索を有効化
WHITENOISE_USE_FINDERS = True

# --- 🛰️ データベース設定 (Pylance 型エラー対策済み) ---
# cast を使用して DBConfig 型を Dict[str, Any] へ明示的に変換
db_config = cast(
    Dict[str, Any],
    dj_database_url.config(  # noqa: F405
        conn_max_age=600, conn_health_checks=True, ssl_require=True
    ),
)
DATABASES["default"] = db_config  # noqa: F405

# --- 🔒 セキュリティ設定 (Render/HTTPS プロキシ対応) ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- ☁️ Cloudinary 設定 ---
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

# --- 🛰️ 互換性維持のための設定 (Cloudinary ライブラリ対策) ---
# 厳格な Manifest（圧縮）を避け、標準の配信ストレージを指定
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
