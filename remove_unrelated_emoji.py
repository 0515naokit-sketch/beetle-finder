#!/usr/bin/env python3
"""
クワガタ・カブトムシと関係のない絵文字を全ページから削除する。
h2/h3 見出し、ボックスタイトル、フッターナビラベル、種ナビカードを対象とする。
"""
import glob
import re

# ====================================================
# 残す絵文字（クワガタ・自然・採集に関係するもの）
# ====================================================
KEEP = {
    '🪲',  # クワガタ（メイン）
    '🐛',  # 幼虫
    '🦌',  # ノコギリクワガタ（鹿の角 → ノコギリ）
    '🌿',  # 葉・自然
    '🌲',  # 木
    '🌳',  # 木
    '🌱',  # 新芽（産卵・幼虫飼育）
    '🌴',  # ヤシの木（南国・沖縄）
    '🍄',  # キノコ（菌糸ビン）
    '🌙',  # 月（夜間採集）
    '🔦',  # 懐中電灯（採集道具）
    '🪣',  # バケツ（トラップ）
    '🏔',  # 山（生息地）
    '⛰',  # 山
    '🗻',  # 富士山
    '🌋',  # 火山（山岳地帯）
    '🌊',  # 波（野外）
    '🌸',  # 桜（春・季節）
    '🍂',  # 落ち葉（秋・季節）
    '🍁',  # もみじ（秋）
    '🌾',  # 稲穂（里山）
    '🌧',  # 雨（雨の日採集）
    '🌤',  # 晴れ曇り
    '🌄',  # 夜明け（早朝採集）
    '🌅',  # 夕日（夕方）
    '🌑',  # 新月（夜間）
    '🏞',  # 国立公園
    '🦺',  # 安全ベスト（装備）
    '🧥',  # ジャケット（装備）
    '🎒',  # リュック（採集道具）
    '🥾',  # 登山靴（採集装備）
    '🐻',  # クマ（生息地の野生動物・注意）
    '🦟',  # 蚊（虫・採集環境）
    '💧',  # 水（樹液・環境）
    '☔',  # 傘（雨）
    '🌀',  # 台風（天候）
    '🌥',  # 曇り
    '🌰',  # 栗（どんぐり系・食べ物→クワガタの木）
    '⛩',  # 鳥居（採集スポット近く）
    '🏯',  # 城（地域ランドマーク採集記事）
    '🏝',  # 島（沖縄など離島）
}

# 削除対象となる絵文字パターン
EMOJI_RE = re.compile(
    r'[\U0001F000-\U0001FFFF'   # 絵文字メイン
    r'\U00002000-\U00002BFF'    # 補足記号
    r'\U0000203C-\U00002049'    # 感嘆符等
    r'©®'             # ©®
    r']',
    re.UNICODE
)

def remove_unrelated_emoji(text):
    """KEEP以外の絵文字を削除する"""
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        if EMOJI_RE.match(ch) and ch not in KEEP:
            # 後続するバリエーションセレクタも飛ばす
            i += 1
            while i < len(text) and text[i] in '︎️‍':
                i += 1
        else:
            result.append(ch)
            i += 1
    # 先頭・末尾の空白を整える
    return re.sub(r'^\s+', '', ''.join(result))


def process_tag_content(html, tag_pattern, content_transform):
    """
    tag_pattern に一致するタグ内のテキストに content_transform を適用する。
    tag_pattern: タグ全体にマッチする正規表現（group(1)=タグ前半、group(2)=内容）
    """
    def replacer(m):
        before = m.group(1)
        content = m.group(2)
        after = m.group(3)
        return before + content_transform(content) + after
    return re.sub(tag_pattern, replacer, html)


def clean_html(html):
    # ① h2, h3 の見出しテキスト（クラス属性あり）
    html = re.sub(
        r'(<h[23][^>]*>)(.*?)(</h[23]>)',
        lambda m: m.group(1) + remove_unrelated_emoji(m.group(2)).strip() + m.group(3),
        html,
        flags=re.DOTALL
    )

    # ② ボックスタイトル系クラスのdiv/p内テキスト
    BOX_CLASSES = [
        'tip-title', 'warn-title', 'info-title', 'good-title',
        'kids-title', 'rec-title', 'sheet-title', 'toc-title',
        'amz-section-title', 'footer-nav-label', 'diff-badge',
        'stage-name', 'method-title', 'tl-label', 'step-num',
        'section-title', 'rec-name',
    ]
    class_pat = '|'.join(BOX_CLASSES)
    html = re.sub(
        rf'(class="(?:{class_pat})"[^>]*>)(.*?)(</)',
        lambda m: m.group(1) + remove_unrelated_emoji(m.group(2)).strip() + m.group(3),
        html,
        flags=re.DOTALL
    )

    # ③ 種ナビカード（.sn-card）内の非クワガタ絵文字を 🪲 に統一
    # 🦌👑⚔️🏆🦶 → 🪲
    replace_species = {'🦌': '🪲', '👑': '🪲', '⚔': '🪲', '⚔️': '🪲', '🏆': '🪲', '🦶': '🪲'}
    def fix_species_emoji(m):
        inner = m.group(2)
        for old, new in replace_species.items():
            inner = inner.replace(old, new)
        return m.group(1) + inner + m.group(3)
    html = re.sub(
        r'(class="sn-card[^"]*"[^>]*>)(.*?)(</div>)',
        fix_species_emoji,
        html,
        flags=re.DOTALL
    )

    # ④ フッターナビラベルから非クワガタ絵文字を除去
    html = re.sub(
        r'(class="footer-nav-label">)(.*?)(</span>)',
        lambda m: m.group(1) + remove_unrelated_emoji(m.group(2)).strip() + m.group(3),
        html,
        flags=re.DOTALL
    )

    # ⑤ .page-subtitle の絵文字も除去
    html = re.sub(
        r'(class="page-subtitle">)(.*?)(</p>)',
        lambda m: m.group(1) + remove_unrelated_emoji(m.group(2)).strip() + m.group(3),
        html,
        flags=re.DOTALL
    )

    # 連続スペースを整理
    html = re.sub(r'  +', ' ', html)
    return html


files = sorted(glob.glob('templates/*.html'))
updated = 0
for path in files:
    with open(path, encoding='utf-8') as f:
        original = f.read()

    cleaned = clean_html(original)

    if cleaned != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        updated += 1
        print(f'✅ {path}')

print(f'\n完了: {updated}/{len(files)} ファイル更新')
