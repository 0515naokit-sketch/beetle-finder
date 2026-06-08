"""
static/js/track.js を全テンプレートの </body> 直前に挿入する
すでに挿入済みのファイルはスキップ
"""
import os, re

TEMPLATES_DIR = 'templates'
SCRIPT_TAG = '<script src="/static/js/track.js"></script>'

inserted = 0
skipped = 0
error = 0

for fname in sorted(os.listdir(TEMPLATES_DIR)):
    if not fname.endswith('.html'):
        continue
    path = os.path.join(TEMPLATES_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'track.js' in content:
        skipped += 1
        continue

    if '</body>' not in content:
        error += 1
        print(f'  ⚠ </body> なし: {fname}')
        continue

    # </body> の直前に挿入
    new_content = content.replace('</body>', f'{SCRIPT_TAG}\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    inserted += 1

print(f'\n完了: 挿入={inserted} / スキップ={skipped} / エラー={error}')
