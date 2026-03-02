import os
from pathlib import Path

import dj_database_url  # type: ignore
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(DEBUG=(bool, False), ALLOWED_HOSTS=(list, []))

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")

# --- セキュリティ ベストプラクティス ---
# 1. SECRET_KEY は環境変数から読み込む（なければ適当な文字列）
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "7#n(v9&j!@*m_4$k+s2q8wz5p^r1x6u9b0y3h7t4e5g2i1o8n0a6s5d4f3g2h1j"
)
# 2. DEBUG は本番（Render）では必ず False にする
# Render(本番) または GitHub Actions(CI) のどちらかなら DEBUG = False
DEBUG = not (os.environ.get("RENDER") or os.environ.get("GITHUB_ACTIONS"))

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

if not DEBUG:
    # CIや本番環境では、Renderのドメインを許可リストに追加
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_host:
        ALLOWED_HOSTS.append(render_host)

    # セキュリティ設定を強制有効化（これで警告が消える）
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# --- アプリケーション定義 ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "apps.shop",  # ドメイン分割されたアプリ
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # パフォーマンス: 静的ファイル配信用
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
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.shop.context_processors.cart_count_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"

# --- データベース設定 (運用ベストプラクティス) ---
# DATABASE_URL 環境変数があれば Postgres、なければ SQLite
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# --- パスワードバリデーション ---
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- 国際化 (日本語設定) ---
LANGUAGE_CODE = "ja"
TIME_ZONE = "Asia/Tokyo"
USE_I18N = True
USE_TZ = True

# --- 静的ファイル設定 (WhiteNoise & 画像最適化準備) ---
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoiseによる圧縮とキャッシュ (パフォーマンス)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- メディアファイル設定 ---
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --- 認証設定 (404エラー解決用) ---
LOGIN_REDIRECT_URL = "/"  # ログイン成功時のリダイレクト先
LOGOUT_REDIRECT_URL = "/"  # ログアウト時のリダイレクト先
LOGIN_URL = "login"  # ログインが必要な時に飛ばすURL名
