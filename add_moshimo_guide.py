"""
add_moshimo_guide.py
────────────────────────────────────────────────────────────────
ガイドページ（guide_*.html）にページテーマ別の
もしもアフィリエイトリンク（Amazon・楽天・Yahoo!）を一括追加。
挿入位置: <div class="cta-box"> の直前
"""

import os
import urllib.parse

TEMPLATES_DIR = "templates"

# ── URLビルダー ──────────────────────────────────────────────────────────────
def amz(kw):
    return f"https://www.amazon.co.jp/s?k={urllib.parse.quote(kw)}&tag=beetlefinder-22"

def rkt(kw):
    kw_enc = urllib.parse.quote(kw)
    return (f"https://af.moshimo.com/af/c/click?a_id=5563442&p_id=54&pc_id=54"
            f"&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{kw_enc}%2F")

def yah(kw):
    kw_enc = urllib.parse.quote(kw)
    return (f"https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925"
            f"&pl_id=19142&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3D{kw_enc}")

# ── 商品ブロックHTML生成 ─────────────────────────────────────────────────────
def item_row(label, icon, kw_amz, kw_rkt=None, kw_yah=None):
    kw_rkt = kw_rkt or kw_amz
    kw_yah = kw_yah or kw_amz
    return f"""\
      <div class="amz-links" style="margin-bottom:6px">
        <span style="font-size:.8rem;font-weight:700;color:#555;min-width:160px;display:inline-block">{icon} {label}</span>
        <a href="{amz(kw_amz)}" target="_blank" rel="noopener sponsored" class="amz-btn">Amazon</a>
        <a href="{rkt(kw_rkt)}" target="_blank" rel="noopener sponsored" class="rkt-btn">楽天</a>
        <a href="{yah(kw_yah)}" target="_blank" rel="noopener sponsored" class="yah-btn">Yahoo!</a>
      </div>"""

def build_block(title, items):
    rows = "\n".join(items)
    return f"""\
  <h2 class="section">🛒 {title}</h2>
  <div class="amz-box">
{rows}
    <p class="amz-note">※Amazon・楽天・Yahoo!のアフィリエイトプログラム参加中。クリックで価格は変わりません。</p>
  </div>

"""

# ── ページ別商品定義 ─────────────────────────────────────────────────────────
PAGES = {
    "guide_aftercare": build_block("採集後の飼育グッズ一覧", [
        item_row("飼育ケース（中〜大）",   "🪲", "クワガタ 飼育ケース 中 大", "クワガタ 飼育ケース", "クワガタ 飼育ケース"),
        item_row("昆虫マット",           "🌱", "昆虫マット クワガタ カブトムシ"),
        item_row("昆虫ゼリー",           "🍊", "昆虫ゼリー クワガタ 16g"),
        item_row("産卵木（朽ち木）",       "🪵", "産卵木 クワガタ 朽ち木", "産卵木 クワガタ"),
        item_row("ハスクチップ（床材）",    "🍂", "ハスクチップ 昆虫 床材", "ハスクチップ 昆虫"),
    ]),
    "guide_kids": build_block("子供と採集 おすすめグッズ", [
        item_row("虫取り網（伸縮式）",     "🥅", "虫取り網 伸縮式 子供"),
        item_row("虫かご（観察ケース）",   "🔍", "虫かご 観察ケース 子供 昆虫採集"),
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 子供 アウトドア"),
        item_row("虫よけスプレー（子供用）", "🦟", "虫よけ スプレー 子供 天然"),
        item_row("長靴（子供用）",         "👢", "長靴 子供 アウトドア 軽量"),
    ]),
    "guide_light": build_block("ライトトラップ・街灯採集の道具", [
        item_row("ブラックライト",         "💡", "ブラックライト LED 昆虫採集"),
        item_row("ライトトラップ用シート",  "📄", "ライトトラップ 白布 昆虫採集"),
        item_row("ヘッドライト（高輝度）",  "🔦", "ヘッドライト 高輝度 充電式 1000ルーメン"),
        item_row("電池（単3・単4）",       "🔋", "充電池 単3 エネループ", "充電池 単3"),
        item_row("虫かご（大型）",         "🪲", "虫かご 大型 昆虫採集"),
    ]),
    "guide_ookuwa": build_block("オオクワガタ採集・飼育グッズ", [
        item_row("菌糸ビン",              "🍄", "菌糸ビン オオクワガタ 800cc"),
        item_row("産卵木（太め）",         "🪵", "産卵木 オオクワガタ 太め 朽ち木"),
        item_row("飼育ケース（コバエシャッター）", "🪲", "コバエシャッター 飼育ケース クワガタ"),
        item_row("昆虫マット（産卵用）",   "🌱", "昆虫マット 産卵用 クワガタ"),
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式"),
    ]),
    "guide_september": build_block("9月・シーズン後半の採集グッズ", [
        item_row("スズメバチスプレー",     "🐝", "スズメバチ 撃退スプレー"),
        item_row("越冬用マット",           "🍂", "昆虫マット 越冬 クワガタ"),
        item_row("飼育ケース（越冬用）",   "🪲", "クワガタ 飼育ケース 越冬"),
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式"),
        item_row("虫よけスプレー",         "🦟", "虫よけスプレー ディート 長時間"),
    ]),
    "guide_october": build_block("10月・越冬準備グッズ", [
        item_row("越冬用マット（深め）",   "🍂", "昆虫マット クワガタ 越冬 深め"),
        item_row("飼育ケース（中〜大）",   "🪲", "クワガタ 飼育ケース 中 大"),
        item_row("霧吹き（湿度管理用）",   "💧", "霧吹き 昆虫 飼育"),
        item_row("昆虫ゼリー",           "🍊", "昆虫ゼリー クワガタ"),
        item_row("温湿度計",             "🌡️", "デジタル温湿度計 小型"),
    ]),
    "guide_akaashi": build_block("アカアシクワガタ採集グッズ", [
        item_row("ヘッドライト（高山用）",  "🔦", "ヘッドライト 充電式 防水 登山"),
        item_row("虫取り網",             "🥅", "虫取り網 伸縮式 昆虫採集"),
        item_row("飼育ケース",           "🪲", "クワガタ 飼育ケース"),
        item_row("レインウェア（防寒）",   "🧥", "レインウェア アウトドア 防寒 軽量"),
        item_row("虫よけスプレー",         "🦟", "虫よけスプレー ディート"),
    ]),
    "guide_august": build_block("8月・盛夏の採集グッズ", [
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式"),
        item_row("虫かご",               "🪣", "虫かご クワガタ カブトムシ"),
        item_row("バナナトラップ材料",     "🍌", "バナナ 昆虫トラップ 焼酎", "バナナトラップ 昆虫採集"),
        item_row("スズメバチスプレー",     "🐝", "スズメバチ 撃退スプレー"),
        item_row("飲料・塩分補給",        "💊", "塩分補給 タブレット アウトドア 熱中症"),
    ]),
    "guide_beginners": build_block("初心者向け採集スターターセット", [
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式 アウトドア"),
        item_row("虫取り網（伸縮式）",     "🥅", "虫取り網 伸縮式 昆虫採集"),
        item_row("虫かご",               "🪣", "虫かご クワガタ カブトムシ"),
        item_row("スズメバチスプレー",     "🐝", "スズメバチ 撃退スプレー 携帯"),
        item_row("長袖シャツ（虫刺され対策）", "👕", "長袖シャツ アウトドア 虫刺され UVカット"),
    ]),
    "guide_july": build_block("7月・最盛期の採集グッズ", [
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式"),
        item_row("虫かご",               "🪣", "虫かご クワガタ カブトムシ"),
        item_row("スズメバチスプレー",     "🐝", "スズメバチ 撃退スプレー"),
        item_row("虫よけスプレー",         "🦟", "虫よけスプレー ディート"),
        item_row("飼育セット（持ち帰り後）", "🪲", "クワガタ カブトムシ 飼育セット"),
    ]),
    "guide_june": build_block("6月・シーズン開幕グッズ", [
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式 防水"),
        item_row("レインウェア（梅雨対策）", "🧥", "レインウェア アウトドア 軽量 防水"),
        item_row("長靴",                 "👢", "長靴 アウトドア 軽量 滑り止め"),
        item_row("虫取り網",             "🥅", "虫取り網 伸縮式"),
        item_row("虫かご",               "🪣", "虫かご 昆虫採集"),
    ]),
    "guide_may": build_block("5月・採集準備グッズ", [
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式"),
        item_row("虫取り網",             "🥅", "虫取り網 伸縮式 昆虫採集"),
        item_row("虫かご",               "🪣", "虫かご クワガタ"),
        item_row("飼育ケース（準備）",    "🪲", "クワガタ 飼育セット 初心者"),
        item_row("長袖シャツ・手袋",      "🧤", "アウトドア 長袖シャツ 速乾 UVカット"),
    ]),
    "guide_rain": build_block("雨天・雨上がり採集グッズ", [
        item_row("防水ヘッドライト（IP54）", "🔦", "ヘッドライト 防水 IP54 充電式"),
        item_row("レインウェア（上下）",   "🧥", "レインウェア セパレート アウトドア"),
        item_row("長靴（滑り止め）",       "👢", "長靴 滑り止め アウトドア"),
        item_row("防水スマホケース",       "📱", "防水スマホケース アウトドア"),
        item_row("虫よけスプレー",         "🦟", "虫よけスプレー ディート 長時間"),
    ]),
    "guide_suji": build_block("スジクワガタ採集・飼育グッズ", [
        item_row("ヘッドライト",          "🔦", "ヘッドライト LED 充電式"),
        item_row("飼育ケース（小型）",    "🪲", "クワガタ 飼育ケース 小型"),
        item_row("昆虫マット",           "🌱", "昆虫マット クワガタ"),
        item_row("産卵木",               "🪵", "産卵木 クワガタ 細め"),
        item_row("虫取り網",             "🥅", "虫取り網 伸縮式"),
    ]),
    "guide_tools": build_block("クワガタ採集 おすすめ道具一覧", [
        item_row("ヘッドライト（高輝度）",  "🔦", "ヘッドライト 高輝度 充電式 1000ルーメン以上"),
        item_row("虫取り網（伸縮式）",     "🥅", "虫取り網 伸縮式 昆虫採集"),
        item_row("虫かご（通気性）",       "🪣", "虫かご 通気性 昆虫採集"),
        item_row("スズメバチスプレー",     "🐝", "スズメバチ 撃退スプレー 携帯"),
        item_row("長袖・虫刺され対策",    "👕", "アウトドア 長袖 虫刺され 速乾"),
    ]),
    "guide_jiyukenkyu": build_block("自由研究グッズ", [
        item_row("観察ケース（ルーペ付き）", "🔍", "昆虫 観察ケース ルーペ 子供"),
        item_row("虫取り網",             "🥅", "虫取り網 子供 昆虫採集"),
        item_row("クワガタ図鑑",          "📗", "クワガタ 図鑑 子供 昆虫"),
        item_row("標本用品",             "📦", "昆虫 標本 キット 子供"),
        item_row("飼育セット",           "🪲", "クワガタ 飼育セット 入門"),
    ]),
    "guide_jiyukenkyu_kabuto": build_block("カブトムシ自由研究グッズ", [
        item_row("観察ケース",           "🔍", "カブトムシ 観察ケース 飼育"),
        item_row("虫取り網",             "🥅", "虫取り網 子供"),
        item_row("カブトムシ図鑑",        "📗", "カブトムシ 図鑑 子供"),
        item_row("飼育マット",           "🌱", "カブトムシ 昆虫マット 飼育"),
        item_row("昆虫ゼリー",           "🍊", "昆虫ゼリー カブトムシ"),
    ]),
}

# ── CSSが未定義なら追加 ──────────────────────────────────────────────────────
AMZ_BOX_CSS = """
    .amz-box{background:#fffbf0;border:1px solid #f0c040;border-radius:8px;padding:14px 16px;margin:20px 0}
    .amz-box-title{font-weight:700;color:#c45000;font-size:.88rem;margin-bottom:10px}
    .amz-links{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:4px}
    .amz-btn{display:inline-block;background:#ff9900;color:#fff !important;padding:6px 12px;border-radius:5px;font-size:.78rem;font-weight:700;text-decoration:none !important}
    .amz-btn:hover{background:#e68900 !important}
    .rkt-btn{display:inline-block;background:#bf0000;color:#fff !important;padding:6px 12px;border-radius:5px;font-size:.78rem;font-weight:700;text-decoration:none !important}
    .rkt-btn:hover{background:#900 !important}
    .yah-btn{display:inline-block;background:#ff0033;color:#fff !important;padding:6px 12px;border-radius:5px;font-size:.78rem;font-weight:700;text-decoration:none !important}
    .yah-btn:hover{background:#cc0029 !important}
    .amz-note{font-size:.7rem;color:#999;margin-top:8px}
"""

INSERT_MARKER = '<div class="cta-box">'


def process(page_key, block_html):
    filepath = os.path.join(TEMPLATES_DIR, f"{page_key}.html")
    if not os.path.exists(filepath):
        return False, "file not found"

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # 既に実際のrkt-btnリンクがあればスキップ（CSS定義は除く）
    if 'class="rkt-btn"' in content or 'href' in content and 'moshimo' in content:
        return False, "already has rkt-btn links"

    if INSERT_MARKER not in content:
        return False, f"marker '{INSERT_MARKER}' not found"

    # CSSがなければ追加
    if ".amz-box{" not in content and ".amz-box {" not in content:
        content = content.replace("</style>", AMZ_BOX_CSS + "  </style>", 1)

    # ブロックを挿入
    content = content.replace(INSERT_MARKER, block_html + INSERT_MARKER, 1)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return True, "updated"


def main():
    updated, skipped = [], []
    for page_key, block in PAGES.items():
        ok, reason = process(page_key, block)
        if ok:
            updated.append(page_key)
            print(f"  ✓ {page_key}.html")
        else:
            skipped.append((page_key, reason))
            print(f"  - {page_key}.html : {reason}")

    print(f"\n更新: {len(updated)}ページ / スキップ: {len(skipped)}ページ")


if __name__ == "__main__":
    main()
