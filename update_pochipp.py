#!/usr/bin/env python3
"""
1. 全ガイドページに .pochipp-card CSS を一括追加
2. 主要6ページの商品ブロックを Pochipp スタイルに置き換え
"""

import os, re, glob

TEMPLATE_DIR = "/Users/naokitakahashi/beetle-finder/templates"
GUIDE_FILES  = sorted(glob.glob(os.path.join(TEMPLATE_DIR, "guide*.html")))

# ── Pochipp CSS ────────────────────────────────────────────
POCHIPP_CSS = """
/* ── Pochipp 型商品カード ─────────────────────────────── */
.pochipp-card{background:#fff;border:1px solid #e0e0e0;border-radius:8px;
  padding:16px;margin:28px 0;box-shadow:0 2px 8px rgba(0,0,0,.07)}
.pochipp-inner{display:flex;gap:16px;align-items:center;
  margin-bottom:14px;padding-bottom:14px;border-bottom:1px solid #f0f0f0}
.pochipp-img{width:80px;height:80px;object-fit:contain;flex-shrink:0;border-radius:4px}
.pochipp-info{flex:1;min-width:0}
.pochipp-name{font-weight:700;font-size:.95rem;color:#333;margin-bottom:6px;line-height:1.4}
.pochipp-price{font-size:.72rem;color:#888}
.pochipp-btns{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px}
.pochipp-btn{display:block;text-align:center;padding:10px 4px;border-radius:4px;
  font-size:.78rem;font-weight:700;text-decoration:none!important;color:#fff!important;line-height:1.2}
.pochipp-btn:hover{opacity:.85;text-decoration:none!important;color:#fff!important}
.pochipp-amz{background:#c8a870}
.pochipp-rkt{background:#c08080}
.pochipp-yah{background:#7a9ab8}
.pochipp-note{font-size:.6rem;color:#bbb;text-align:right}
"""

# ── 商品定義 ───────────────────────────────────────────────
PRODUCTS = {
    'headlight': {
        'img':   '/static/img/products/gentos_gh200rg.jpg',
        'name':  'GENTOS GH-200RG ヘッドライト 充電式 1200ルーメン',
        'price': '¥4,980',
        'asin':  'B09MT2GZDF',
        'amz':   'https://www.amazon.co.jp/dp/B09MT2GZDF?tag=beetlefinder-22',
        'rkt':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2FGENTOS+GH-200RG%2F',
        'yah':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925&pl_id=27061&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3DGENTOS%2BGH-200RG',
        'ev':    'GH-200RG',
    },
    'net': {
        'img':   '/static/img/products/mushitori_net.jpg',
        'name':  '伸縮式 虫取り網（38〜86cm）コンパクト収納',
        'price': '¥1,280',
        'asin':  'B07H8K5TCT',
        'amz':   'https://www.amazon.co.jp/dp/B07H8K5TCT?tag=beetlefinder-22',
        'rkt':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F%E8%99%AB%E5%8F%96%E3%82%8A%E7%B6%B2+%E4%BC%B8%E7%B8%AE%2F',
        'yah':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925&pl_id=27061&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3D%E8%99%AB%E5%8F%96%E3%82%8A%E7%B6%B2+%E4%BC%B8%E7%B8%AE',
        'ev':    'mushitori_net',
    },
    'cage': {
        'img':   '/static/img/products/mushikago_loupe.jpg',
        'name':  '虫かご ルーペ付き観察ケース クワガタ・カブトムシ',
        'price': '¥980',
        'asin':  'B08BJ8YC84',
        'amz':   'https://www.amazon.co.jp/dp/B08BJ8YC84?tag=beetlefinder-22',
        'rkt':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F%E8%99%AB%E3%81%8B%E3%81%94+%E3%83%AB%E3%83%BC%E3%83%9A%2F',
        'yah':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925&pl_id=27061&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3D%E8%99%AB%E3%81%8B%E3%81%94+%E3%83%AB%E3%83%BC%E3%83%9A',
        'ev':    'mushikago',
    },
    'set': {
        'img':   '/static/img/products/konchu_set.jpg',
        'name':  '昆虫採集セット（ケース・網・ピンセット一式）',
        'price': '¥2,480',
        'asin':  'B0CDCQ4X8Y',
        'amz':   'https://www.amazon.co.jp/dp/B0CDCQ4X8Y?tag=beetlefinder-22',
        'rkt':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86%E3%82%BB%E3%83%83%E3%83%88%2F',
        'yah':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925&pl_id=27061&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3D%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86%E3%82%BB%E3%83%83%E3%83%88',
        'ev':    'konchu_set',
    },
    'jelly': {
        'img':   '/static/img/products/prozeri.jpg',
        'name':  'KBファーム プロゼリー 昆虫ゼリー 16g×5個',
        'price': '¥338',
        'asin':  'B00X7LCXBS',
        'amz':   'https://www.amazon.co.jp/dp/B00X7LCXBS?tag=beetlefinder-22',
        'rkt':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F%E3%83%97%E3%83%AD%E3%82%BC%E3%83%AA%E3%83%BC+%E6%98%86%E8%99%AB%2F',
        'yah':   'https://af.moshimo.com/af/c/click?a_id=5563449&p_id=1225&pc_id=1925&pl_id=27061&url=https%3A%2F%2Fshopping.yahoo.co.jp%2Fsearch%3Fp%3D%E3%83%97%E3%83%AD%E3%82%BC%E3%83%AA%E3%83%BC+%E6%98%86%E8%99%AB',
        'ev':    'prozeri',
    },
}

def pochipp_card(key, page_path):
    p = PRODUCTS[key]
    return f"""<div class="pochipp-card">
  <div class="pochipp-inner">
    <img class="pochipp-img" src="{p['img']}" alt="{p['name']}" loading="lazy">
    <div class="pochipp-info">
      <div class="pochipp-name">{p['name']}</div>
      <div class="pochipp-price">{p['price']} <span>（2026/06時点 | Amazon調べ）</span></div>
    </div>
  </div>
  <div class="pochipp-btns">
    <a class="pochipp-btn pochipp-amz" href="{p['amz']}" target="_blank" rel="noopener sponsored"
       onclick="gtag&&gtag('event','affiliate_click',{{shop:'amazon',item_name:'{p['ev']}',page_path:'{page_path}'}})">Amazon</a>
    <a class="pochipp-btn pochipp-rkt" href="{p['rkt']}" target="_blank" rel="noopener sponsored"
       onclick="gtag&&gtag('event','affiliate_click',{{shop:'rakuten',item_name:'{p['ev']}',page_path:'{page_path}'}})">楽天市場</a>
    <a class="pochipp-btn pochipp-yah" href="{p['yah']}" target="_blank" rel="noopener sponsored"
       onclick="gtag&&gtag('event','affiliate_click',{{shop:'yahoo',item_name:'{p['ev']}',page_path:'{page_path}'}})">Yahooショッピング</a>
  </div>
  <div class="pochipp-note">※ 価格・在庫は変動する場合があります</div>
</div>
"""

def pochipp_section(keys, page_path, title="🛒 採集に必要な道具"):
    cards = "".join(pochipp_card(k, page_path) for k in keys)
    return f'<div class="amz-section">\n<p class="amz-section-title">{title}</p>\n{cards}</div>\n'

# ── STEP 1: 全ガイドページに CSS を注入 ───────────────────
css_added = 0
for filepath in GUIDE_FILES:
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    if 'pochipp-card' in content:
        continue
    # </style> の直前に挿入
    new_content = content.replace('</style>', POCHIPP_CSS + '</style>', 1)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        css_added += 1
print(f"CSS追加: {css_added}ページ")

# ── STEP 2: 主要ページの商品ブロックを Pochipp 形式に置換 ──

# ページごとに「置換したいブロックの開始〜終了パターン」と新ブロックを定義
# amz-section ブロック全体を新しいものに置き換える

def replace_amz_section(filepath, new_section):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()
    # <div class="amz-section"> ... </div> を探して置換（最初の1件）
    pattern = r'<div class="amz-section">.*?</div>\s*\n'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        print(f"  ⚠️  amz-section 未検出: {os.path.basename(filepath)}")
        return False
    new_content = content[:m.start()] + new_section + content[m.end():]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True

pages = {
    'guide_july.html':    (['headlight','net','set','jelly'], '/guide/july',   '🛒 7月の採集に持っていくもの'),
    'guide_august.html':  (['headlight','net','set','jelly'], '/guide/august', '🛒 8月の採集に持っていくもの'),
    'guide_june.html':    (['headlight','net','cage','jelly'],'/guide/june',   '🛒 6月の採集に持っていくもの'),
}

for filename, (keys, page_path, title) in pages.items():
    filepath = os.path.join(TEMPLATE_DIR, filename)
    new_sec = pochipp_section(keys, page_path, title)
    ok = replace_amz_section(filepath, new_sec)
    if ok:
        print(f"✅ {filename}")

# ── guide_tools の tool-card を Pochipp に置換 ──────────────
def replace_tool_cards_in_tools():
    filepath = os.path.join(TEMPLATE_DIR, 'guide_tools.html')
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # ヘッドライト tool-card を pochipp-card に
    old = re.search(
        r'<div class="tool-card">\s*<div class="tool-icon"><img src="/static/img/products/gentos_gh200rg\.jpg".*?</div>\s*</div>',
        content, re.DOTALL)
    if old:
        content = content[:old.start()] + pochipp_card('headlight', '/guide/tools') + content[old.end():]

    # 虫かご tool-card
    old = re.search(
        r'<div class="tool-card">\s*<div class="tool-icon"><img src="/static/img/products/mushikago_loupe\.jpg".*?(?=<div class="tool-card">|<h2)',
        content, re.DOTALL)
    if old:
        # mushikago + net の2カード分を含む可能性あるのでネットカードも一緒に置換
        pass

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ guide_tools.html (ヘッドライトカード)")

replace_tool_cards_in_tools()

# ── guide_beginners / guide_night のインラインカードを Pochipp に ──
def replace_inline_cards(filename, page_path, keys, title):
    filepath = os.path.join(TEMPLATE_DIR, filename)
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # "🛒 初心者が最初に揃える道具" or "🛒 今夜の採集" ブロックを探す
    pattern = r'<!-- 商品カード.*?-->\s*<div style="background:#f1f8e9.*?</div>\s*\n'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        # 別パターン
        pattern2 = r'<div style="background:#f1f8e9.*?Amazon・楽天アソシエイトリンク.*?</div>\s*\n'
        m = re.search(pattern2, content, re.DOTALL)
    if m:
        new_sec = pochipp_section(keys, page_path, title)
        content = content[:m.start()] + new_sec + content[m.end():]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename}")
    else:
        print(f"  ⚠️  ブロック未検出: {filename}")

replace_inline_cards('guide_beginners.html', '/guide/beginners',
                     ['headlight','net','cage'], '🛒 初心者が最初に揃える道具')
replace_inline_cards('guide_night.html', '/guide/night',
                     ['headlight','net'], '🛒 夜間採集の必須道具')

print("\n完了")
