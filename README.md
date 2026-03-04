# Gemini Portfolio Shop

Django + HTMX を活用した、堅牢かつモダンな UX を持つ E-Commerce サイトのポートフォリオです。
UI の心地よさと、バックエンドの整合性（在庫管理・排他制御）の両立にこだわって開発しています。

## 🚀 主な機能と技術的ハイライト

### 1. モダンな非同期 UX (HTMX)
- **SPA 風の操作感**: ページ全体のリロードを避け、HTMX の **OOB (Out-of-Band) Swaps** を活用。
- **即時フィードバック**: 商品追加時に「右上のカート数」と「通知メッセージ」をピンポイントで動的更新。
- **洗練された UI**: Pico.css をベースにし、CSS 変数を活用した一貫性のあるデザイン。

### 2. 堅牢なビジネスロジック (Service Layer)
- **Thin View / Fat Service**: ビジネスロジックを `services.py` に集約し、保守性とテスト性を向上。
- **データ不整合の防止**: 
  - `select_for_update` による行ロックを行い、同時購入時の在庫崩れを防止。
  - `F` クエリによるアトミックな数値更新を実装。
  - `transaction.atomic()` による注文処理の完全な整合性担保。

### 3. プロフェッショナルな品質管理
- **静的解析**: `Ruff` による高速な lint/format 管理。
- **型安全性**: `mypy` (Strict 寄り) と Pylance を組み合わせた厳密な型定義。
- **自動テスト**: `pytest-django` を採用。正常系・異常系・複数商品注文など、決済の心臓部をテストで保護。
- **エラー監視**: `Sentry` を導入し、本番環境での例外検知を自動化。

## 🛠️ 技術スタック

| Category | Technology |
| :--- | :--- |
| **Framework** | Django 6.0 |
| **Frontend** | HTMX, Pico.css, Jinja2 (Django Template) |
| **Database** | PostgreSQL / SQLite |
| **Quality** | Ruff, mypy, pytest, pytest-django |
| **Infrastructure** | Environment Variables (django-environ), Sentry |

## 🏁 セットアップとテスト実行

### 開発環境の起動
```bash
# 依存関係のインストール (uv使用)
uv sync

# マイグレーションとサーバー起動
uv run python manage.py migrate
uv run python manage.py runserver

# 全チェック一括実行
uv run ruff check . && uv run mypy . && uv run pytest
