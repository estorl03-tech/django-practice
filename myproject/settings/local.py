from .base import *  # noqa: F403

# --- 🚀 開発環境基本設定 (KISS原則) ---
DEBUG = True

# 🚀 ローカル環境の許可設定 (DRY原則: base.py の設定を継承しつつ拡張)
# noqa: F405 を追加して Ruff のスターインポート警告を抑制
ALLOWED_HOSTS += ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]  # noqa: F405

# デバッグツール用の内部IP設定
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# --- 📦 静的ファイル & ストレージ設定 (Django 6.0.2 準拠) ---
# 開発時は WhiteNoise を通さず、標準の StaticFilesStorage を使用して即時反映
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

# 🚀 メディアファイルのローカル優先設定 (オプション)
# 開発中に Cloudinary へのアップロードを避けたい場合は以下のコメントアウトを外す
# STORAGES["default"] = { # noqa: F405
#     "BACKEND": "django.core.files.storage.FileSystemStorage",
# }

# --- 🔒 セキュリティ設定の緩和 (ローカル開発用) ---
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# --- 📧 メール設定 (12-factor app) ---
# 開発中は実際にメールを送らず、ターミナルに内容を表示
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- 🛰️ データベース設定 ---
# DATABASE_URL が未設定の場合は base.py のロジックにより SQLite が使用されます
