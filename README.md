# 🛍️ Gemini Portfolio Shop

Django + HTMX を活用した、堅牢かつモダンな UX を持つ  
E-Commerce サイトのポートフォリオです。

UI の心地よさと、バックエンドの整合性（在庫管理・排他制御）の両立にこだわって開発しています。

---

## 🚀 主な機能と技術的ハイライト

### 1️⃣ モダンな非同期 UX（HTMX）

- **SPA 風の操作感**
  - ページ全体のリロードを避け、HTMX の OOB (Out-of-Band) Swaps を活用
- **即時フィードバック**
  - 商品追加時に「右上のカート数」と「通知メッセージ」をピンポイントで動的更新

---

### 2️⃣ 堅牢なビジネスロジック（Service Layer）

- **Thin View / Fat Service**
  - ロジックを `services.py` に集約し、保守性とテスト性を向上
- **データ不整合の防止**
  - `select_for_update` による行ロック
  - `F()` クエリによるアトミックな更新
  - `transaction.atomic()` による整合性担保

---

### 3️⃣ CI/CD & 品質管理（GitHub Actions 連携済み）

- **自動化されたパイプライン**
  - GitHub への Push 時に GitHub Actions が起動
- **品質ガードレール**
  - 以下のチェックを CI 上で自動実行
  - パスしない限りデプロイ不可

#### 🔍 CI で実行しているチェック

- Ruff（高速 Lint & コードスタイルチェック）
- mypy（厳密な型チェック）
- pytest（決済ロジックを含むユニットテスト）

#### 🛡️ エラー監視

- Sentry を導入し、本番環境での例外をリアルタイム検知

---

## 🛠️ 技術スタック

| Category        | Technology |
|----------------|------------|
| Framework      | Django 6.0 |
| Frontend       | HTMX, Pico.css, Django Template |
| Database       | PostgreSQL / SQLite |
| CI/CD          | GitHub Actions（Ruff, mypy, pytest） |
| Infrastructure | django-environ, Sentry |

---

## 🏁 セットアップ

### 開発環境の起動

```bash
# 依存関係のインストール（uv 使用）
uv sync

# マイグレーション
uv run python manage.py migrate

# サーバー起動
uv run python manage.py runserver

# GitHub Actions と同じ工程を一括実行
uv run ruff check . && \
uv run mypy . && \
uv run pytest
