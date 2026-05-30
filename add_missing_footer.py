#!/usr/bin/env python3
"""
フッターが無いページにフッターを追加し、著者名も挿入する
"""
import os
import re
import glob

TEMPLATES_DIR = "templates"

FOOTER_HTML = """
<footer>
  <nav class="footer-nav">
    <div class="footer-nav-group">
      <span class="footer-nav-label">🪲 種別ガイド</span>
      <a href="/guide/miyama">ミヤマクワガタ</a>
      <a href="/guide/nokogiri">ノコギリクワガタ</a>
      <a href="/guide/hirata">ヒラタクワガタ</a>
      <a href="/guide/ookuwa">オオクワガタ</a>
      <a href="/guide/kokuwagata">コクワガタ</a>
      <a href="/guide/akaashi">アカアシクワガタ</a>
      <a href="/guide/kabuto">カブトムシ</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">📅 月別ガイド</span>
      <a href="/guide/may">5月の採集</a>
      <a href="/guide/june">6月の採集</a>
      <a href="/guide/july">7月の採集</a>
      <a href="/guide/august">8月の採集</a>
      <a href="/guide/september">9月の採集</a>
      <a href="/guide/october">10月の採集</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">📖 採集テクニック</span>
      <a href="/guide/night">夜間採集のコツ</a>
      <a href="/guide/morning">早朝採集のコツ</a>
      <a href="/guide/trap">トラップ採集</a>
      <a href="/guide/light">灯火採集</a>
      <a href="/guide/tree">樹液の出る木</a>
      <a href="/guide/spot">採集スポットの探し方</a>
      <a href="/guide/tools">採集道具リスト</a>
      <a href="/guide/beginners">初心者向けガイド</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">🗾 都道府県ガイド</span>
      <a href="/guide/pref/tokyo">東京都</a>
      <a href="/guide/pref/kanagawa">神奈川県</a>
      <a href="/guide/pref/saitama">埼玉県</a>
      <a href="/guide/pref/chiba">千葉県</a>
      <a href="/guide/pref/osaka">大阪府</a>
      <a href="/guide/pref/aichi">愛知県</a>
      <a href="/guide/pref/hokkaido">北海道</a>
      <a href="/guide/pref">全都道府県一覧</a>
    </div>
  </nav>
  <div class="footer-bottom">
    <p style="margin:0 0 6px;font-size:.76rem;color:#5a8a5a">
      ✍️ 監修・執筆：<a href="/about" style="color:#81c784">森山春樹</a>（クワガタ採集歴20年以上 ／ 全国47都道府県フィールド経験）
    </p>
    <a href="/">クワガタ採集スポット検索 beetle-finder</a> ｜
    <a href="/app">🗺 スポット検索</a> ｜
    <a href="/guide">📖 ガイド一覧</a> ｜
    <a href="/about">サービスについて</a> ｜
    <a href="/privacy">プライバシーポリシー</a> ｜
    <a href="/terms">利用規約</a>
  </div>
</footer>"""

FOOTER_CSS = """  footer{background:#1b2d1b;color:#81c784;padding:28px 16px 16px;font-size:.78rem;margin-top:40px}
  .footer-nav{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:20px;max-width:800px;margin:0 auto 20px;padding:0 0 20px;border-bottom:1px solid #2e4e2e}
  .footer-nav-group{display:flex;flex-direction:column;gap:6px}
  .footer-nav-label{color:#a5d6a7;font-weight:700;font-size:.8rem;margin-bottom:2px}
  .footer-nav a{color:#81c784;text-decoration:none;font-size:.78rem;line-height:1.6}
  .footer-nav a:hover{color:#fff;text-decoration:underline}
  .footer-bottom{text-align:center;color:#4a7a4a}
  .footer-bottom a{color:#81c784}"""

# フッター無しのターゲット
targets = [f for f in sorted(glob.glob(os.path.join(TEMPLATES_DIR, "guide_pref_*.html")))
           if '<footer>' not in open(f, encoding='utf-8').read()]

# 非prefページのスキップ分
other_skipped = [
    "templates/guide_case.html",
    "templates/guide_scoring.html",
    "templates/landing.html",
]
targets += [f for f in other_skipped if os.path.exists(f) and '<footer>' not in open(f, encoding='utf-8').read()]

updated = 0
skipped = 0

for filepath in targets:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if '<footer>' in content:
        print(f"⏭️  既存フッター: {os.path.basename(filepath)}")
        continue

    # CSSにフッタースタイルが無ければ追加
    if 'footer-nav' not in content:
        content = content.replace('</style>', FOOTER_CSS + '\n</style>', 1)

    # <script> の前 (</div>\n\n<script> や </div>\n<script> など) にフッターを挿入
    # パターン: 最後の </div> の後ろ、<script> の前
    inserted = False

    # パターン1: </div>\n\n<script>
    m = re.search(r'(</div>)\s*\n\s*(<script>)', content)
    if m:
        pos = m.start(2)
        content = content[:pos] + FOOTER_HTML + '\n\n' + content[pos:]
        inserted = True

    if not inserted:
        # パターン2: </div>\n</body>
        m = re.search(r'(</div>)\s*\n\s*(</body>)', content)
        if m:
            pos = m.start(2)
            content = content[:pos] + FOOTER_HTML + '\n\n' + content[pos:]
            inserted = True

    if inserted:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        updated += 1
        print(f"✅ {os.path.basename(filepath)}")
    else:
        skipped += 1
        print(f"⚠️  スキップ: {os.path.basename(filepath)}")

print(f"\n完了: {updated} 件更新 / {skipped} 件スキップ")
