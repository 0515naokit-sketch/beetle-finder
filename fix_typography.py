#!/usr/bin/env python3
"""
全ガイドページの文字サイズ・行間・余白を一括改善するスクリプト

変更点：
  body  line-height  1.8/1.85 → 1.95
  p     font-size    .9x rem  → 1rem
  p     margin-bottom 12px   → 1.4em
  li    margin-bottom 4-6px  → 0.6em
  ul,ol margin-bottom 14px   → 1.3em
  h2.section margin-top      32px → 40px
  h3.sub margin-top          18px → 24px
  コールアウトボックス padding  14px → 16px 18px → 20px
"""

import glob, re

def replace_rule(css: str, selector_pat: str, prop: str, old_vals, new_val: str) -> str:
    """セレクタブロック内の特定プロパティを置換"""
    def replacer(m):
        block = m.group(0)
        for old in old_vals:
            block = block.replace(f'{prop}:{old}', f'{prop}:{new_val}')
        return block
    return re.sub(selector_pat, replacer, css)

def fix_typography(content: str) -> str:
    # ── body line-height ─────────────────────────────────
    content = re.sub(
        r'(body\{[^}]*line-height:)1\.8(?:5)?',
        r'\g<1>1.95',
        content
    )

    # ── p の本文フォントサイズ (.9xrem → 1rem) ───────────
    # p{...} ブロック内のみ対象（コンポーネント個別指定は除外）
    def fix_p_block(m):
        block = m.group(0)
        # font-size: .8x〜.95rem を 1rem に
        block = re.sub(r'font-size:\.9[0-9]rem', 'font-size:1rem', block)
        block = re.sub(r'font-size:\.9rem', 'font-size:1rem', block)
        # margin-bottom: 12px → 1.4em
        block = block.replace('margin-bottom:12px', 'margin-bottom:1.4em')
        return block
    # セレクタが "p{" または "p " で始まるブロック（子孫セレクタは除外）
    content = re.sub(r'\bp\{[^}]+\}', fix_p_block, content)

    # ── li margin-bottom ─────────────────────────────────
    def fix_li_block(m):
        block = m.group(0)
        block = re.sub(r'font-size:\.9[0-9]rem', 'font-size:1rem', block)
        block = re.sub(r'font-size:\.9rem', 'font-size:1rem', block)
        block = re.sub(r'margin-bottom:[456]px', 'margin-bottom:.6em', block)
        return block
    content = re.sub(r'\bli\{[^}]+\}', fix_li_block, content)

    # ── ul,ol margin-bottom ──────────────────────────────
    def fix_ul_block(m):
        block = m.group(0)
        block = block.replace('margin-bottom:14px', 'margin-bottom:1.3em')
        block = block.replace('margin-bottom:12px', 'margin-bottom:1.3em')
        return block
    content = re.sub(r'\bul(?:,ol)?\{[^}]+\}', fix_ul_block, content)
    content = re.sub(r'\bol(?:,ul)?\{[^}]+\}', fix_ul_block, content)

    # ── h2.section margin-top 32px → 40px ───────────────
    content = re.sub(
        r'(h2\.section\{[^}]*margin:)32px(\s+0\s+\d+px)',
        r'\g<1>40px\2',
        content
    )
    content = re.sub(
        r'(h2\.section\{[^}]*margin:)36px(\s+0\s+\d+px)',
        r'\g<1>40px\2',
        content
    )

    # ── h3.sub margin-top 18px → 24px ───────────────────
    content = re.sub(
        r'(h3(?:\.sub)?\{[^}]*margin:)18px(\s+0\s+\d+px)',
        r'\g<1>24px\2',
        content
    )

    # ── コールアウトボックス padding 拡大 ────────────────
    # tip-box / warn-box / info-box / danger-box
    for box_cls in ['tip-box', 'warn-box', 'info-box', 'danger-box', 'faq-box', 'intro-box']:
        content = re.sub(
            rf'(\.{box_cls}\{{[^}}]*padding:)14px 18px',
            rf'\g<1>18px 22px',
            content
        )
        content = re.sub(
            rf'(\.{box_cls}\{{[^}}]*padding:)14px 16px',
            rf'\g<1>18px 20px',
            content
        )
        content = re.sub(
            rf'(\.{box_cls}\{{[^}}]*padding:)10px 14px',
            rf'\g<1>14px 18px',
            content
        )

    return content

files = sorted(glob.glob('/Users/naokitakahashi/beetle-finder/templates/guide*.html'))
updated = 0

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        original = f.read()
    
    fixed = fix_typography(original)
    
    if fixed != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(fixed)
        print(f'  OK: {fp.split("/")[-1]}')
        updated += 1
    else:
        print(f'  --: {fp.split("/")[-1]}')

print(f'\n完了: {updated}/{len(files)} ファイルを更新')
