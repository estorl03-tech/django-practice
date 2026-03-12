# ✨ Gemini Portfolio Shop

**「KISS原則を核とし、実務的な堅牢性を追求した Django 6.0 × HTMX ECポートフォリオ」**

本プロジェクトは、最新の **Python 3.14.3** と **Django 6.0** をベースに、「バックエンドエンジニアがいかにしてフロントエンドの複雑性を制御し、データの整合性を守るか」をテーマに構築したECサイト・ポートフォリオです。

## 🚀 Demo
- **URL**: [https://django-ec-portfolio.onrender.com](https://django-ec-portfolio.onrender.com)
- **Guest Account**: 
  - ID: `guest_user` / Pass: `guest_password123`
  - ※ログイン後、カート操作から注文完了までのフローをスムーズに確認いただけます。

---

## 🛠️ Tech Stack

### **Core Stack**
- **Framework**: Python 3.14.3 / Django 6.0.2
- **Frontend**: HTMX 2.0 / Pico CSS 2.1.1 (No-build, Semantic UI)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Cloudinary (Image management)
- **Monitoring**: Sentry
- **Package Manager**: **uv** (Next-generation Python tool)

### **Quality & Automation**
- **CI/CD**: GitHub Actions (Lint, Type Check, Test, Deploy)
- **Static Analysis**: **Ruff** (Lint/Format), **Mypy** (Strict Type Check)
- **Testing**: Pytest / Django Test

---

## 📈 Performance & Web Vitals
本プロジェクトは、JSランタイムを最小限に抑えた設計により、モバイル環境でも極めて高いパフォーマンスを記録しています。

![PageSpeed Insights Score](./image_6ec4ba.png)

- **Performance: 94** / **Accessibility: 98** / **Best Practices: 100** / **SEO: 91**
- **No-JS Framework**: HTMXを採用し、巨大なJavaScriptの読み込みと実行オーバーヘッドを排除。
- **Image Optimization**: CloudinaryによるWebP自動変換とCDN配信。

---

## ✨ 3-Layered Engineering (実装のこだわり)

単に「動く」だけでなく、以下の3層でデータの整合性とUXを担保しています。

### 1. Model層：DBレベルでの防衛線
- **CheckConstraint**: `models.py` にて価格と在庫が負の値にならないようDBレベルで制約を付与。
- **Price Snapshot**: 注文時の価格を `OrderItem` に保存し、将来の価格改定による過去データの不整合を防止。

### 2. Service層：ビジネスロジックの集約
- **Atomic Transactions**: `transaction.atomic` による注文・在庫更新の完全な一貫性保証。
- **Concurrency Control**: `select_for_update()` による行ロックと、`F()` クエリによるDB直結の在庫減算ロジックを実装。

### 3. View層：HTMXによる軽量SPA体験
- **OOB (Out-of-Band) Swap**: `hx-swap-oob` を活用。一回のリクエストで「カートバッジ」「在庫表示」「メッセージ」を同時更新。
- **Security**: `@login_required` や所有権チェック (`filter(user=request.user)`) をViewレベルで徹底。

---

## 📦 Local Setup (using uv)

```bash
# クローン
git clone [https://github.com/estorl03-tech/django-practice](https://github.com/estorl03-tech/django-practice)
cd django-practice

# uvによる環境構築
uv sync

# マイグレーション & サーバー起動
uv run python manage.py migrate
uv run python manage.py runserver
```

信頼性への取り組み
uv/Ruff/Mypy: 開発環境の標準化と、静的解析による品質維持。

12-factor app: 環境変数による設定分離とステートレスな設計（KISS原則）。

CI/CD: 品質チェックをパスしなければデプロイされない安全なリリースサイクル。
