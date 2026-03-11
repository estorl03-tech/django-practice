import os

import dj_database_url

from .base import *  # noqa: F403

# --- 🚀 本番環境基本設定 ---
DEBUG = False

# Render ホストの許可設定
ALLOWED_HOSTS = [".onrender.com", "localhost", "127.0.0.1"]
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_host:
    ALLOWED_HOSTS.append(render_host)

# --- 🛠️ MIDDLEWARE 設定 (WhiteNoise 挿入) ---
try:
    # SecurityMiddleware の直後（通常はインデックス1）に WhiteNoise を挿入
    if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:  # noqa: F405
        MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
except NameError, AttributeError:
    # base.py で定義されていない場合の安全なフォールバック
    pass

# --- 📦 静的ファイル & ストレージ設定 (Django 6.0.2 準拠) ---
# base.py の設定を本番用に最適化
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        # 本番環境では圧縮とキャッシュを有効化
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ホワイトノイズの詳細設定
WHITENOISE_MANIFEST_STRICT = False

# --- 🛰️ データベース設定 ---
# conn_max_age で接続を維持し、Supabase への再接続オーバーヘッドを軽減
DATABASES["default"] = dj_database_url.config(  # noqa: F405
    conn_max_age=600, conn_health_checks=True, ssl_require=True
)

# --- 🔒 セキュリティ設定 (Render/HTTPS プロキシ対応) ---
# 12-factor app に基づき、プロキシ背後での HTTPS 認識を確実にする
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS 設定 (ブラウザに HTTPS 強制を指示)
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# その他のセキュリティヘッダー
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# --- ☁️ Cloudinary 設定 ---
# 既に base.py で env.str() により取得されているが、環境変数から直接上書きも可能
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}
