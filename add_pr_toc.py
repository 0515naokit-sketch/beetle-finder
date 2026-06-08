#!/usr/bin/env python3
"""
全ガイドページに PR表示 + 目次（TOC）を一括追加
・PR表示: page-subtitle の直後
・TOC: PR表示の直後（h2要素から自動生成）
・既に追加済みのページはスキップ
"""

import os, re, glob
from bs4 import BeautifulSoup

TEMPLATE_DIR = "/Users/naokitakahashi/beetle-finder/templates"
GUIDE_FILES = sorted(glob.glob(os.path.join(TEMPLATE_DIR, "guide*.html")))

PR_MARKER = "pr-disclosure"  # 重複挿入防止用マーカー

def make_pr_html():
    return (
        '\n<div class="' + PR_MARKER + '" style="'
        'display:inline-flex;align-items:center;gap:6px;'
        'background:#fff8e1;border:1px solid #ffe082;border-radius:6px;'
        'padding:4px 10px;font-size:.7rem;color:#795548;margin:8px 0 16px;'
        '">'
        '<span style="background:#f57f17;color:#fff;font-size:.62rem;font-weight:700;'
        'padding:1px 6px;border-radius:3px">PR</span>'
        'この記事にはプロモーション（広告）が含まれています'
        '</div>\n'
    )

def make_toc_html(headings):
    """headings: list of (id, text)"""
    if len(headings) < 3:
        return ""
    items = "\n".join(
        f'    <li><a href="#{hid}" style="color:#2e7d32;text-decoration:none;font-size:.82rem">'
        f'{text}</a></li>'
        for hid, text in headings
    )
    return (
        '\n<nav class="toc-box" style="'
        'background:#f1f8e9;border:2px solid #c8e6c9;border-radius:10px;'
        'padding:16px 20px;margin:0 0 28px;'
        '">\n'
        '  <div style="font-size:.82rem;font-weight:700;color:#1b5e20;margin-bottom:10px">'
        '📋 この記事の目次</div>\n'
        '  <ol style="margin:0;padding-left:20px;line-height:2">\n'
        f'{items}\n'
        '  </ol>\n'
        '</nav>\n'
    )

def slugify(text):
    """日本語テキストからIDを生成"""
    text = re.sub(r'[^\w぀-ゟ゠-ヿ一-鿿]', '-', text)
    return text.strip('-')[:40] or 'section'

processed = 0
skipped = 0

for filepath in GUIDE_FILES:
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # 既に追加済みならスキップ
    if PR_MARKER in content:
        skipped += 1
        continue

    # BeautifulSoupでパース
    soup = BeautifulSoup(content, 'html.parser')

    # page-subtitle を探す
    subtitle = soup.find(class_='page-subtitle')
    if not subtitle:
        skipped += 1
        continue

    # h2要素を収集してTOC生成
    h2s = soup.find_all('h2', class_='section')
    if not h2s:
        h2s = soup.find_all('h2')  # fallback

    headings = []
    for h2 in h2s:
        text = h2.get_text(strip=True)
        # 絵文字や特殊文字を除去
        text_clean = re.sub(r'[🔦🪲🌿🌙🏕🎒📖🗺🌄🌲🌳🦌🐝⚠️✅❌🔴🟡🟢📋🛒🍬🥅🧺💡🔬🌟⭐☆💰🏆🎯📝🔎🌱🌿🍃💚]', '', text).strip()
        if not text_clean or len(text_clean) < 2:
            continue
        hid = h2.get('id') or slugify(text_clean)
        # idが無ければ付与
        if not h2.get('id'):
            h2['id'] = hid
        headings.append((hid, text_clean[:30]))

    # PR表示とTOCのHTMLを作成
    pr_html = make_pr_html()
    toc_html = make_toc_html(headings)
    insert_html = pr_html + toc_html

    # page-subtitle の直後に挿入（文字列操作）
    # BeautifulSoupのinsert_after使うとインデントが崩れるので文字列で処理
    # page-subtitle タグを特定して後ろに挿入
    subtitle_str = str(subtitle)
    # 最初の一致のみ置換
    new_content = content.replace(subtitle_str, subtitle_str + insert_html, 1)

    if new_content == content:
        skipped += 1
        continue

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    processed += 1
    print(f"✅ {os.path.basename(filepath)}")

print(f"\n完了: {processed}ページ処理, {skipped}ページスキップ")
