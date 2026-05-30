#!/usr/bin/env python3
"""
全ガイドページ（都道府県以外）にシェアボタン・OGP追加
"""
import glob, re, urllib.parse

BASE_URL = "https://beetle-finder.onrender.com"

SHARE_CSS = '''
  .share-box{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:28px 0;padding:14px 18px;background:#f9f9f9;border-radius:10px;border:1px solid #e0e0e0}
  .share-label{font-size:.82rem;font-weight:700;color:#555}
  .share-links{display:flex;gap:8px;flex-wrap:wrap}
  .share-x{background:#000;color:#fff!important;padding:7px 16px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none!important}
  .share-x:hover{background:#333!important}
  .share-hb{background:#00a4de;color:#fff!important;padding:7px 16px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none!important}
  .share-hb:hover{background:#0083b3!important}'''

def make_share_html(title, url):
    tweet = urllib.parse.quote(f'{title} {url} #クワガタ採集 #beetle_finder')
    hb    = urllib.parse.quote(url)
    ht    = urllib.parse.quote(title)
    return f'''
<div class="share-box">
  <span class="share-label">📣 この記事をシェア</span>
  <div class="share-links">
    <a href="https://twitter.com/intent/tweet?text={tweet}" target="_blank" rel="noopener" class="share-x">𝕏 Xでシェア</a>
    <a href="https://b.hatena.ne.jp/add?mode=confirm&url={hb}&title={ht}" target="_blank" rel="noopener" class="share-hb">🔖 はてブ</a>
  </div>
</div>'''

def make_ogp(title, desc, url):
    return f'''  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{BASE_URL}/static/img/ogp-guide.png">
  <meta property="og:site_name" content="クワガタ採集スポット検索 beetle-finder">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{BASE_URL}/static/img/ogp-guide.png">'''

# 都道府県以外のガイドページを対象
files = [f for f in sorted(glob.glob('/Users/naokitakahashi/beetle-finder/templates/guide*.html'))
         if 'guide_pref_' not in f]

updated = 0
for fp in files:
    with open(fp) as f:
        content = f.read()
    original = content

    title_m = re.search(r'<title>(.*?)</title>', content)
    desc_m  = re.search(r'<meta name=["\']description["\'] content=["\'](.*?)["\']', content)
    canon_m = re.search(r'<link rel=["\']canonical["\'] href=["\'](.*?)["\']', content)
    if not title_m:
        continue

    title = title_m.group(1)
    desc  = desc_m.group(1) if desc_m else title
    url   = canon_m.group(1) if canon_m else BASE_URL + '/guide'

    # OGP追加
    if 'og:title' not in content:
        ogp = make_ogp(title, desc, url)
        content = content.replace('</head>', ogp + '\n</head>', 1)

    # シェアCSSとボタン追加
    if 'share-box' not in content:
        content = content.replace('</style>', SHARE_CSS + '\n  </style>', 1)
        share = make_share_html(title, url)
        content = content.replace('<footer>', share + '\n<footer>', 1)

    if content != original:
        with open(fp, 'w') as f:
            f.write(content)
        updated += 1

print(f'ガイドページ OGP+シェアボタン: {updated}/{len(files)} 件更新')
