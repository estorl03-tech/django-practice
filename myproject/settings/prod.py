import os

import dj_database_url

from .base import *  # noqa: F403

DEBUG = False

render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
ALLOWED_HOSTS = [render_host] if render_host else ["*"]

# 本番のセキュリティ設定 (Custom指示通り)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# データベース (DATABASE_URL から Postgres を取得)
DATABASES = {"default": dj_database_url.config(conn_max_age=600)}
