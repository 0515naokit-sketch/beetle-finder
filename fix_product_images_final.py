#!/usr/bin/env python3
"""
1. Download actual product images from Amazon CDN (m.media-amazon.com)
2. Save locally to /static/img/products/
3. Update all templates:
   - Replace Amazon widget URLs with local paths
   - Remove emoji fallback wrappers (prod-img-wrap / prod-img-fb)
   - Keep clean <img class="prod-img"> tags
"""

import os
import re
import urllib.request

STATIC_DIR = "/Users/naokitakahashi/beetle-finder/static/img/products"
TEMPLATES_DIR = "/Users/naokitakahashi/beetle-finder/templates"

os.makedirs(STATIC_DIR, exist_ok=True)

# Product image URLs from もしもアフィリエイト かんたんリンク
PRODUCTS = {
    'B09MT2GZDF': ('gentos_gh200rg.jpg',    'https://m.media-amazon.com/images/I/41dTwd-JbZL._SL500_.jpg'),
    'B09324G799': ('gentos_cp195db.jpg',     'https://m.media-amazon.com/images/I/41orin7+ufS._SL500_.jpg'),
    'B08BJ8YC84': ('mushikago_loupe.jpg',    'https://m.media-amazon.com/images/I/41FJQcr-j+L._SL500_.jpg'),
    'B0CDCQ4X8Y': ('konchu_set.jpg',         'https://m.media-amazon.com/images/I/51xx5wOsmFL._SL500_.jpg'),
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://beetle-finder.onrender.com/',
}

print("=== Downloading images ===")
for asin, (filename, url) in PRODUCTS.items():
    dest = os.path.join(STATIC_DIR, filename)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        if len(data) > 5000:
            with open(dest, 'wb') as f:
                f.write(data)
            print(f"  OK: {filename} ({len(data)//1024}KB)")
        else:
            print(f"  SKIP (too small {len(data)}B): {filename}")
    except Exception as e:
        print(f"  ERROR: {filename} -> {e}")

print("\n=== Updating templates ===")

# Build replacement map: old widget URL -> local path
widget_to_local = {}
for asin, (filename, _) in PRODUCTS.items():
    old = f"https://ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN={asin}&Format=_SL200_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=beetlefinder-22"
    new = f"/static/img/products/{filename}"
    widget_to_local[old] = new

changed = []
for fname in os.listdir(TEMPLATES_DIR):
    if not fname.endswith('.html'):
        continue
    path = os.path.join(TEMPLATES_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Replace widget URLs with local paths
    for old, new in widget_to_local.items():
        content = content.replace(old, new)

    # 2. Remove emoji fallback wrapper: <div class="prod-img-wrap"><span class="prod-img-fb">EMOJI</span>IMG</div>
    # Pattern: <div class="prod-img-wrap"><span class="prod-img-fb">...</span><img ...></div>
    content = re.sub(
        r'<div class="prod-img-wrap"><span class="prod-img-fb">[^<]*</span>(<img [^>]+>)</div>',
        r'\1',
        content
    )

    # 3. Remove onerror attribute we added
    content = re.sub(r' onerror="this\.style\.opacity=\'0\'"', '', content)

    # 4. Remove the injected prod-img-wrap CSS block
    content = re.sub(
        r'\n \.prod-img-wrap\{[^\n]+\}\n \.prod-img\{[^\n]+\}\n \.prod-img-fb\{[^\n]+\}',
        '',
        content
    )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        changed.append(fname)

print(f"Updated {len(changed)} files:")
for f in sorted(changed):
    print(f"  {f}")
