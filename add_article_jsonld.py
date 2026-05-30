#!/usr/bin/env python3
"""
全ガイドページのArticle JSON-LD を以下の2点改善するスクリプト：
1. author を Organization→Person（森山春樹）に更新
2. guide_breeding.html / guide_reports.html に Article JSON-LD を新規追加
"""

import glob
import re
import json

BASE_URL = "https://beetle-finder.onrender.com"
AUTHOR_OLD = '"author": {"@type": "Organization", "name": "beetle-finder"}'
AUTHOR_OLD_COMPACT = '"author":{"@type":"Organization","name":"beetle-finder"}'
AUTHOR_NEW_FULL = '"author": {"@type": "Person", "name": "森山春樹", "url": "https://beetle-finder.onrender.com/about"}'
AUTHOR_NEW_COMPACT = '"author":{"@type":"Person","name":"森山春樹","url":"https://beetle-finder.onrender.com/about"}'

# publisher も更新
PUBLISHER_OLD = '"publisher": {"@type": "Organization", "name": "beetle-finder", "url": "https://beetle-finder.onrender.com"}'
PUBLISHER_OLD_COMPACT = '"publisher":{"@type":"Organization","name":"beetle-finder","url":"https://beetle-finder.onrender.com"}'
PUBLISHER_NEW_FULL = '"publisher": {"@type": "Organization", "name": "beetle-finder", "url": "https://beetle-finder.onrender.com", "logo": {"@type": "ImageObject", "url": "https://beetle-finder.onrender.com/static/img/icon-kuwagata.jpg"}}'
PUBLISHER_NEW_COMPACT = '"publisher":{"@type":"Organization","name":"beetle-finder","url":"https://beetle-finder.onrender.com","logo":{"@type":"ImageObject","url":"https://beetle-finder.onrender.com/static/img/icon-kuwagata.jpg"}}'

# 新規追加が必要なページ
NEW_JSONLD = {
    'templates/guide_breeding.html': {
        "headline": "クワガタ・カブトムシ幼虫の育て方｜初心者向け飼育方法を完全解説",
        "description": "クワガタ・カブトムシの幼虫の育て方を初心者向けに解説。マット・菌糸ビン・温度管理・蛹化・羽化まで、採集した幼虫をしっかり育てる方法をまとめました。",
        "url": f"{BASE_URL}/guide/breeding",
    },
    'templates/guide_reports.html': {
        "headline": "クワガタ採集レポート一覧｜実体験から学ぶ採集のコツ【beetle-finder】",
        "description": "beetle-finder運営者・森山春樹の実体験クワガタ採集レポート。奥多摩でミヤマ採集・秩父の雨上がり採集・高尾山ファミリー採集など、実際の採集記録と成功のコツを公開。",
        "url": f"{BASE_URL}/guide/reports",
    },
}

def make_article_jsonld(info: dict) -> str:
    obj = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": info["headline"],
        "description": info["description"],
        "url": info["url"],
        "datePublished": "2026-05-01",
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
            "@id": info["url"]
        }
    }
    return f'<script type="application/ld+json">\n{json.dumps(obj, ensure_ascii=False, indent=2)}\n</script>\n'

files = sorted(glob.glob('templates/guide*.html'))
updated = 0

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # --- 1. author 更新（フォーマット違いに両対応）
    content = content.replace(AUTHOR_OLD, AUTHOR_NEW_FULL)
    content = content.replace(AUTHOR_OLD_COMPACT, AUTHOR_NEW_COMPACT)

    # --- 2. publisher 更新（logo追加）
    content = content.replace(PUBLISHER_OLD, PUBLISHER_NEW_FULL)
    content = content.replace(PUBLISHER_OLD_COMPACT, PUBLISHER_NEW_COMPACT)

    # --- 3. 新規追加ページ
    if fp in NEW_JSONLD and 'application/ld+json' not in content:
        jsonld = make_article_jsonld(NEW_JSONLD[fp])
        content = content.replace('</head>', jsonld + '</head>', 1)

    if content != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  OK: {fp}')
        updated += 1
    else:
        print(f'  --: {fp} (no change)')

print(f'\n完了: {updated}/{len(files)} ファイルを更新')
