# beetle-finder プロジェクト設定

## 自動デプロイ（必須）
**コード変更を行ったら、必ずその場でGitHubにpushすること。**

変更後は以下を自動実行する：
```bash
git add <変更ファイル>
git commit -m "変更内容の説明"
git push origin main
```

- pushするとRender.comが自動検知してデプロイする（2〜5分）
- ユーザーに確認を取らずそのままpushしてよい

## プロジェクト概要
- Flask製クワガタ採集スポット検索アプリ
- 本番URL: https://beetle-finder.onrender.com
- GitHub: https://github.com/0515naokit-sketch/beetle-finder
- ホスティング: Render.com（mainブランチへのpushで自動デプロイ）

## 起動方法
- プレビュー: `.claude/launch.json` の "beetle-finder" 設定を使用
- ポート: 5000
- テンプレートキャッシュ対策: FLASK_DEBUG=true 設定済み

## 主なファイル
- `app.py` — Flaskルート・APIエンドポイント
- `templates/index.html` — メイン検索アプリ画面（大型ファイル）
- `templates/contact.html` — お問い合わせページ
- `templates/landing.html` — トップページ
- `templates/guide*.html` — 採集ガイド記事群

## デザイン方針
- ファミリー向け明るいライトテーマ（白・薄緑ベース）
- ヘッダー: グリーングラデーション（#2e7d32 → #43a047）
- ブランドカラー: #2e7d32（ダークグリーン）、#4caf50（グリーン）
- モバイル: ボトムシート型（地図ファースト）

## Google Analytics
- ID: G-D50YSSYFKN

## Amazon Associates
- タグ: beetlefinder-22

## AdSense
- Publisher ID: ca-pub-9675243685208925（審査中）
