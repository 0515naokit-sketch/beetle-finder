#!/usr/bin/env python3
"""
都道府県ページ強化：
- 近隣県リンク追加（PV/セッション向上）
- OGP meta追加（AI引用・SNSシェア強化）
- SNSシェアボタン追加（X流入強化）
"""

import glob, re, json

BASE_URL = "https://beetle-finder.onrender.com"

# ── 近隣県マッピング ───────────────────────────────────────────────────────
NEARBY = {
    'hokkaido': [],
    'aomori':   ['iwate','akita'],
    'iwate':    ['aomori','akita','miyagi'],
    'miyagi':   ['iwate','akita','yamagata','fukushima'],
    'akita':    ['aomori','iwate','miyagi','yamagata'],
    'yamagata': ['akita','miyagi','fukushima','niigata'],
    'fukushima':['miyagi','yamagata','niigata','tochigi','gunma','ibaraki'],
    'ibaraki':  ['fukushima','tochigi','saitama','chiba','tokyo'],
    'tochigi':  ['fukushima','ibaraki','gunma','saitama'],
    'gunma':    ['fukushima','tochigi','saitama','nagano','niigata'],
    'saitama':  ['tochigi','gunma','ibaraki','tokyo','chiba','nagano','yamanashi'],
    'chiba':    ['ibaraki','saitama','tokyo','kanagawa'],
    'tokyo':    ['saitama','chiba','kanagawa','yamanashi'],
    'kanagawa': ['tokyo','chiba','yamanashi','shizuoka'],
    'niigata':  ['yamagata','fukushima','gunma','nagano','toyama'],
    'toyama':   ['niigata','nagano','ishikawa','gifu'],
    'ishikawa': ['toyama','fukui','gifu'],
    'fukui':    ['ishikawa','gifu','shiga','kyoto'],
    'yamanashi':['saitama','tokyo','kanagawa','nagano','shizuoka'],
    'nagano':   ['niigata','gunma','saitama','yamanashi','shizuoka','aichi','gifu','toyama'],
    'gifu':     ['toyama','ishikawa','fukui','nagano','shizuoka','aichi','mie','shiga'],
    'shizuoka': ['kanagawa','yamanashi','nagano','aichi'],
    'aichi':    ['shizuoka','nagano','gifu','mie'],
    'mie':      ['aichi','gifu','shiga','nara','wakayama'],
    'shiga':    ['fukui','gifu','mie','kyoto','nara'],
    'kyoto':    ['fukui','shiga','nara','osaka','hyogo'],
    'osaka':    ['kyoto','nara','hyogo','wakayama'],
    'hyogo':    ['kyoto','osaka','nara','tottori','okayama'],
    'nara':     ['mie','shiga','kyoto','osaka','wakayama'],
    'wakayama': ['mie','nara','osaka'],
    'tottori':  ['hyogo','okayama','shimane'],
    'shimane':  ['tottori','okayama','hiroshima','yamaguchi'],
    'okayama':  ['hyogo','tottori','shimane','hiroshima'],
    'hiroshima':['okayama','shimane','yamaguchi','ehime'],
    'yamaguchi':['shimane','hiroshima','fukuoka'],
    'tokushima':['kagawa','ehime','kochi'],
    'kagawa':   ['tokushima','ehime'],
    'ehime':    ['kagawa','tokushima','kochi','hiroshima'],
    'kochi':    ['tokushima','ehime'],
    'fukuoka':  ['yamaguchi','saga','kumamoto','oita'],
    'saga':     ['fukuoka','nagasaki'],
    'nagasaki': ['saga','kumamoto'],
    'kumamoto': ['fukuoka','nagasaki','oita','miyazaki','kagoshima'],
    'oita':     ['fukuoka','kumamoto','miyazaki'],
    'miyazaki': ['kumamoto','oita','kagoshima'],
    'kagoshima':['kumamoto','miyazaki'],
    'okinawa':  [],
}

PREF_NAMES = {
    'hokkaido':'北海道','aomori':'青森県','iwate':'岩手県','miyagi':'宮城県',
    'akita':'秋田県','yamagata':'山形県','fukushima':'福島県','ibaraki':'茨城県',
    'tochigi':'栃木県','gunma':'群馬県','saitama':'埼玉県','chiba':'千葉県',
    'tokyo':'東京都','kanagawa':'神奈川県','niigata':'新潟県','toyama':'富山県',
    'ishikawa':'石川県','fukui':'福井県','yamanashi':'山梨県','nagano':'長野県',
    'gifu':'岐阜県','shizuoka':'静岡県','aichi':'愛知県','mie':'三重県',
    'shiga':'滋賀県','kyoto':'京都府','osaka':'大阪府','hyogo':'兵庫県',
    'nara':'奈良県','wakayama':'和歌山県','tottori':'鳥取県','shimane':'島根県',
    'okayama':'岡山県','hiroshima':'広島県','yamaguchi':'山口県','tokushima':'徳島県',
    'kagawa':'香川県','ehime':'愛媛県','kochi':'高知県','fukuoka':'福岡県',
    'saga':'佐賀県','nagasaki':'長崎県','kumamoto':'熊本県','oita':'大分県',
    'miyazaki':'宮崎県','kagoshima':'鹿児島県','okinawa':'沖縄県',
}

def make_nearby_html(slug: str) -> str:
    nearby = NEARBY.get(slug, [])
    if not nearby:
        return ''
    items = []
    for s in nearby:
        name = PREF_NAMES.get(s, s)
        items.append(f'<a href="/guide/pref/{s}" class="nearby-btn">{name}</a>')
    return f'''
<div class="nearby-box">
  <span class="nearby-label">🗾 近隣の都道府県ガイドも見る</span>
  <div class="nearby-links">{''.join(items)}</div>
</div>'''

NEARBY_CSS = '''
  .nearby-box{background:#e8f5e9;border-radius:10px;padding:14px 18px;margin:24px 0;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
  .nearby-label{font-size:.82rem;font-weight:700;color:#1b5e20;white-space:nowrap}
  .nearby-links{display:flex;flex-wrap:wrap;gap:8px}
  .nearby-btn{display:inline-block;background:#fff;border:1px solid #a5d6a7;color:#2e7d32;padding:5px 12px;border-radius:20px;font-size:.8rem;font-weight:700;text-decoration:none}
  .nearby-btn:hover{background:#2e7d32;color:#fff;text-decoration:none}'''

def make_share_html(title: str, url: str) -> str:
    import urllib.parse
    tweet_text = urllib.parse.quote(f'{title} {url} #クワガタ採集 #beetle_finder')
    return f'''
<div class="share-box">
  <span class="share-label">📣 この記事をシェア</span>
  <div class="share-links">
    <a href="https://twitter.com/intent/tweet?text={tweet_text}" target="_blank" rel="noopener" class="share-x">𝕏 Xでシェア</a>
    <a href="https://b.hatena.ne.jp/add?mode=confirm&url={urllib.parse.quote(url)}&title={urllib.parse.quote(title)}" target="_blank" rel="noopener" class="share-hb">🔖 はてブ</a>
  </div>
</div>'''

SHARE_CSS = '''
  .share-box{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:28px 0;padding:14px 18px;background:#f9f9f9;border-radius:10px;border:1px solid #e0e0e0}
  .share-label{font-size:.82rem;font-weight:700;color:#555}
  .share-links{display:flex;gap:8px;flex-wrap:wrap}
  .share-x{background:#000;color:#fff!important;padding:7px 16px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none!important}
  .share-x:hover{background:#333!important}
  .share-hb{background:#00a4de;color:#fff!important;padding:7px 16px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none!important}
  .share-hb:hover{background:#0083b3!important}'''

def make_ogp(title: str, description: str, url: str) -> str:
    return f'''  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE_URL}/static/img/ogp-guide.png">
  <meta property="og:site_name" content="クワガタ採集スポット検索 beetle-finder">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{BASE_URL}/static/img/ogp-guide.png">'''

def process_pref_file(fp: str) -> bool:
    m = re.search(r'guide_pref_(\w+)\.html', fp)
    if not m:
        return False
    slug = m.group(1)
    pref_name = PREF_NAMES.get(slug, slug)

    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # ── OGP追加（なければ）──────────────────────────
    if 'og:title' not in content:
        title_m = re.search(r'<title>(.*?)</title>', content)
        desc_m  = re.search(r'<meta name=["\']description["\'] content=["\'](.*?)["\']', content)
        canon_m = re.search(r'<link rel=["\']canonical["\'] href=["\'](.*?)["\']', content)
        if title_m and desc_m:
            title = title_m.group(1)
            desc  = desc_m.group(1)
            url   = canon_m.group(1) if canon_m else f'{BASE_URL}/guide/pref/{slug}'
            ogp   = make_ogp(title, desc, url)
            content = content.replace('</head>', ogp + '\n</head>', 1)

    # ── CSS追加（なければ）──────────────────────────
    if 'nearby-box' not in content:
        content = content.replace('</style>', NEARBY_CSS + '\n  </style>', 1)
    if 'share-box' not in content:
        content = content.replace('</style>', SHARE_CSS + '\n  </style>', 1)

    # ── 近隣県リンク挿入（CTAボックスの直前）────────
    if 'nearby-box' not in original:
        nearby_html = make_nearby_html(slug)
        if nearby_html:
            # .cta-boxの直前に挿入
            content = re.sub(
                r'(<div class=["\']cta-box["\'])',
                nearby_html + r'\n\1',
                content,
                count=1
            )

    # ── シェアボタン挿入（フッター直前）───────────────
    if 'share-box' not in original:
        title_m = re.search(r'<title>(.*?)</title>', content)
        canon_m = re.search(r'<link rel=["\']canonical["\'] href=["\'](.*?)["\']', content)
        if title_m:
            title = title_m.group(1)
            url   = canon_m.group(1) if canon_m else f'{BASE_URL}/guide/pref/{slug}'
            share = make_share_html(title, url)
            content = content.replace('<footer>', share + '\n<footer>', 1)

    if content != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# ─── 実行 ────────────────────────────────────────────────────────────────────
pref_files = sorted(glob.glob('/Users/naokitakahashi/beetle-finder/templates/guide_pref_*.html'))
updated = 0
for fp in pref_files:
    if process_pref_file(fp):
        print(f'  OK: {fp.split("/")[-1]}')
        updated += 1
print(f'\n都道府県ページ: {updated}/{len(pref_files)} 件更新')
