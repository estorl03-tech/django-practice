from .base import *  # noqa: F403

# --- 🚀 開発環境基本設定 (KISS原則) ---
# 開発時は詳細なエラーメッセージを表示
DEBUG = True

# 🚀 ローカル環境の許可設定 (DRY原則: base.py の設定を継承しつつ拡張)
# 0.0.0.0 を含めることで、同一ネットワーク内のスマホ等からの実機確認を容易にします
ALLOWED_HOSTS += ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]

# --- 📦 静的ファイル & ストレージ設定 (Django 6.0.2 準拠) ---
# 開発時は WhiteNoise の圧縮機能を無効化し、ファイルの変更を即座に反映
# これにより collectstatic を回す手間を省きます (KISS)
STORAGES["staticfiles"] = {  # noqa: F405
    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
}

# --- 🔒 セキュリティ設定の緩和 (ローカル開発用) ---
# 本番用の設定（HTTPS強制など）をオフにし、ローカルでのログイン不可問題を回避
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# --- 📧 メール設定 (12-factor app) ---
# 開発中は実際にメールを送らず、ターミナルに内容を表示
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# --- 🛰️ データベース設定 ---
# DATABASE_URL が未設定の場合は base.py のロジックにより SQLite が使用されます
