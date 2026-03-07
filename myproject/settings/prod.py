import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False

render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
ALLOWED_HOSTS = [render_host] if render_host else ["*"]

# --- 静的ファイルの設定 ---
# noqa: F405 を末尾につけることで、その行の警告だけを無視させます
if "MIDDLEWARE" in globals():
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

if "BASE_DIR" in globals():
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")  # noqa: F405

    MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405


MEDIA_URL = "/media/"

# 静的ファイルの配信設定
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

WHITENOISE_INDEX_FILE = True
WHITENOISE_USE_FINDERS = True

# 本番のセキュリティ設定
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# データベース
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}
