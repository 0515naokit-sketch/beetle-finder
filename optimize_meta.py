"""
optimize_meta.py
────────────────────────────────────────────────────────────────
都道府県ページのtitle・meta descriptionを検索クリック率向上のため最適化。

【変換内容】
A) 旧フォーマット（34ページ）
   変更前: ○○県クワガタ採集ガイド｜地名のスポット完全解説
   変更後: ○○県のクワガタ採集スポット｜地名で採れる種・時期・場所まとめ【2026年】

   description変更前: ○○県でクワガタを採るなら地名...
   description変更後: ○○県でクワガタ・カブトムシが採れる場所を徹底解説。地名...

B) 年なしフォーマット（4ページ）
   変更前: ...まとめ
   変更後: ...まとめ【2026年】

C) ガイドページ（2ページ）
   guide_kids, guide_tools のタイトルを年付きに統一
"""

import re
import glob
import os

TEMPLATES_DIR = "templates"


# ── A) 旧フォーマット都道府県ページ ───────────────────────────────────────────
def fix_old_format(filepath, content):
    """
    "○○県クワガタ採集ガイド｜地名のスポット完全解説"
    → "○○県のクワガタ採集スポット｜地名で採れる種・時期・場所まとめ【2026年】"
    """
    # タイトル変換
    m = re.search(r'<title>(.+?)県クワガタ採集ガイド｜(.+?)のスポット完全解説</title>', content)
    if not m:
        return content, False

    pref = m.group(1)
    locations = m.group(2)

    new_title = f'<title>{pref}県のクワガタ採集スポット｜{locations}で採れる種・時期・場所まとめ【2026年】</title>'
    content = re.sub(
        r'<title>.+?県クワガタ採集ガイド｜.+?のスポット完全解説</title>',
        new_title,
        content,
        count=1
    )

    # og:title があれば同様に変換
    content = re.sub(
        r'(<meta property="og:title" content=")(.+?)県クワガタ採集ガイド｜(.+?)のスポット完全解説(")',
        lambda m2: f'{m2.group(1)}{m2.group(2)}県のクワガタ採集スポット｜{m2.group(3)}で採れる種・時期・場所まとめ{m2.group(4)}',
        content,
        count=1
    )

    # twitter:title も同様
    content = re.sub(
        r'(<meta name="twitter:title" content=")(.+?)県クワガタ採集ガイド｜(.+?)のスポット完全解説(")',
        lambda m2: f'{m2.group(1)}{m2.group(2)}県のクワガタ採集スポット｜{m2.group(3)}で採れる種・時期・場所まとめ{m2.group(4)}',
        content,
        count=1
    )

    # description変換:
    # "○○県でクワガタを採るなら地名A・地名B..." 全体を新フォーマットで置換
    # → "○○県でクワガタ・カブトムシが採れる場所を徹底解説。地名A・地名B..."
    content = re.sub(
        rf'(content="){re.escape(pref)}県でクワガタを採るなら',
        f'content="{pref}県でクワガタ・カブトムシが採れる場所を徹底解説。',
        content,
        count=1
    )

    return content, True


# ── B) 年なしフォーマット ─────────────────────────────────────────────────────
def fix_missing_year(filepath, content):
    """
    "のクワガタ採集スポット｜...まとめ" → "...まとめ【2026年】"
    """
    if '【2026年】' in content:
        return content, False
    if 'のクワガタ採集スポット' not in content:
        return content, False

    # title タグ
    content = re.sub(
        r'(<title>.*?まとめ)(</title>)',
        r'\1【2026年】\2',
        content,
        count=1
    )

    return content, True


# ── C) ガイドページ個別修正 ──────────────────────────────────────────────────
GUIDE_FIXES = {
    "guide_kids.html": {
        "title_old": "子供・家族でクワガタ採集ガイド | 安全な場所・準備・楽しみ方",
        "title_new": "子供・家族でクワガタ採集｜安全な場所・準備・楽しみ方【2026年】",
        "desc_old":  "子供と一緒にクワガタ・カブトムシ採集を楽しむガイド。",
        "desc_new":  "子供と一緒にクワガタ・カブトムシ採集を楽しもう！",
    },
    "guide_tools.html": {
        "title_old": "クワガタ採集 道具おすすめガイド | ヘッドライト・虫かご・ライトトラップ選び方",
        "title_new": "クワガタ採集 道具おすすめガイド｜ヘッドライト・虫かご・ライトトラップ選び方【2026年】",
        "desc_old":  None,
        "desc_new":  None,
    },
}


def fix_guide_page(filepath, content):
    name = os.path.basename(filepath)
    fix = GUIDE_FIXES.get(name)
    if not fix:
        return content, False

    changed = False
    if fix["title_old"] in content:
        content = content.replace(fix["title_old"], fix["title_new"], 1)
        changed = True
    if fix.get("desc_old") and fix["desc_old"] in content:
        content = content.replace(fix["desc_old"], fix["desc_new"], 1)
        changed = True

    return content, changed


# ── メイン ────────────────────────────────────────────────────────────────────
def process_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    changed = False

    name = os.path.basename(filepath)

    if name.startswith("guide_pref_"):
        # 旧フォーマット判定
        if re.search(r'<title>.+?県クワガタ採集ガイド｜.+?のスポット完全解説</title>', content):
            content, ch = fix_old_format(filepath, content)
            changed = changed or ch
        # 年なし判定
        elif 'のクワガタ採集スポット' in content and '【2026年】' not in content:
            content, ch = fix_missing_year(filepath, content)
            changed = changed or ch
    else:
        content, ch = fix_guide_page(filepath, content)
        changed = changed or ch

    if changed and content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def main():
    targets = sorted(glob.glob(os.path.join(TEMPLATES_DIR, "guide_pref_*.html")))
    targets += [
        os.path.join(TEMPLATES_DIR, "guide_kids.html"),
        os.path.join(TEMPLATES_DIR, "guide_tools.html"),
    ]

    updated = []
    skipped = []

    for fp in targets:
        ok = process_file(fp)
        if ok:
            updated.append(os.path.basename(fp))
            print(f"  ✓ {os.path.basename(fp)}")
        else:
            skipped.append(os.path.basename(fp))

    print(f"\n更新: {len(updated)}ページ / スキップ: {len(skipped)}ページ")


if __name__ == "__main__":
    main()
