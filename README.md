Gemini Portfolio ShopDjango + HTMX を活用した、堅牢かつモダンな UX を持つ E-Commerce サイトのポートフォリオです。UI の心地よさと、バックエンドの整合性（在庫管理・排他制御）の両立にこだわって開発しています。🚀 主な機能と技術的ハイライト1. モダンな非同期 UX (HTMX)SPA 風の操作感: ページ全体のリロードを避け、HTMX の OOB (Out-of-Band) Swaps を活用。即時フィードバック: 商品追加時に「右上のカート数」と「通知メッセージ」をピンポイントで動的更新。2. 堅牢なビジネスロジック (Service Layer)Thin View / Fat Service: ロジックを services.py に集約し、保守性とテスト性を向上。データ不整合の防止: select_for_update による行ロック、F クエリによるアトミックな更新、transaction.atomic() による整合性担保。3. CI/CD & 品質管理（GitHub Actions 連携済み）自動化されたパイプライン: GitHub への Push 時に GitHub Actions が起動。品質ガードレール: 以下のチェックを CI 上で自動実行し、パスしない限りデプロイを許可しない運用。Ruff: コードスタイルと高速 Lintmypy: 厳密な型チェックpytest: 決済ロジックを含む全ユニットテストエラー監視: Sentry を導入し、本番環境での例外をリアルタイム検知。🛠️ 技術スタックCategoryTechnologyFrameworkDjango 6.0FrontendHTMX, Pico.css, Jinja2 (Django Template)DatabasePostgreSQL / SQLiteCI/CDGitHub Actions (Ruff, mypy, pytest)Infrastructuredjango-environ, Sentry🏁 セットアップとテスト実行開発環境の起動Bash# 依存関係のインストール (uv使用)
uv sync

# マイグレーションとサーバー起動
uv run python manage.py migrate
uv run python manage.py runserver
CI/CD 同等の品質チェック（ローカル）Bash# GitHub Actions と同じ工程を一括実行
uv run ruff check . && uv run mypy . && uv run pytest
📝 開発上のこだわり実務レベルの品質管理: GitHub Actions による CI 環境を構築し、常にテストをパスしたコードのみを管理。型エラーの排除: Pylance/mypy で型エラーを 0 に抑え込み。運用意識: Sentry による監視、環境変数の分離など、本番運用に耐えうる構成。

