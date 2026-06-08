#!/usr/bin/env python3
"""全コンテンツページに最終更新日を表示するスクリプト"""
import re
import os

TEMPLATES_DIR = "templates"

SKIP_FILES = {
    "404.html", "contact.html", "index.html", "landing.html",
    "terms.html", "privacy.html",  # 既に更新日あり
    "guide_pref.html",  # Jinja2テンプレート
    "guide_pref_index.html",
    "guide_spot.html",
    "guide.html",  # トップナビページ
    "about.html",  # 別形式
}

def date_to_japanese(date_str):
    """2026-05-21 → 2026年5月21日"""
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if not m:
        return None
    y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return f"{y}年{mo}月{d}日"

def process_file(filepath):
    filename = os.path.basename(filepath)
    if filename in SKIP_FILES:
        return False, "スキップ"

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # 既に最終更新日がある場合はスキップ
    if '最終更新' in content and 'class="updated"' in content:
        return False, "既に存在"

    # Jinja2テンプレート変数があるファイルはスキップ
    if '{{ ' in content:
        return False, "Jinja2テンプレート"

    # dateModifiedを取得
    m = re.search(r'"dateModified"\s*:\s*"([^"]+)"', content)
    if not m:
        # datePublishedにフォールバック
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', content)
    if not m:
        return False, "日付なし"

    date_str = m.group(1)
    ja_date = date_to_japanese(date_str)
    if not ja_date:
        return False, "日付パースエラー"

    # h1.page-titleの後に挿入
    # page-subtitleがある場合はその後に、なければh1の後に
    updated_html = f'\n <p class="updated" style="font-size:.8rem;color:#888;margin-bottom:8px">最終更新日：{ja_date}</p>'

    # page-subtitleの後に挿入
    if 'class="page-subtitle"' in content:
        new_content = re.sub(
            r'(<p class="page-subtitle"[^>]*>.*?</p>)',
            r'\1' + updated_html,
            content, count=1, flags=re.DOTALL
        )
    elif 'class="page-title"' in content:
        # h1.page-titleの直後に挿入
        new_content = re.sub(
            r'(<h1 class="page-title"[^>]*>.*?</h1>)',
            r'\1' + updated_html,
            content, count=1, flags=re.DOTALL
        )
    else:
        return False, "挿入ポイントなし"

    if new_content == content:
        return False, "変更なし"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    return True, ja_date

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
    print(f"\n合計 {added} ページに最終更新日を追加しました")

if __name__ == "__main__":
    main()
