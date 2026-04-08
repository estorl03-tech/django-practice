import os
from typing import Any, Dict, cast

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403

# 本番環境の基本設定
DEBUG = False

if not SECRET_KEY or SECRET_KEY == "django-insecure-key":  # noqa: F405
    raise ImproperlyConfigured("SECRET_KEY must be set in production.")

# Render ホストの許可設定
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)

# MIDDLEWARE 設定
try:
    # SecurityMiddleware の直後に WhiteNoise を挿入
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
except (NameError, AttributeError):
    pass

# 静的ファイルとストレージ設定
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        # Cloudinary の FileNotFound エラー回避のため、
        # 圧縮を行わない標準の WhiteNoise ストレージを使う
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

# データベース設定
db_config = cast(
    Dict[str, Any],
    dj_database_url.config(  # noqa: F405
        # Render free + Supabase pooler では長寿命接続が stale になりやすいため、
        # リクエストごとに接続を開き直す寄りの設定にする。
        conn_max_age=0,
        conn_health_checks=True,
        ssl_require=True,
    ),
)
DATABASES["default"] = db_config  # noqa: F405

# セキュリティ設定
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Cloudinary 設定
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

# 互換性維持のための設定
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
