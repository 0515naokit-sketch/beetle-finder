"""
アフィリエイトボタンのラベルを改善する
「Amazon」→「Amazon で確認 →」
「楽天」→「楽天 で確認 →」
「Yahoo」→「Yahoo! で確認 →」
※ rec-amz / rec-rkt / rec-yah / amz-btn / rkt-btn / yah-btn クラスのリンク内のみ
"""
import os, re

TEMPLATES_DIR = 'templates'

# パターン: クラス付きの <a> タグ内のテキストだけを置換
# 対象パターン例: class="rec-amz" ...>Amazon<
# シンプルにテキストノード単体 ">Amazon<" などを置換する方針

REPLACEMENTS = [
    # (検索パターン, 置換後)
    (r'(class="rec-amz"[^>]*>)Amazon(<)', r'\1Amazon で確認 →\2'),
    (r'(class="rec-rkt"[^>]*>)楽天(<)',   r'\1楽天 で確認 →\2'),
    (r'(class="rec-yah"[^>]*>)Yahoo(<)',  r'\1Yahoo! で確認 →\2'),
    (r'(class="amz-btn"[^>]*>)Amazonで探す →(<)', r'\1Amazonで価格をチェック →\2'),
    (r'(class="rkt-btn"[^>]*>)楽天(<)',   r'\1楽天 で確認 →\2'),
    (r'(class="yah-btn"[^>]*>)Yahoo!(<)', r'\1Yahoo! で確認 →\2'),
]

updated = 0
total_replacements = 0

for fname in sorted(os.listdir(TEMPLATES_DIR)):
    if not fname.endswith('.html'):
        continue
    path = os.path.join(TEMPLATES_DIR, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content
    file_changes = 0
    for pattern, replacement in REPLACEMENTS:
        new_content, n = re.subn(pattern, replacement, new_content)
        file_changes += n

    if file_changes > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated += 1
        total_replacements += file_changes
        print(f'  ✅ {fname}: {file_changes}箇所')

print(f'\n完了: {updated}ファイル / 計{total_replacements}箇所更新')
