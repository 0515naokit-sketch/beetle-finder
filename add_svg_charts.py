#!/usr/bin/env python3
"""
47都道府県ガイドページに「種別採集しやすさチャート」SVGを一括追加するスクリプト
- 各ページの最初の sp-table（種テーブル）を解析して横棒グラフSVGを生成
- SVGがすでに存在するページはスキップ
"""

import re
import glob
import html

# ── 難易度 → スコア・色・ラベル マッピング ─────────────────────────────
def parse_difficulty(text: str) -> tuple[int, str, str]:
    """難易度テキストからスコア・色・ラベルを返す"""
    t = text.strip()
    # 説明文ありパターン
    if '激レア' in t or '超レア' in t:
        return 8,  '#7b1fa2', '激レア'
    if '難' in t and ('★★★' in t or '★★★★' in t):
        return 25, '#e53935', '難'
    if '普通' in t or '★★☆' in t:
        return 55, '#fb8c00', '普通'
    if '易' in t or '★☆☆' in t:
        return 82, '#2e7d32', '易しい'
    # 星のみパターン（例: ★★★★, ★★★, ★★, ★）
    stars = t.count('★')
    if stars >= 4:
        return 8,  '#7b1fa2', '激レア'
    if stars == 3:
        return 25, '#e53935', '難'
    if stars == 2:
        return 55, '#fb8c00', '普通'
    if stars == 1:
        return 82, '#2e7d32', '易しい'
    return 50, '#78909c', '-'

# ── 種名クリーニング ────────────────────────────────────────────────────
def clean_name(raw: str) -> str:
    text = re.sub(r'<[^>]+>', '', raw)
    text = html.unescape(text).strip()
    # カブトムシを短縮しない、括弧除去だけ
    text = re.sub(r'（[^）]*）', '', text).strip()
    return text

# ── SVGチャート生成 ─────────────────────────────────────────────────────
def make_svg(species_data: list[dict], pref_name: str) -> str:
    """
    species_data: [{'name': str, 'score': int, 'color': str, 'label': str}, ...]
    """
    n = len(species_data)
    if n == 0:
        return ''

    ROW_H   = 38      # 1行の高さ
    LABEL_W = 118     # 左ラベル幅
    BAR_AREA = 310    # バー描画エリア幅
    LEGEND_H = 36     # 凡例エリア高さ
    PAD_TOP  = 40     # タイトル+余白
    PAD_BOT  = 8
    TOTAL_H  = PAD_TOP + n * ROW_H + LEGEND_H + PAD_BOT
    TOTAL_W  = LABEL_W + BAR_AREA + 60   # 右マージン

    rows_svg = []
    for i, sp in enumerate(species_data):
        y = PAD_TOP + i * ROW_H
        bar_w = max(4, int(sp['score'] / 100 * BAR_AREA))
        # 背景ゼブラ
        bg = '#f9fdf9' if i % 2 == 0 else '#ffffff'
        score_label = f"{sp['score']}%"
        name = sp['name']
        # 長い名前を省略
        if len(name) > 9:
            name = name[:9] + '…'

        rows_svg.append(f'''
  <!-- row {i}: {sp["name"]} -->
  <rect x="0" y="{y}" width="{TOTAL_W}" height="{ROW_H}" fill="{bg}"/>
  <text x="{LABEL_W - 6}" y="{y + ROW_H//2 + 5}" text-anchor="end"
        font-size="12" fill="#333" font-family="'Hiragino Sans','Meiryo',sans-serif">{name}</text>
  <rect x="{LABEL_W}" y="{y + 9}" width="{bar_w}" height="{ROW_H - 18}"
        fill="{sp['color']}" rx="3" opacity="0.88"/>
  <text x="{LABEL_W + bar_w + 6}" y="{y + ROW_H//2 + 5}"
        font-size="11" fill="{sp['color']}" font-weight="bold"
        font-family="'Hiragino Sans','Meiryo',sans-serif">{sp['label']}</text>''')

    # 凡例
    LEG_Y = PAD_TOP + n * ROW_H + 10
    legend_items = [
        ('#2e7d32', '易しい'),
        ('#fb8c00', '普通'),
        ('#e53935', '難'),
        ('#7b1fa2', '激レア'),
    ]
    legend_svg = ''
    lx = LABEL_W
    for color, lbl in legend_items:
        legend_svg += f'<rect x="{lx}" y="{LEG_Y}" width="12" height="12" fill="{color}" rx="2"/>'
        legend_svg += f'<text x="{lx+16}" y="{LEG_Y+11}" font-size="10" fill="#666" font-family="\'Hiragino Sans\',\'Meiryo\',sans-serif">{lbl}</text>'
        lx += 68

    svg = f'''<figure style="margin:16px 0 24px;background:#fff;border:1px solid #c8e6c9;border-radius:10px;overflow:hidden;padding:0">
  <figcaption style="background:#e8f5e9;padding:9px 16px;font-size:.82rem;font-weight:700;color:#1b5e20;border-bottom:1px solid #c8e6c9">
    📊 {pref_name}で採れる主な種の採集しやすさ
  </figcaption>
  <div style="overflow-x:auto;-webkit-overflow-scrolling:touch">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TOTAL_W} {TOTAL_H}"
       width="100%" style="max-width:{TOTAL_W}px;display:block;min-width:360px"
       role="img" aria-label="{pref_name}のクワガタ採集しやすさチャート">
  <title>{pref_name}のクワガタ・カブトムシ 採集しやすさチャート</title>
  <!-- タイトル行背景 -->
  <rect x="0" y="0" width="{TOTAL_W}" height="{PAD_TOP - 4}" fill="#f1f8e9"/>
  <text x="{LABEL_W - 6}" y="26" text-anchor="end" font-size="11" fill="#666"
        font-family="'Hiragino Sans','Meiryo',sans-serif">種名</text>
  <text x="{LABEL_W}" y="26" font-size="11" fill="#666"
        font-family="'Hiragino Sans','Meiryo',sans-serif">←  採集しにくい　　採集しやすい  →</text>
  <!-- 目盛り線 -->
  <line x1="{LABEL_W}" y1="{PAD_TOP - 4}" x2="{LABEL_W}" y2="{PAD_TOP + n * ROW_H}" stroke="#e0e0e0" stroke-width="1"/>
  <line x1="{LABEL_W + BAR_AREA}" y1="{PAD_TOP - 4}" x2="{LABEL_W + BAR_AREA}" y2="{PAD_TOP + n * ROW_H}" stroke="#e0e0e0" stroke-width="1" stroke-dasharray="4,3"/>
  {''.join(rows_svg)}
  <!-- 凡例 -->
  <rect x="0" y="{LEG_Y - 4}" width="{TOTAL_W}" height="{LEGEND_H}" fill="#fafafa"/>
  {legend_svg}
  </svg>
  </div>
</figure>'''
    return svg

# ── メイン処理 ──────────────────────────────────────────────────────────

# pref名マッピング（ファイル名 → 都道府県名）
PREF_NAMES = {
    'hokkaido': '北海道', 'aomori': '青森県', 'iwate': '岩手県',
    'miyagi': '宮城県', 'akita': '秋田県', 'yamagata': '山形県',
    'fukushima': '福島県', 'ibaraki': '茨城県', 'tochigi': '栃木県',
    'gunma': '群馬県', 'saitama': '埼玉県', 'chiba': '千葉県',
    'tokyo': '東京都', 'kanagawa': '神奈川県', 'niigata': '新潟県',
    'toyama': '富山県', 'ishikawa': '石川県', 'fukui': '福井県',
    'yamanashi': '山梨県', 'nagano': '長野県', 'gifu': '岐阜県',
    'shizuoka': '静岡県', 'aichi': '愛知県', 'mie': '三重県',
    'shiga': '滋賀県', 'kyoto': '京都府', 'osaka': '大阪府',
    'hyogo': '兵庫県', 'nara': '奈良県', 'wakayama': '和歌山県',
    'tottori': '鳥取県', 'shimane': '島根県', 'okayama': '岡山県',
    'hiroshima': '広島県', 'yamaguchi': '山口県', 'tokushima': '徳島県',
    'kagawa': '香川県', 'ehime': '愛媛県', 'kochi': '高知県',
    'fukuoka': '福岡県', 'saga': '佐賀県', 'nagasaki': '長崎県',
    'kumamoto': '熊本県', 'oita': '大分県', 'miyazaki': '宮崎県',
    'kagoshima': '鹿児島県', 'okinawa': '沖縄県',
}

# sp-table（種テーブル）を解析してSVGを挿入
def process_file(filepath: str) -> bool:
    pref_key = re.search(r'guide_pref_(\w+)\.html', filepath)
    if not pref_key:
        return False
    pref_key = pref_key.group(1)
    pref_name = PREF_NAMES.get(pref_key, pref_key)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # すでにSVGが挿入済みならスキップ
    if '<figure' in content and 'figcaption' in content and '採集しやすさ' in content:
        print(f'  SKIP (already done): {filepath}')
        return False

    # 最初の sp-table を探す（種テーブル＝ヘッダーに「種名」がある方）
    # パターン: <table class="sp-table"> ... </table>
    table_pattern = re.compile(
        r'(<table class="sp-table">)(.*?)(</table>)',
        re.DOTALL
    )
    matches = list(table_pattern.finditer(content))
    if not matches:
        print(f'  WARNING: no sp-table found in {filepath}')
        return False

    # 最初のテーブルで「種」「種名」「種類」ヘッダーを持つものを探す
    SPECIES_HEADERS = {'<th>種名</th>', '<th>種</th>', '<th>種類</th>'}
    species_table_match = None
    species_col_idx = 0
    diff_col_idx    = 1
    for m in matches:
        header_check = m.group(2)
        matched_header = next((h for h in SPECIES_HEADERS if h in header_check), None)
        if matched_header:
            # ヘッダー行からカラムインデックスを取得
            header_row = re.search(r'<tr>(.*?)</tr>', header_check, re.DOTALL)
            if header_row:
                ths = re.findall(r'<th[^>]*>(.*?)</th>', header_row.group(1))
                for idx, th_text in enumerate(ths):
                    clean_th = re.sub(r'<[^>]+>', '', th_text).strip()
                    if clean_th in ('種', '種名', '種類'):
                        species_col_idx = idx
                    if '難易度' in clean_th:
                        diff_col_idx = idx
            species_table_match = m
            break

    if not species_table_match:
        print(f'  WARNING: no species table found in {filepath}')
        return False

    # テーブル内の行を解析（ヘッダー行除く）
    table_body = species_table_match.group(2)
    row_pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
    species_list = []

    for row_m in row_pattern.finditer(table_body):
        row_html = row_m.group(1)
        if '<th>' in row_html:
            continue  # ヘッダー行スキップ
        # td を抽出
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
        if len(tds) <= max(species_col_idx, diff_col_idx):
            continue
        name_raw  = tds[species_col_idx]
        diff_raw  = tds[diff_col_idx]
        name      = clean_name(name_raw)
        diff_text = re.sub(r'<[^>]+>', '', diff_raw)
        score, color, label = parse_difficulty(diff_text)
        if name:
            species_list.append({
                'name':  name,
                'score': score,
                'color': color,
                'label': label,
            })

    if not species_list:
        print(f'  WARNING: no species rows parsed in {filepath}')
        return False

    # SVG生成
    svg_html = make_svg(species_list, pref_name)

    # テーブルの直後に挿入
    insert_pos = species_table_match.end()
    new_content = content[:insert_pos] + '\n' + svg_html + content[insert_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  OK ({len(species_list)} species): {filepath}')
    return True


if __name__ == '__main__':
    files = sorted(glob.glob('templates/guide_pref_*.html'))
    print(f'処理対象: {len(files)} ファイル')
    updated = 0
    for fp in files:
        if process_file(fp):
            updated += 1
    print(f'\n完了: {updated}/{len(files)} ファイルを更新しました')
