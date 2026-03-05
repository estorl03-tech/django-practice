# myproject/settings/local.py
from .base import *  # noqa: F403 # base.py の全設定を読み込む [cite: 2026-02-21]

DEBUG = True  # 🚀 開発時は必ず True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # 🚀 ローカル環境を許可 [cite: 2026-02-21]
