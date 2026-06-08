#!/usr/bin/env python3
"""
Wrap Amazon prod-img tags with a fallback container.
If Amazon image loads → shows image.
If it fails → shows emoji fallback (onerror hides the img).
Also injects the necessary CSS into each affected page.
"""

import os
import re

TEMPLATES_DIR = "/Users/naokitakahashi/beetle-finder/templates"

# Emoji mapping by ASIN
ASIN_EMOJI = {
    'B09MT2GZDF': '🔦',
    'B09324G799': '🔦',
    'B08BJ8YC84': '🏕️',
    'B0CDCQ4X8Y': '🦗',
    'B07BDMV6YN': '🌿',  # 発酵マット
    'B07WKWBYK8': '🍄',  # 菌糸ビン
}
DEFAULT_EMOJI = '🛒'

CSS_INJECT = """
 .prod-img-wrap{display:flex;align-items:center;justify-content:center;width:100%;height:160px;background:#f0f7f0;border-radius:10px;margin:0 auto 10px;overflow:hidden;position:relative}
 .prod-img{width:160px;height:160px;object-fit:contain;border-radius:8px;display:block}
 .prod-img-fb{font-size:3.5rem;line-height:1;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);pointer-events:none}"""

def extract_asin(src):
    m = re.search(r'ASIN=([A-Z0-9]+)', src)
    return m.group(1) if m else None

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Find all prod-img tags and wrap them
    def replace_img(m):
        tag = m.group(0)
        src_match = re.search(r'src="([^"]+)"', tag)
        if not src_match:
            return tag
        src = src_match.group(1)
        asin = extract_asin(src)
        emoji = ASIN_EMOJI.get(asin, DEFAULT_EMOJI)

        # Build new img tag with onerror
        # Add onerror to hide img if it fails (emoji underneath shows through)
        new_tag = tag.replace('<img ', '<img onerror="this.style.opacity=\'0\'" ')
        if 'onerror' in tag:
            new_tag = tag  # already has onerror

        return f'<div class="prod-img-wrap"><span class="prod-img-fb">{emoji}</span>{new_tag}</div>'

    # Match prod-img img tags (not already wrapped)
    pattern = r'<img class="prod-img"[^>]+>'
    # Only wrap if not already inside prod-img-wrap
    if 'prod-img-wrap' not in content:
        content = re.sub(pattern, replace_img, content)

    # Inject CSS if not present
    if 'prod-img-wrap' in content and '.prod-img-wrap{' not in content:
        # Inject before </style>
        content = content.replace('</style>', CSS_INJECT + '\n </style>', 1)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

changed = []
for fname in os.listdir(TEMPLATES_DIR):
    if fname.endswith('.html'):
        path = os.path.join(TEMPLATES_DIR, fname)
        if process_file(path):
            changed.append(fname)

print(f"Changed {len(changed)} files:")
for f in sorted(changed):
    print(f"  {f}")
