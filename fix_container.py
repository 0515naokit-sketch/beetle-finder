#!/usr/bin/env python3
"""
全ガイドページの container div 崩れを一括修正

問題: update_pochipp.py の正規表現が amz-section の prod-row 閉じタグを残してしまい、
      コンテナが途中で閉じてしまっていた。

修正方針:
1. container の早期 </div> を探す
2. share-box / footer より明らかに早く閉じている場合は修正
3. 早期 </div> を削除し、share-box の直前に正しい </div> を追加
4. msmaflink ページのみ: 残留 prod-card / amz-note2 も削除
"""

import glob, os, re

TEMPLATE_DIR = "/Users/naokitakahashi/beetle-finder/templates"
files = sorted(glob.glob(os.path.join(TEMPLATE_DIR, "guide*.html")))

def find_container_close(content):
    """container div が char-by-char で最初に depth=0 になる位置を返す"""
    ci = content.find('<div class="container">')
    if ci == -1:
        return None, None
    depth = 0
    i = ci
    while i < len(content):
        if content[i:i+4] == '<div':
            depth += 1; i += 4
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return ci, i  # i は '</div>' の開始位置
            i += 6
        else:
            i += 1
    return ci, None

fixed = 0
skipped = 0

for fp in files:
    with open(fp, encoding='utf-8') as f:
        content = f.read()

    ci, close_pos = find_container_close(content)
    if close_pos is None:
        skipped += 1
        continue

    # share-box または footer の位置
    anchor = content.find('<div class="share-box">')
    if anchor == -1:
        anchor = content.find('<footer>')
    if anchor == -1:
        skipped += 1
        continue

    container_line = content[:close_pos].count('\n') + 1
    anchor_line    = content[:anchor].count('\n') + 1

    # コンテナが share-box より10行以上早く閉じているなら問題
    if anchor_line - container_line <= 10:
        skipped += 1
        continue

    # ── 修正処理 ──────────────────────────────────────────────
    # 1. 早期 </div> を削除（その行ごと）
    #    close_pos は '</div>' の先頭位置
    line_start = content.rfind('\n', 0, close_pos) + 1
    line_end   = content.find('\n', close_pos + 6)
    if line_end == -1:
        line_end = len(content)
    else:
        line_end += 1  # 改行を含む

    # その行が '</div>' しか含まない（空白を除いて）場合のみ削除
    line_content = content[line_start:line_end].strip()
    if line_content != '</div>':
        # 行に他のコンテンツもある場合は </div> だけを削除
        new_content = content[:close_pos] + content[close_pos+6:]
    else:
        new_content = content[:line_start] + content[line_end:]

    # 2. msmaflink ページ: 残留 prod-card ブロックを削除
    #    prod-card div 全体（深さカウント方式）を全部削除
    while '<div class="prod-card">' in new_content:
        m = new_content.find('<div class="prod-card">')
        # anchor より前にある prod-card だけ削除
        if m > new_content.find('<div class="share-box">') if '<div class="share-box">' in new_content else m > new_content.find('<footer>'):
            break
        # div 深さカウントで閉じ位置を探す
        depth = 0
        j = m
        while j < len(new_content):
            if new_content[j:j+4] == '<div':
                depth += 1; j += 4
            elif new_content[j:j+6] == '</div>':
                depth -= 1
                if depth == 0:
                    end = j + 6
                    if end < len(new_content) and new_content[end] == '\n':
                        end += 1
                    break
                j += 6
            else:
                j += 1
        # 直前の改行もまとめて削除
        ls = new_content.rfind('\n', 0, m) + 1
        new_content = new_content[:ls] + new_content[end:]

    # 3. 残留 amz-note2 を削除
    new_content = re.sub(r'\s*<p class="amz-note2">.*?</p>\n?', '\n', new_content, flags=re.DOTALL)

    # 4. share-box / footer の直前に </div> を挿入
    anchor_str = '<div class="share-box">'
    if anchor_str not in new_content:
        anchor_str = '<footer>'
    ai = new_content.find(anchor_str)
    # 直前の行の末尾に挿入
    new_content = new_content[:ai] + '</div>\n' + new_content[ai:]

    with open(fp, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ {os.path.basename(fp)}  (container L{container_line} → L{anchor_line}前に移動)")
    fixed += 1

print(f"\n修正: {fixed}件 / スキップ: {skipped}件")
