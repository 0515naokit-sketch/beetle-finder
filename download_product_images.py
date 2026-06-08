#!/usr/bin/env python3
"""
Download Amazon product images and save locally.
Then update all templates to use local paths instead of Amazon widget URLs.
"""

import os
import re
import urllib.request
import urllib.error

STATIC_DIR = "/Users/naokitakahashi/beetle-finder/static/img/products"
TEMPLATES_DIR = "/Users/naokitakahashi/beetle-finder/templates"

os.makedirs(STATIC_DIR, exist_ok=True)

# ASIN → filename mapping
PRODUCTS = {
    'B09MT2GZDF': 'gentos_gh200rg.jpg',
    'B09324G799': 'gentos_cp195db.jpg',
    'B08BJ8YC84': 'mushikago_loupe.jpg',
    'B0CDCQ4X8Y': 'konchu_set.jpg',
}

# Amazon product image URL formats to try (in order)
def get_image_urls(asin):
    return [
        # SiteStripe widget URL (original)
        f"https://ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN={asin}&Format=_SL200_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=beetlefinder-22",
        # Media Amazon direct
        f"https://m.media-amazon.com/images/P/{asin}.jpg",
    ]

def download_image(asin, filename):
    dest = os.path.join(STATIC_DIR, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"  Already exists: {filename}")
        return True

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://beetle-finder.onrender.com/',
    }

    for url in get_image_urls(asin):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if len(data) > 1000:  # real image, not an error page
                    with open(dest, 'wb') as f:
                        f.write(data)
                    print(f"  Downloaded: {filename} ({len(data)//1024}KB) from {url[:60]}")
                    return True
                else:
                    print(f"  Too small ({len(data)}B): {url[:60]}")
        except Exception as e:
            print(f"  Failed: {url[:60]} → {e}")

    print(f"  FAILED all URLs for {asin}")
    return False

print("=== Downloading product images ===")
success = {}
for asin, filename in PRODUCTS.items():
    print(f"\nASIN {asin} → {filename}")
    ok = download_image(asin, filename)
    success[asin] = ok

print("\n=== Updating templates ===")

def update_templates():
    changed = []
    for fname in os.listdir(TEMPLATES_DIR):
        if not fname.endswith('.html'):
            continue
        path = os.path.join(TEMPLATES_DIR, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Replace Amazon widget URLs with local paths
        for asin, filename in PRODUCTS.items():
            if not success.get(asin):
                continue
            local_url = f"/static/img/products/{filename}"
            widget_url = f"https://ws-fe.amazon-adsystem.com/widgets/q?_encoding=UTF8&ASIN={asin}&Format=_SL200_&ID=AsinImage&MarketPlace=JP&ServiceVersion=20070822&WS=1&tag=beetlefinder-22"
            if widget_url in content:
                content = content.replace(widget_url, local_url)

        if content != original:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            changed.append(fname)

    print(f"Updated {len(changed)} files:")
    for f in sorted(changed):
        print(f"  {f}")

update_templates()
