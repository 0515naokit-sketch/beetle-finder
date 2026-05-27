"""
add_moshimo_links.py
────────────────────────────────────────────────────────────────
もしもアフィリエイトリンク（楽天・Amazon・Yahoo!）を
都道府県ページに一括追加するスクリプト。

対象：guide_pref_*.html のうち rec-rkt / moshimo リンクがないページ
挿入位置：<h2 class="section">🔗 関連ガイド</h2> の直前
"""

import os
import re
import glob

TEMPLATES_DIR = "templates"

# ── もしも どこでもリンク のURLビルダー ───────────────────────────────────
def amz(keyword):
    kw = keyword.replace(' ', '+')
    return f"https://www.amazon.co.jp/s?k={kw}&tag=beetlefinder-22"

def rkt(keyword):
    import urllib.parse
    kw = urllib.parse.quote(keyword)
    return (f"https://af.moshimo.com/af/c/click?a_id=5563442&p_id=54&pc_id=54"
            f"&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{kw}%2F")

def yah(keyword):
    import urllib.parse
    kw = urllib.parse.quote(keyword)
    return (f"https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925"
            f"&pl_id=19142&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3D{kw}")

# ── 商品ブロックHTML ────────────────────────────────────────────────────────
BLOCK = """\
  <h2 class="section">🛒 採集・飼育おすすめグッズ</h2>
  <div class="amz-box">
    <div class="amz-box-title">🔦 夜間採集の必需品</div>
    <div class="amz-links">
      <a href="{amz_light}" target="_blank" rel="noopener sponsored" class="amz-btn">ヘッドライト(Amazon)</a>
      <a href="{rkt_light}" target="_blank" rel="noopener sponsored" class="rkt-btn">ヘッドライト(楽天)</a>
      <a href="{yah_light}" target="_blank" rel="noopener sponsored" class="yah-btn">ヘッドライト(Yahoo!)</a>
    </div>
    <div class="amz-links" style="margin-top:8px">
      <a href="{amz_net}" target="_blank" rel="noopener sponsored" class="amz-btn">虫取り網(Amazon)</a>
      <a href="{rkt_net}" target="_blank" rel="noopener sponsored" class="rkt-btn">虫取り網(楽天)</a>
      <a href="{yah_net}" target="_blank" rel="noopener sponsored" class="yah-btn">虫取り網(Yahoo!)</a>
    </div>
    <div class="amz-box-title" style="margin-top:14px">🪲 飼育グッズ</div>
    <div class="amz-links">
      <a href="{amz_case}" target="_blank" rel="noopener sponsored" class="amz-btn">飼育ケース(Amazon)</a>
      <a href="{rkt_case}" target="_blank" rel="noopener sponsored" class="rkt-btn">飼育ケース(楽天)</a>
      <a href="{yah_case}" target="_blank" rel="noopener sponsored" class="yah-btn">飼育ケース(Yahoo!)</a>
    </div>
    <div class="amz-links" style="margin-top:8px">
      <a href="{amz_mat}" target="_blank" rel="noopener sponsored" class="amz-btn">昆虫マット(Amazon)</a>
      <a href="{rkt_mat}" target="_blank" rel="noopener sponsored" class="rkt-btn">昆虫マット(楽天)</a>
      <a href="{yah_mat}" target="_blank" rel="noopener sponsored" class="yah-btn">昆虫マット(Yahoo!)</a>
    </div>
    <div class="amz-links" style="margin-top:8px">
      <a href="{amz_jelly}" target="_blank" rel="noopener sponsored" class="amz-btn">昆虫ゼリー(Amazon)</a>
      <a href="{rkt_jelly}" target="_blank" rel="noopener sponsored" class="rkt-btn">昆虫ゼリー(楽天)</a>
      <a href="{yah_jelly}" target="_blank" rel="noopener sponsored" class="yah-btn">昆虫ゼリー(Yahoo!)</a>
    </div>
    <p class="amz-note">※Amazon・楽天・Yahoo!のアフィリエイトプログラム参加中。クリックで価格は変わりません。</p>
  </div>

"""

# ── リンクを生成 ────────────────────────────────────────────────────────────
AFFILIATE_BLOCK = BLOCK.format(
    amz_light=amz("ヘッドライト LED 充電式 アウトドア"),
    rkt_light=rkt("ヘッドライト LED 充電式"),
    yah_light=yah("ヘッドライト LED 充電式"),
    amz_net=amz("虫取り網 伸縮式 昆虫採集"),
    rkt_net=rkt("虫取り網 伸縮式 昆虫採集"),
    yah_net=yah("虫取り網 伸縮式 昆虫採集"),
    amz_case=amz("クワガタ 飼育ケース"),
    rkt_case=rkt("クワガタ 飼育ケース"),
    yah_case=yah("クワガタ 飼育ケース"),
    amz_mat=amz("昆虫マット クワガタ カブトムシ"),
    rkt_mat=rkt("昆虫マット クワガタ"),
    yah_mat=yah("昆虫マット クワガタ"),
    amz_jelly=amz("昆虫ゼリー クワガタ カブトムシ"),
    rkt_jelly=rkt("昆虫ゼリー クワガタ"),
    yah_jelly=yah("昆虫ゼリー クワガタ"),
)

# 挿入マーカーのパターン（優先順）
INSERT_MARKERS = [
    '<h2 class="section">🔗 関連ガイド</h2>',
    '<h2 class="section">関連ガイド</h2>',
    '<h2 class="section">📖 関連ガイド</h2>',
    '<div class="cta-box">',   # fallback
]

# CSSを持つページ向け：.amz-box スタイルが未定義なら追加
AMZ_BOX_CSS = """\
    .amz-box{background:#fffbf0;border:1px solid #f0c040;border-radius:8px;padding:14px 16px;margin:20px 0}
    .amz-box-title{font-weight:700;color:#c45000;font-size:.88rem;margin-bottom:10px}
    .amz-links{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:6px}
    .amz-btn{display:inline-block;background:#ff9900;color:#fff !important;padding:7px 14px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none !important}
    .amz-btn:hover{background:#e68900 !important;color:#fff !important}
    .rkt-btn{display:inline-block;background:#bf0000;color:#fff !important;padding:7px 14px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none !important}
    .rkt-btn:hover{background:#900 !important;color:#fff !important}
    .yah-btn{display:inline-block;background:#ff0033;color:#fff !important;padding:7px 14px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none !important}
    .yah-btn:hover{background:#cc0029 !important;color:#fff !important}
    .amz-note{font-size:.7rem;color:#999;margin:0}
"""


def has_moshimo(content):
    return "moshimo" in content or "rec-rkt" in content or "rkt-btn" in content


def has_amz_box_css(content):
    return ".amz-box{" in content or ".amz-box {" in content


def process_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    if has_moshimo(content):
        return False, "skip (already has moshimo)"

    # 挿入マーカーを探す
    marker = None
    for m in INSERT_MARKERS:
        if m in content:
            marker = m
            break

    if not marker:
        return False, "skip (no marker found)"

    # CSSが未定義ならstyle内に追加
    if not has_amz_box_css(content):
        content = content.replace("</style>", AMZ_BOX_CSS + "  </style>", 1)

    # リンクブロックを挿入
    content = content.replace(marker, AFFILIATE_BLOCK + marker, 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return True, "updated"


def main():
    files = sorted(glob.glob(os.path.join(TEMPLATES_DIR, "guide_pref_*.html")))
    updated = []
    skipped = []

    for fp in files:
        ok, reason = process_file(fp)
        name = os.path.basename(fp)
        if ok:
            updated.append(name)
            print(f"  ✓ {name}")
        else:
            skipped.append((name, reason))

    print(f"\n更新: {len(updated)}ページ / スキップ: {len(skipped)}ページ")
    print("\nスキップ:")
    for name, reason in skipped:
        print(f"  - {name}: {reason}")


if __name__ == "__main__":
    main()
