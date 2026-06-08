#!/usr/bin/env python3
"""全コンテンツページに BreadcrumbList 構造化データを追加するスクリプト"""
import re
import json
import os
import html

BASE_URL = "https://beetle-finder.onrender.com"
TEMPLATES_DIR = "templates"

# スキップするページ（非コンテンツ・パンくずなし・Jinja2テンプレート）
SKIP_FILES = {
    "404.html", "contact.html", "index.html", "landing.html",
    "terms.html",  # noindex
    "guide_pref.html",  # Jinja2テンプレート（既にBreadcrumbListあり）
    "guide_pref_index.html",  # ナビ系
    "guide_spot.html",  # ナビ系
}

def extract_breadcrumb(content, filename):
    """breadcrumbのリンクと最後のアイテムを抽出"""
    # multilineでbreadcrumbを取得（div内に改行あり）
    m = re.search(r'<(?:div|nav)[^>]*class="breadcrumb"[^>]*>(.*?)</(?:div|nav)>', content, re.DOTALL)
    if not m:
        return None
    bc_inner = m.group(1)

    # Jinja2変数が含まれるページはスキップ
    if "{{" in bc_inner or "{%" in bc_inner:
        return None

    # aタグのhrefとテキストを抽出
    links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', bc_inner)
    if not links:
        return None

    # 最後のアイテム（現在ページ）のテキストを抽出
    # HTMLタグを除去
    plain = re.sub(r'<[^>]+>', '', bc_inner)
    # エンティティをデコード
    plain = html.unescape(plain)
    # セパレータ（>、›、‹）で分割
    parts = re.split(r'\s*[>›»‹«\|]\s*', plain)
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return None
    current_page = parts[-1]

    return links, current_page

def get_canonical_url(content):
    """canonical URLを取得"""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', content)
    return m.group(1) if m else None

def build_breadcrumb_jsonld(links, current_page, canonical_url):
    """BreadcrumbList JSON-LDを生成"""
    items = []
    for i, (href, name) in enumerate(links):
        url = BASE_URL + href if href.startswith("/") else href
        items.append({
            "@type": "ListItem",
            "position": i + 1,
            "name": name,
            "item": url
        })
    # 現在ページを追加
    if canonical_url:
        items.append({
            "@type": "ListItem",
            "position": len(links) + 1,
            "name": current_page,
            "item": canonical_url
        })

    schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)

def process_file(filepath):
    filename = os.path.basename(filepath)
    if filename in SKIP_FILES:
        return False, "スキップ"

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # 既にBreadcrumbListが存在する場合はスキップ
    if "BreadcrumbList" in content:
        return False, "既に存在"

    # breadcrumbが無い場合はスキップ
    result = extract_breadcrumb(content, filename)
    if result is None:
        return False, "パンくず無し/Jinja2"

    links, current_page = result
    canonical_url = get_canonical_url(content)

    jsonld = build_breadcrumb_jsonld(links, current_page, canonical_url)
    script_block = f'\n<script type="application/ld+json">\n{jsonld}\n</script>'

    # </head>の直前に挿入
    if "</head>" not in content:
        return False, "</head>なし"

    new_content = content.replace("</head>", script_block + "\n</head>", 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, f"{len(links)+1}アイテム"

def main():
    files = sorted(os.listdir(TEMPLATES_DIR))
    added = 0
    for fname in files:
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(TEMPLATES_DIR, fname)
        ok, msg = process_file(fpath)
        status = "✅ 追加" if ok else "  スキップ"
        print(f"{status}: {fname} ({msg})")
        if ok:
            added += 1
    print(f"\n合計 {added} ページに BreadcrumbList を追加しました")

if __name__ == "__main__":
    main()
