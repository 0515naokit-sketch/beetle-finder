#!/usr/bin/env python3
"""
回遊施策を全ガイドページに一括実装：
④ フッターにカテゴリナビ追加（全81ページ）
⑤ 都道府県ページの種別テーブルに種別ガイドリンク（47ページ）
② 「今月が旬」バナー JS（全81ページ）
"""

import glob, re

# ── ④ 新フッター HTML ──────────────────────────────────────────────────
NEW_FOOTER = '''<footer>
  <nav class="footer-nav">
    <div class="footer-nav-group">
      <span class="footer-nav-label">🪲 種別ガイド</span>
      <a href="/guide/kabuto">カブトムシ</a>
      <a href="/guide/miyama">ミヤマクワガタ</a>
      <a href="/guide/nokogiri">ノコギリクワガタ</a>
      <a href="/guide/hirata">ヒラタクワガタ</a>
      <a href="/guide/kokuwagata">コクワガタ</a>
      <a href="/guide/ookuwa">オオクワガタ</a>
      <a href="/guide/akaashi">アカアシクワガタ</a>
      <a href="/guide/suji">スジクワガタ</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">📅 月別ガイド</span>
      <a href="/guide/may">5月</a>
      <a href="/guide/june">6月</a>
      <a href="/guide/july">7月</a>
      <a href="/guide/august">8月</a>
      <a href="/guide/september">9月</a>
      <a href="/guide/october">10月</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">📖 採集テクニック</span>
      <a href="/guide/beginners">初心者ガイド</a>
      <a href="/guide/night">夜間採集</a>
      <a href="/guide/rain">雨上がり採集</a>
      <a href="/guide/morning">早朝採集</a>
      <a href="/guide/trap">トラップ採集</a>
      <a href="/guide/light">ライト採集</a>
      <a href="/guide/tools">採集道具</a>
      <a href="/guide/tree">採集木図鑑</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">🗾 都道府県ガイド</span>
      <a href="/guide/pref/tokyo">東京都</a>
      <a href="/guide/pref/kanagawa">神奈川県</a>
      <a href="/guide/pref/saitama">埼玉県</a>
      <a href="/guide/pref/chiba">千葉県</a>
      <a href="/guide/pref/nagano">長野県</a>
      <a href="/guide/pref/yamanashi">山梨県</a>
      <a href="/guide/pref/hokkaido">北海道</a>
      <a href="/guide/pref">全都道府県一覧 →</a>
    </div>
  </nav>
  <div class="footer-bottom">
    <a href="/">クワガタ採集スポット検索 beetle-finder</a> ｜
    <a href="/app">🗺 スポット検索</a> ｜
    <a href="/guide">📖 ガイド一覧</a> ｜
    <a href="/about">サービスについて</a> ｜
    <a href="/privacy">プライバシーポリシー</a> ｜
    <a href="/terms">利用規約</a>
  </div>
</footer>'''

FOOTER_CSS = '''
  /* ── フッターナビ ─────────────────────────────── */
  footer{background:#1b2d1b;color:#81c784;padding:28px 16px 16px;font-size:.78rem;margin-top:40px}
  .footer-nav{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:20px;max-width:800px;margin:0 auto 20px;padding:0 0 20px;border-bottom:1px solid #2e4e2e}
  .footer-nav-group{display:flex;flex-direction:column;gap:6px}
  .footer-nav-label{color:#a5d6a7;font-weight:700;font-size:.8rem;margin-bottom:2px}
  .footer-nav a{color:#81c784;text-decoration:none;font-size:.78rem;line-height:1.6}
  .footer-nav a:hover{color:#fff;text-decoration:underline}
  .footer-bottom{text-align:center;color:#4a7a4a}
  .footer-bottom a{color:#81c784}'''

# ── ② 今月が旬バナー JS ─────────────────────────────────────────────────
SEASON_BANNER_JS = '''
<script>
(function(){
  var m = new Date().getMonth()+1;
  var map = {5:['6月の採集準備を今から！コクワガタが動き出す季節','/guide/june','6月の採集ガイドを読む'],
             6:['クワガタシーズン開幕！6月の採集ガイド','/guide/june','今すぐ読む →'],
             7:['🔥 採集最盛期！7月は全種が揃うベストシーズン','/guide/july','7月ガイドを読む'],
             8:['カブトムシのピーク！8月の採集攻略法','/guide/august','8月ガイドを読む'],
             9:['9月もまだ間に合う！秋の採集ガイド','/guide/september','9月ガイドを読む'],
             10:['10月の採集はコクワが主役。シーズン終盤戦','/guide/october','10月ガイドを読む']};
  if(!map[m]) return;
  var d=document.createElement('div');
  d.innerHTML='<div style="background:linear-gradient(135deg,#1b5e20,#2e7d32);color:#fff;padding:12px 18px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:.85rem;border-bottom:3px solid #4caf50"><span>📅 '+map[m][0]+'</span><a href="'+map[m][1]+'" style="background:#fff;color:#1b5e20;font-weight:700;padding:6px 14px;border-radius:20px;text-decoration:none;white-space:nowrap;font-size:.8rem">'+map[m][2]+'</a></div>';
  var header=document.getElementById('site-header');
  if(header&&header.nextSibling){header.parentNode.insertBefore(d.firstChild,header.nextSibling);}
  else{document.body.insertBefore(d.firstChild,document.body.firstChild);}
})();
</script>'''

# ── ⑤ 種別テーブルリンクマッピング ───────────────────────────────────────
SPECIES_LINKS = {
    'コクワガタ':        '/guide/kokuwagata',
    'ノコギリクワガタ':  '/guide/nokogiri',
    'カブトムシ':        '/guide/kabuto',
    'ミヤマクワガタ':    '/guide/miyama',
    'ヒラタクワガタ':    '/guide/hirata',
    'オオクワガタ':      '/guide/ookuwa',
    'アカアシクワガタ':  '/guide/akaashi',
    'スジクワガタ':      '/guide/suji',
    'オキナワヒラタクワガタ': '/guide/hirata',
    'ヤエヤマノコギリ':  '/guide/nokogiri',
    'リュウキュウコクワガタ': '/guide/kokuwagata',
}

def linkify_species_in_table(content: str, filepath: str) -> str:
    """sp-tableの最初のtd（種名列）をリンク化"""
    if 'guide_pref_' not in filepath:
        return content
    
    def link_td(m):
        td_content = m.group(1)
        # すでにリンクがある場合はスキップ
        if '<a ' in td_content:
            return m.group(0)
        # class属性があるtdのテキストを取得
        plain = re.sub(r'<[^>]+>', '', td_content).strip()
        if plain in SPECIES_LINKS:
            url = SPECIES_LINKS[plain]
            # クラス属性を保持しつつリンク化
            return m.group(0).replace(
                td_content,
                f'<a href="{url}" style="color:#1b5e20;font-weight:700">{plain}</a>'
            )
        return m.group(0)
    
    # <table class="sp-table">内の<td>を処理
    def process_table(tm):
        table_html = tm.group(0)
        # 各行の最初のtdのみリンク化
        def process_row(rm):
            row = rm.group(0)
            if '<th>' in row or '<th ' in row:
                return row  # ヘッダー行スキップ
            # 最初のtdのみ
            return re.sub(r'<td([^>]*)>([^<]+)</td>', link_td, row, count=1)
        return re.sub(r'<tr>.*?</tr>', process_row, table_html, flags=re.DOTALL)
    
    return re.sub(
        r'<table class=["\']sp-table["\']>.*?</table>',
        process_table,
        content,
        flags=re.DOTALL
    )

def replace_footer(content: str) -> str:
    """フッターを新フッターに置換"""
    # 既存フッターを検出して置換
    new = re.sub(r'<footer>.*?</footer>', NEW_FOOTER, content, flags=re.DOTALL)
    return new

def update_footer_css(content: str) -> str:
    """フッターCSSを更新"""
    # 既存のfooter CSSを削除して新CSSを追加
    # footer{ ... } ルールを削除
    content = re.sub(r'\s*footer\{[^}]+\}', '', content)
    # .footer-links があれば削除
    content = re.sub(r'\s*\.footer-links\{[^}]+\}', '', content)
    content = re.sub(r'\s*\.footer-links\s+a\{[^}]+\}', '', content)
    # </style>の直前に新CSS追加
    content = content.replace('</style>', FOOTER_CSS + '\n  </style>', 1)
    return content

def add_season_banner(content: str) -> str:
    """シーズンバナーJSを</body>直前に追加（重複防止）"""
    if 'season_banner' in content or 'シーズン開幕' in content or 'var map = {' in content:
        return content
    return content.replace('</body>', SEASON_BANNER_JS + '\n</body>')

# ── メイン処理 ───────────────────────────────────────────────────────────
files = sorted(glob.glob('/Users/naokitakahashi/beetle-finder/templates/guide*.html'))
updated = 0

for fp in files:
    with open(fp, 'r', encoding='utf-8') as f:
        original = f.read()
    
    content = original
    content = replace_footer(content)
    content = update_footer_css(content)
    content = add_season_banner(content)
    content = linkify_species_in_table(content, fp)

    if content != original:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  OK: {fp.split("/")[-1]}')
        updated += 1
    else:
        print(f'  --: {fp.split("/")[-1]}')

print(f'\n完了: {updated}/{len(files)} ファイルを更新')
