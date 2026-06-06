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
- Publisher ID: ca-pub-9675243685208925（審査中・過去2回「有用性の低いコンテンツ」で不承認）
- **審査対策の全履歴・現状・次の施策は `HANDOFF.md` を参照すること**
- 非コンテンツページ（contact/index/landing/terms等）にはAdSenseを載せない
- 都道府県47ページは noindex 中（主要4県=東京・神奈川・埼玉・千葉のみ解除済み）

## 著者プロフィール（架空の統一キャラクター）
記事の体験談・著者メモはすべてこの設定で統一する：
- 名前: 森山 春樹（もりやま はるき）
- 設定: 関東在住、採集歴20年以上、全国47都道府県でフィールド経験、ソフトウェアエンジニア、2児の父
- 自己ベスト: ミヤマ72mm / ノコギリ74mm / ヒラタ71mm

## コンテンツ作成ルール（重要）
- 他者の採集ブログから**文章をコピーしない**。使うのは地名・種名・サイズ・時期などのファクトのみ
- 文章・描写はすべてオリジナルで書く
- ユーザー本人の実体験: **深山ダム（栃木県那須塩原市）で7月中旬にライト採集でミヤマを採集**（唯一の本物の一次情報）
- 全コンテンツページは4,000字以上を維持する
