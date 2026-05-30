#!/usr/bin/env python3
"""
47都道府県ページに種別Wikimedia Commons写真を追加するスクリプト
- 各ページの最初の種（sp-table先頭行）に対応する写真を挿入
- SVGチャート（<figure>）の直後に挿入
- 写真がすでに挿入済みのページはスキップ
"""

import re
import glob

# ── 種別 → 写真情報マッピング ──────────────────────────────────────────
SPECIES_PHOTO = {
    'ミヤマクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Lucanus_maculifemoratus_male.jpg/640px-Lucanus_maculifemoratus_male.jpg',
        'alt':     'ミヤマクワガタのオス（Lucanus maculifemoratus）',
        'caption': 'ミヤマクワガタのオス（Lucanus maculifemoratus）— 大きな大顎と頭部の突起が特徴。標高600m以上の冷涼な山地に生息する夏を代表するクワガタ。',
        'credit':  'CC BY-SA 3.0 / OpenCage',
    },
    'ノコギリクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Prosopocoilus_inclinatus_male_20101003.jpg/640px-Prosopocoilus_inclinatus_male_20101003.jpg',
        'alt':     'ノコギリクワガタのオス（Prosopocoilus inclinatus）',
        'caption': 'ノコギリクワガタのオス（Prosopocoilus inclinatus）— ギザギザの大顎が名前の由来。平地〜低山地の雑木林に広く生息する定番種。',
        'credit':  'CC BY-SA 3.0 / Alpsdake',
    },
    'コクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Dorcus_rectus_01.JPG/640px-Dorcus_rectus_01.JPG',
        'alt':     'コクワガタのオス（Dorcus rectus）',
        'caption': 'コクワガタのオス（Dorcus rectus）— 日本で最も広く生息する採集しやすいクワガタ。細身の黒い体と緩やかな大顎が特徴。',
        'credit':  'CC BY-SA 3.0 / Σ64',
    },
    'ヒラタクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Dorcus_titanus_pilifer.jpg/640px-Dorcus_titanus_pilifer.jpg',
        'alt':     'ヒラタクワガタのオス（Dorcus titanus pilifer）',
        'caption': 'ヒラタクワガタのオス（Dorcus titanus pilifer）— 扁平な体と強力な大顎が特徴。河川沿いの低地に生息する力自慢の種。',
        'credit':  'CC BY-SA 3.0 / Chia-Chi Ho',
    },
    'カブトムシ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Kabutomushi-20070710.jpg/640px-Kabutomushi-20070710.jpg',
        'alt':     'カブトムシのオス（Trypoxylus dichotomus）',
        'caption': 'カブトムシのオス（Trypoxylus dichotomus）— 立派な角が特徴の「昆虫の王者」。クヌギ・コナラの樹液に集まり夜間に採集できる。',
        'credit':  'CC BY 2.0 / Joi Ito',
    },
    'オオクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Dorcus_hopei_binodulosus01.jpg/640px-Dorcus_hopei_binodulosus01.jpg',
        'alt':     'オオクワガタのオス（Dorcus hopei binodulosus）',
        'caption': 'オオクワガタのオス（Dorcus hopei binodulosus）— 「黒いダイヤ」とも呼ばれる幻のクワガタ。採集難易度は最高レベル。',
        'credit':  'CC BY-SA 3.0 / Alpsdake',
    },
    'アカアシクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/Dorcus_rubrofemoratus.jpg/640px-Dorcus_rubrofemoratus.jpg',
        'alt':     'アカアシクワガタのオス（Dorcus rubrofemoratus）',
        'caption': 'アカアシクワガタのオス（Dorcus rubrofemoratus）— 脚の付け根の赤みが名前の由来。ブナ帯の高山に生息する希少種。',
        'credit':  'CC BY-SA 2.0 / Takato Marui',
    },
    'スジクワガタ': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Dorcusstriatipennis.JPG/640px-Dorcusstriatipennis.JPG',
        'alt':     'スジクワガタのオス（Dorcus striatipennis）',
        'caption': 'スジクワガタのオス（Dorcus striatipennis）— 翅鞘の縦筋がコクワガタとの識別ポイント。里山の平地〜丘陵帯に生息する小型種。',
        'credit':  'CC BY-SA 3.0 / Endingok',
    },
    # 上記にないときのデフォルト（コクワガタ）
    'default': {
        'url':     'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Dorcus_rectus_01.JPG/640px-Dorcus_rectus_01.JPG',
        'alt':     'クワガタムシ（Dorcus rectus）',
        'caption': 'コクワガタ（Dorcus rectus）— 日本全国に広く生息する代表的なクワガタムシ。',
        'credit':  'CC BY-SA 3.0 / Σ64',
    },
}

def get_first_species(content: str) -> str:
    """sp-tableの最初のデータ行から種名を取得"""
    table_m = re.search(r'<table class=["\']sp-table["\']>(.*?)</table>', content, re.DOTALL)
    if not table_m:
        return ''
    tbody = table_m.group(1)
    for row_m in re.finditer(r'<tr>(.*?)</tr>', tbody, re.DOTALL):
        row = row_m.group(1)
        if '<th>' in row:
            continue
        tds = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if tds:
            name = re.sub(r'<[^>]+>', '', tds[0]).strip()
            name = re.sub(r'（[^）]*）', '', name).strip()
            return name
    return ''

def make_photo_html(photo: dict, pref_name: str) -> str:
    return f'''
<figure style="margin:16px 0 24px;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.15)">
  <img src="{photo['url']}"
       alt="{photo['alt']}"
       loading="lazy" width="640" height="427"
       style="width:100%;display:block;max-height:340px;object-fit:cover">
  <figcaption style="font-size:.72rem;color:#888;text-align:center;padding:7px 12px;background:#f9f9f9;line-height:1.6">
    {photo['caption']}<br>
    <small>出典: Wikimedia Commons（{photo['credit']}）</small>
  </figcaption>
</figure>'''

PREF_NAMES = {
    'hokkaido':'北海道','aomori':'青森県','iwate':'岩手県','miyagi':'宮城県',
    'akita':'秋田県','yamagata':'山形県','fukushima':'福島県','ibaraki':'茨城県',
    'tochigi':'栃木県','gunma':'群馬県','saitama':'埼玉県','chiba':'千葉県',
    'tokyo':'東京都','kanagawa':'神奈川県','niigata':'新潟県','toyama':'富山県',
    'ishikawa':'石川県','fukui':'福井県','yamanashi':'山梨県','nagano':'長野県',
    'gifu':'岐阜県','shizuoka':'静岡県','aichi':'愛知県','mie':'三重県',
    'shiga':'滋賀県','kyoto':'京都府','osaka':'大阪府','hyogo':'兵庫県',
    'nara':'奈良県','wakayama':'和歌山県','tottori':'鳥取県','shimane':'島根県',
    'okayama':'岡山県','hiroshima':'広島県','yamaguchi':'山口県','tokushima':'徳島県',
    'kagawa':'香川県','ehime':'愛媛県','kochi':'高知県','fukuoka':'福岡県',
    'saga':'佐賀県','nagasaki':'長崎県','kumamoto':'熊本県','oita':'大分県',
    'miyazaki':'宮崎県','kagoshima':'鹿児島県','okinawa':'沖縄県',
}

def process_file(filepath: str) -> bool:
    pref_key = re.search(r'guide_pref_(\w+)\.html', filepath)
    if not pref_key:
        return False
    pref_key = pref_key.group(1)
    pref_name = PREF_NAMES.get(pref_key, pref_key)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # すでに写真が挿入済みならスキップ
    if 'upload.wikimedia.org' in content:
        print(f'  SKIP (already has photo): {filepath}')
        return False

    # 種名を取得
    species = get_first_species(content)
    photo = SPECIES_PHOTO.get(species, SPECIES_PHOTO['default'])

    # 挿入位置：SVGチャートの <figure>...</figure> の直後
    # （figcaptionで終わる </figure> を探す）
    figure_end = content.rfind('</figure>')
    if figure_end == -1:
        # SVGがない場合は sp-table の </table> の直後
        table_m = re.search(r'(<table class=["\']sp-table["\']>.*?</table>)', content, re.DOTALL)
        if not table_m:
            print(f'  WARNING: no insertion point found: {filepath}')
            return False
        insert_pos = table_m.end()
    else:
        insert_pos = figure_end + len('</figure>')

    photo_html = make_photo_html(photo, pref_name)
    new_content = content[:insert_pos] + '\n' + photo_html + content[insert_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'  OK [{species}→photo]: {filepath}')
    return True


if __name__ == '__main__':
    files = sorted(glob.glob('templates/guide_pref_*.html'))
    print(f'処理対象: {len(files)} ファイル')
    updated = 0
    for fp in files:
        if process_file(fp):
            updated += 1
    print(f'\n完了: {updated}/{len(files)} ファイルを更新しました')
