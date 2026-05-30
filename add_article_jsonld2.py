#!/usr/bin/env python3
"""
Article JSON-LDがないガイドページ65件に追加するスクリプト
- <title> と <meta name="description"> からheadline/descriptionを自動取得
- ファイル名からURLを生成
- </head> の直前に挿入
"""

import glob, re, json

BASE_URL = "https://beetle-finder.onrender.com"

# ファイル名 → URL パスのマッピング
# guide_pref_xxx.html → /guide/pref/xxx
# guide_xxx.html      → /guide/xxx
# guide.html          → /guide

def filename_to_url(fp: str) -> str:
    name = fp.replace('templates/', '').replace('.html', '')
    if name == 'guide':
        return f"{BASE_URL}/guide"
    if name.startswith('guide_pref_'):
        slug = name.replace('guide_pref_', '')
        return f"{BASE_URL}/guide/pref/{slug}"
    slug = name.replace('guide_', '')
    return f"{BASE_URL}/guide/{slug}"

def get_title(content: str) -> str:
    m = re.search(r'<title>(.*?)</title>', content)
    return m.group(1).strip() if m else ''

def get_description(content: str) -> str:
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content)
    return m.group(1).strip() if m else ''

def make_article_jsonld(headline, description, url) -> str:
    obj = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": description,
        "url": url,
        "datePublished": "2026-04-01",
        "dateModified": "2026-05-30",
        "author": {
            "@type": "Person",
            "name": "森山春樹",
            "url": f"{BASE_URL}/about"
        },
        "publisher": {
            "@type": "Organization",
            "name": "beetle-finder",
            "url": BASE_URL,
            "logo": {
                "@type": "ImageObject",
                "url": f"{BASE_URL}/static/img/icon-kuwagata.jpg"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": url
        }
    }
    return f'<script type="application/ld+json">\n{json.dumps(obj, ensure_ascii=False, indent=2)}\n</script>'

files = sorted(glob.glob('templates/guide*.html'))
updated = 0
skipped = 0

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    # Article JSON-LDがすでにある場合はスキップ
    if '"Article"' in content:
        skipped += 1
        continue

    headline = get_title(content)
    description = get_description(content)
    url = filename_to_url(fp)

    if not headline:
        print(f'  WARNING: タイトルなし {fp}')
        continue

    jsonld = make_article_jsonld(headline, description, url)
    # </head> の直前に挿入
    new_content = content.replace('</head>', jsonld + '\n</head>', 1)

    if new_content == content:
        print(f'  WARNING: 挿入失敗 {fp}')
        continue

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  OK: {fp}')
    updated += 1

print(f'\n完了: {updated} 件追加, {skipped} 件スキップ（既存Article）')
