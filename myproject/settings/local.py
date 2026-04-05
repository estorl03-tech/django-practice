from .base import *  # noqa: F403

# 開発環境の基本設定
DEBUG = True

# base.py の設定を継承しつつローカル向けに拡張する
ALLOWED_HOSTS += ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]  # noqa: F405

# デバッグツール用の内部IP設定
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# 静的ファイルとストレージ設定
# 開発時は WhiteNoise を通さず、標準の StaticFilesStorage を使う
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

# ローカルでファイル保存したい場合は以下を有効にする
# STORAGES["default"] = { # noqa: F405
#     "BACKEND": "django.core.files.storage.FileSystemStorage",
# }

# ローカル開発用のセキュリティ設定
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# メール設定
# 開発中は実際にメールを送らず、ターミナルに内容を表示する
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# データベース設定
# DATABASE_URL が未設定の場合は base.py のロジックにより SQLite を使う
