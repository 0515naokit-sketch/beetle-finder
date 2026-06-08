#!/usr/bin/env python3
"""
Improve readability across all guide and report templates.
Changes:
- h2.section: 1.2rem → 1.4rem, increase bottom margin
- h3.sub: 1rem → 1.15rem
- container max-width: 800px → 720px (easier to read)
- body line-height: 1.85/1.95 → 2.0
- Add margin-top to h2 paragraphs that follow
- tip/warn box padding improvements
"""

import os
import re

TEMPLATES_DIR = "/Users/naokitakahashi/beetle-finder/templates"

replacements = [
    # h2.section font-size: 1.2rem → 1.4rem, tighter letter-spacing
    (r'h2\.section\{font-size:1\.2rem;', 'h2.section{font-size:1.4rem;'),
    # h2 bottom margin too tight: margin:40px 0 12px → margin:44px 0 16px
    (r'margin:40px 0 12px\}', 'margin:44px 0 16px}'),
    # h3.sub font-size: 1rem → 1.15rem
    (r'h3\.sub\{font-size:1rem;', 'h3.sub{font-size:1.15rem;'),
    # Container max-width: 800px → 720px
    (r'max-width:800px;', 'max-width:720px;'),
    (r'max-width:780px;', 'max-width:720px;'),
    (r'max-width:820px;', 'max-width:720px;'),
    (r'max-width:760px;', 'max-width:720px;'),
    # Body line-height: 1.85 → 2.0
    (r'line-height:1\.85\}', 'line-height:2.0}'),
    # Body line-height: 1.95 → 2.0
    (r'line-height:1\.95\}', 'line-height:2.0}'),
    # p font-size still .9rem → 1rem (some pages)
    (r'p\{margin-bottom:12px;font-size:\.9rem\}', 'p{margin-bottom:1.4em;font-size:1rem}'),
    (r'p\{margin-bottom:1\.4em;font-size:\.9rem\}', 'p{margin-bottom:1.4em;font-size:1rem}'),
    # ul,ol font-size .9rem → 1rem
    (r'ul,ol\{margin:0 0 12px 20px;font-size:\.9rem\}', 'ul,ol{padding-left:22px;margin-bottom:1.3em}'),
    (r'ul,ol\{padding-left:22px;margin-bottom:1\.3em;font-size:\.9rem\}', 'ul,ol{padding-left:22px;margin-bottom:1.3em}'),
    # li font-size .9rem → 1rem
    (r'li\{margin-bottom:\.6em;font-size:\.9rem\}', 'li{margin-bottom:.7em;font-size:1rem}'),
    (r'li\{margin-bottom:\.5em;font-size:\.9rem\}', 'li{margin-bottom:.7em;font-size:1rem}'),
    # Increase container padding
    (r'padding:24px 16px 60px\}', 'padding:28px 20px 72px}'),
    (r'padding:28px 16px 60px\}', 'padding:28px 20px 72px}'),
]

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

changed = []
for fname in os.listdir(TEMPLATES_DIR):
    if fname.startswith('guide') or fname.startswith('report'):
        path = os.path.join(TEMPLATES_DIR, fname)
        if fix_file(path):
            changed.append(fname)

print(f"Changed {len(changed)} files:")
for f in sorted(changed):
    print(f"  {f}")
