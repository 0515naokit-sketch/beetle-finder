#!/usr/bin/env python3
"""
① 記事本文中のキーワードに内部リンクを自動挿入
- 各ページで最初の出現のみリンク化（同じキーワードの連打を避ける）
- <script>, <style>, <a> タグ内は処理しない
- 自分自身のページへのリンクは作らない
"""

import glob, re

KEYWORD_MAP = [
    # 種別ガイド
    ('ミヤマクワガタ',       '/guide/miyama'),
    ('ノコギリクワガタ',     '/guide/nokogiri'),
    ('ヒラタクワガタ',       '/guide/hirata'),
    ('コクワガタ',           '/guide/kokuwagata'),
    ('オオクワガタ',         '/guide/ookuwa'),
    ('アカアシクワガタ',     '/guide/akaashi'),
    ('スジクワガタ',         '/guide/suji'),
    ('カブトムシ',           '/guide/kabuto'),
    # テクニック系
    ('夜間採集',             '/guide/night'),
    ('早朝採集',             '/guide/morning'),
    ('雨上がり',             '/guide/rain'),
    ('トラップ',             '/guide/trap'),
    ('ライトトラップ',       '/guide/light'),
    ('採集道具',             '/guide/tools'),
    ('採集スポット',         '/app'),
    ('クヌギ',               '/guide/tree'),
    ('コナラ',               '/guide/tree'),
    # 月別
    ('6月',                  '/guide/june'),
    ('7月',                  '/guide/july'),
    ('8月',                  '/guide/august'),
    ('5月',                  '/guide/may'),
    ('9月',                  '/guide/september'),
    ('10月',                 '/guide/october'),
    # ケア系
    ('飼育',                 '/guide/breeding'),
    ('採集後',               '/guide/aftercare'),
    # 初心者
    ('初心者',               '/guide/beginners'),
]

# ページURLから自分自身のガイドを割り出す
FILENAME_TO_URL = {
    'guide_miyama.html':      '/guide/miyama',
    'guide_nokogiri.html':    '/guide/nokogiri',
    'guide_hirata.html':      '/guide/hirata',
    'guide_kokuwagata.html':  '/guide/kokuwagata',
    'guide_ookuwa.html':      '/guide/ookuwa',
    'guide_akaashi.html':     '/guide/akaashi',
    'guide_suji.html':        '/guide/suji',
    'guide_kabuto.html':      '/guide/kabuto',
    'guide_night.html':       '/guide/night',
    'guide_morning.html':     '/guide/morning',
    'guide_rain.html':        '/guide/rain',
    'guide_trap.html':        '/guide/trap',
    'guide_light.html':       '/guide/light',
    'guide_tools.html':       '/guide/tools',
    'guide_tree.html':        '/guide/tree',
    'guide_june.html':        '/guide/june',
    'guide_july.html':        '/guide/july',
    'guide_august.html':      '/guide/august',
    'guide_may.html':         '/guide/may',
    'guide_september.html':   '/guide/september',
    'guide_october.html':     '/guide/october',
    'guide_breeding.html':    '/guide/breeding',
    'guide_aftercare.html':   '/guide/aftercare',
    'guide_beginners.html':   '/guide/beginners',
}

def split_html(html):
    """HTMLをテキスト部分とタグ部分に分割して返す"""
    parts = re.split(r'(<[^>]+>)', html)
    return parts

def add_inline_links(content: str, self_url: str) -> str:
    """本文テキストのキーワードに初出のみリンクを挿入"""
    
    # <style>〜</style> と <script>〜</script> を退避
    placeholders = {}
    def stash(m):
        key = f'__STASH_{len(placeholders)}__'
        placeholders[key] = m.group(0)
        return key
    
    content = re.sub(r'<style[^>]*>.*?</style>', stash, content, flags=re.DOTALL)
    content = re.sub(r'<script[^>]*>.*?</script>', stash, content, flags=re.DOTALL)
    
    # 既存の<a>タグ内も退避
    content = re.sub(r'<a\b[^>]*>.*?</a>', stash, content, flags=re.DOTALL)
    
    used_keywords = set()
    
    for keyword, url in KEYWORD_MAP:
        if url == self_url:
            continue  # 自分自身へのリンクはスキップ
        if keyword in used_keywords:
            continue
        
        # テキストノードのみで最初の出現を置換
        # タグ内(属性値等)には挿入しない
        pattern = re.compile(r'(?<![>])' + re.escape(keyword))
        
        count = [0]
        def replacer(m, kw=keyword, u=url, c=count):
            # すでに置換済みならスキップ
            if c[0] > 0:
                return m.group(0)
            c[0] += 1
            return f'<a href="{u}" style="color:#388e3c;font-weight:700;text-decoration:underline">{kw}</a>'
        
        # タグ間のテキストのみを対象に置換
        parts = re.split(r'(<[^>]+>|__STASH_\d+__)', content)
        new_parts = []
        replaced = False
        for part in parts:
            if part.startswith('<') or part.startswith('__STASH_'):
                new_parts.append(part)
            elif not replaced and keyword in part:
                new_part = part.replace(keyword, 
                    f'<a href="{url}" style="color:#388e3c;font-weight:700;text-decoration:underline">{keyword}</a>',
                    1)
                new_parts.append(new_part)
                replaced = True
            else:
                new_parts.append(part)
        content = ''.join(new_parts)
    
    # 退避したブロックを復元
    for key, val in placeholders.items():
        content = content.replace(key, val)
    
    return content

files = sorted(glob.glob('/Users/naokitakahashi/beetle-finder/templates/guide*.html'))
# 都道府県ページと種別ページを対象（インデックスページは除く）
target_files = [f for f in files 
                if 'guide_pref_' in f 
                or any(k in f for k in ['kabuto','miyama','nokogiri','hirata','kokuwagata',
                                         'ookuwa','akaashi','suji','june','july','august',
                                         'may','september','october','night','morning',
                                         'rain','trap','light','beginners','tools','breeding',
                                         'aftercare','kids','spot','calendar','reports',
                                         'scoring','tree'])]

updated = 0
for fp in target_files:
    fname = fp.split('/')[-1]
    self_url = FILENAME_TO_URL.get(fname, '')
    
    with open(fp, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = add_inline_links(original, self_url)
    
    if content != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        # リンク数をカウント
        added = content.count('text-decoration:underline') - original.count('text-decoration:underline')
        print(f'  OK (+{added}links): {fname}')
        updated += 1

print(f'\n完了: {updated}/{len(target_files)} ファイルを更新')
