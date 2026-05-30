#!/usr/bin/env python3
"""
全ガイドページのフッターに著者名「森山春樹」を追加する
footer-bottom の著作権行の前に著者情報を挿入
"""
import os
import re
import glob

TEMPLATES_DIR = "templates"

# 対象ファイル（全ガイドページ）
TARGETS = sorted(
    glob.glob(os.path.join(TEMPLATES_DIR, "guide*.html"))
    + glob.glob(os.path.join(TEMPLATES_DIR, "landing.html"))
)

# 著者行を追加する位置: </div>\n</footer> の直前の footer-bottom 内
OLD_FOOTER_BOTTOM = """  <div class="footer-bottom">
    <a href="/">クワガタ採集スポット検索 beetle-finder</a> ｜
    <a href="/app">🗺 スポット検索</a> ｜
    <a href="/guide">📖 ガイド一覧</a> ｜
    <a href="/about">サービスについて</a> ｜
    <a href="/privacy">プライバシーポリシー</a> ｜
    <a href="/terms">利用規約</a>
  </div>
</footer>"""

NEW_FOOTER_BOTTOM = """  <div class="footer-bottom">
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

updated = 0
skipped = 0
already = 0

for filepath in TARGETS:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if "森山春樹" in content and "footer-bottom" in content and "監修・執筆" in content:
        already += 1
        continue

    if OLD_FOOTER_BOTTOM in content:
        new_content = content.replace(OLD_FOOTER_BOTTOM, NEW_FOOTER_BOTTOM)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        updated += 1
        print(f"✅ {os.path.basename(filepath)}")
    else:
        # フォールバック: </footer> 直前の </div> の前に挿入を試みる
        # footer-bottomブロックを正規表現で探す
        pattern = r'(<div class="footer-bottom">)(.*?)(</div>\s*</footer>)'
        match = re.search(pattern, content, re.DOTALL)
        if match and "監修・執筆" not in content:
            author_line = '    <p style="margin:0 0 6px;font-size:.76rem;color:#5a8a5a">\n      ✍️ 監修・執筆：<a href="/about" style="color:#81c784">森山春樹</a>（クワガタ採集歴20年以上 ／ 全国47都道府県フィールド経験）\n    </p>\n'
            new_inner = author_line + match.group(2)
            new_content = content[:match.start(2)] + new_inner + content[match.start(3):]
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1
            print(f"✅ (regex) {os.path.basename(filepath)}")
        else:
            skipped += 1
            print(f"⚠️  スキップ: {os.path.basename(filepath)}")

print(f"\n完了: {updated} 件更新 / {already} 件既存 / {skipped} 件スキップ")
