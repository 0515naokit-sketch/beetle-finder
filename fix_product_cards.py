"""
月別ガイドの amz-box（カテゴリ名+ボタンのみ）を
商品名・価格帯・説明付きのカード型に置き換える

対象: guide_july, guide_august, guide_september, guide_october, guide_may,
      guide_spring, guide_morning, guide_night, guide_rain
"""
import os, re

TEMPLATES_DIR = 'templates'

# ページごとに商品カードを定義
# 各エントリ: (emoji, タイトル, バッジ, 説明文, 価格帯, amazon_kw, rakuten_kw)
PAGE_PRODUCTS = {
    'guide_july.html': {
        'section_title': '7月の採集装備【2026年版】',
        'intro': '7月はシーズン最盛期。熱中症・スズメバチ・クマ対策を万全にして出かけましょう。私が実際に使っている装備を選び方のポイントつきで紹介します。',
        'products': [
            ('🔦', '充電式ヘッドライト（500lm以上）', '必須', '7月の夜間採集では虫が多く、木を素早く確認するため明るいライトが有利。500ルーメン以上・防水・充電式を選ぼう。電池切れが心配な場合はモバイルバッテリーも持参。', '2,500〜5,000円', 'ヘッドライト+充電式+高輝度+防水+アウトドア', '%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88+%E9%AB%98%E8%BC%9D%E5%BA%A6+%E5%85%85%E9%9B%BB%E5%BC%8F+%E9%98%B2%E6%B0%B4'),
            ('🦟', '防虫スプレー（長時間タイプ・12時間）', '必須', '7月は蚊・ブヨが多い。ディート30%以上または植物性ピカリジンタイプで12時間持続するものを選ぼう。腕・首・足首に重点的に使用。', '700〜1,500円', '防虫スプレー+長時間+12時間+アウトドア+ディート', '%E9%98%B2%E8%99%AB%E3%82%B9%E3%83%97%E3%83%AC%E3%83%BC+%E9%95%B7%E6%99%82%E9%96%93+%E3%82%A2%E3%82%A6%E3%83%88%E3%83%89%E3%82%A2'),
            ('🐝', 'スズメバチ忌避スプレー', '7月必須', 'スズメバチが最も活発になるのが7〜9月。採集前に衣服にスプレーしておくと安心。甘い香りの香水・制汗スプレーは逆に誘引するので禁止。', '1,000〜2,500円', 'スズメバチ+忌避スプレー+アウトドア', '%E3%82%B9%E3%82%BA%E3%83%A1%E3%83%90%E3%83%81+%E5%BF%8C%E9%81%BF%E3%82%B9%E3%83%97%E3%83%AC%E3%83%BC'),
            ('🪣', 'クワガタ用 保冷ボックス（ソフトタイプ）', 'おすすめ', '7月の炎天下に採集した虫をそのまま放置すると死んでしまう。ソフトクーラーに保冷剤と虫かごを入れて持ち帰るのがベスト。', '1,500〜4,000円', '保冷ボックス+ソフト+小型+アウトドア', '%E3%82%BD%E3%83%95%E3%83%88%E3%82%AF%E3%83%BC%E3%83%A9%E3%83%BC+%E5%B0%8F%E5%9E%8B+%E3%82%A2%E3%82%A6%E3%83%88%E3%83%89%E3%82%A2'),
            ('🧃', 'モバイルバッテリー（10,000mAh）', 'あると便利', '深夜採集が長引いたときにヘッドライトの予備電源として使える。小型軽量の10,000mAhクラスが採集には最適。', '2,000〜4,000円', 'モバイルバッテリー+10000mAh+軽量+小型', '%E3%83%A2%E3%83%90%E3%82%A4%E3%83%AB%E3%83%90%E3%83%83%E3%83%86%E3%83%AA%E3%83%BC+10000mAh+%E5%B0%8F%E5%9E%8B'),
        ]
    },
    'guide_august.html': {
        'section_title': '8月の採集装備【2026年版】',
        'intro': 'カブトムシ最盛期の8月。熱中症対策と夜間採集の装備を万全にして出かけましょう。',
        'products': [
            ('🔦', '充電式ヘッドライト（500lm以上）', '必須', '8月は夜間でも気温が高く汗をかくため、防汗バンド付きや軽量タイプが快適。500lm以上あれば木全体を素早くチェックできる。', '2,500〜5,000円', 'ヘッドライト+充電式+高輝度+防水', '%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88+%E9%AB%98%E8%BC%9D%E5%BA%A6+%E5%85%85%E9%9B%BB%E5%BC%8F'),
            ('🦟', '防虫スプレー（ディート30%以上）', '必須', '8月は蚊・ブヨのピーク。効果時間が長いディート高濃度タイプか、ピカリジン配合タイプを選ぼう。子供には濃度の低いタイプを。', '700〜1,500円', '防虫スプレー+ディート+高濃度+長時間', '%E9%98%B2%E8%99%AB%E3%82%B9%E3%83%97%E3%83%AC%E3%83%BC+%E9%95%B7%E6%99%82%E9%96%93'),
            ('🧊', '保冷剤・ソフトクーラー', '8月特有', '採集後の虫の管理が最重要。炎天下の車内は60℃超になることも。採集した虫は保冷ボックスに入れて持ち帰ること。', '1,500〜3,500円', 'ソフトクーラー+保冷剤+昆虫採集', '%E3%82%BD%E3%83%95%E3%83%88%E3%82%AF%E3%83%BC%E3%83%A9%E3%83%BC+%E4%BF%9D%E5%86%B7%E5%89%A4'),
            ('💦', '汗拭きシート・冷感タオル', 'あると便利', '夜間でも気温28℃以上になる8月。汗をこまめに拭いて熱中症を予防。冷感タオルを首に巻くと体感温度が下がる。', '400〜1,200円', '冷感タオル+汗拭きシート+アウトドア+スポーツ', '%E5%86%B7%E6%84%9F%E3%82%BF%E3%82%AA%E3%83%AB+%E6%B1%97%E6%8B%AD%E3%81%8D%E3%82%B7%E3%83%BC%E3%83%88'),
            ('🪣', 'クワガタ用 虫かご（コバエシャッター付き）', '必須', '8月は帰宅後そのまま飼育するケースも多い。コバエシャッター付きなら後片付けも楽。2〜3個用意しておくと種・サイズ別に分けられる。', '900〜2,500円', '虫かご+クワガタ+コバエシャッター+飼育ケース', '%E8%99%AB%E3%81%8B%E3%81%94+%E3%82%AF%E3%83%AF%E3%82%AC%E3%82%BF+%E3%82%B3%E3%83%90%E3%82%A8%E9%98%B2%E6%AD%A2'),
        ]
    },
    'guide_september.html': {
        'section_title': '9月の採集装備【2026年版】',
        'intro': '残暑が続く9月。シーズン終盤戦に必要な装備を選び方のポイントつきで紹介します。',
        'products': [
            ('🔦', '充電式ヘッドライト', '必須', '9月は日没が早くなり採集可能な時間が増える。防水・充電式・300lm以上を確認して選ぼう。', '2,000〜4,500円', 'ヘッドライト+充電式+防水+アウトドア', '%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88+%E5%85%85%E9%9B%BB%E5%BC%8F'),
            ('🧥', '薄手のジャケット・ウインドシェル', '9月から必要', '9月後半は標高600m以上で夜間15℃以下になることも。薄手のウインドシェルをザックに入れておくと体温調節ができる。', '3,000〜8,000円', 'ウインドシェル+薄手+軽量+アウトドア', '%E3%82%A6%E3%82%A4%E3%83%B3%E3%83%89%E3%82%B7%E3%82%A7%E3%83%AB+%E8%BB%BD%E9%87%8F'),
            ('🦟', '防虫スプレー', 'おすすめ', '9月もまだ蚊・ブヨは多い。採集前に忘れずスプレー。', '700〜1,500円', '防虫スプレー+長時間+アウトドア', '%E9%98%B2%E8%99%AB%E3%82%B9%E3%83%97%E3%83%AC%E3%83%BC+%E9%95%B7%E6%99%82%E9%96%93'),
        ]
    },
    'guide_october.html': {
        'section_title': '10月の採集装備【2026年版】',
        'intro': '10月はコクワが主役のシーズン終盤。朝晩は冷え込むため防寒・防水対策が重要です。',
        'products': [
            ('🧥', 'フリース・薄手のダウン', '10月必須', '10月の夜間は気温10℃以下になる山間部も多い。軽量フリースや薄手ダウンを1枚ザックに入れておこう。', '2,500〜8,000円', 'フリース+軽量+薄手+アウトドア', '%E3%83%95%E3%83%AA%E3%83%BC%E3%82%B9+%E8%BB%BD%E9%87%8F+%E3%82%A2%E3%82%A6%E3%83%88%E3%83%89%E3%82%A2'),
            ('🔦', '充電式ヘッドライト', '必須', '日没が17時台になる10月。夜間採集には明るいヘッドライト必須。', '2,000〜4,500円', 'ヘッドライト+充電式+防水', '%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88+%E5%85%85%E9%9B%BB%E5%BC%8F'),
            ('🧤', '防寒グローブ', 'あると便利', '10月夜間は素手だと指先が悴む。薄手の防水グローブがあると採集しやすい。', '1,000〜3,000円', 'グローブ+防水+薄手+防寒+アウトドア', '%E3%82%B0%E3%83%AD%E3%83%BC%E3%83%96+%E9%98%B2%E6%B0%B4+%E8%96%84%E6%89%8B+%E9%98%B2%E5%AF%92'),
        ]
    },
    'guide_may.html': {
        'section_title': '5月の採集準備グッズ【2026年版】',
        'intro': 'シーズン前の5月。今のうちに装備を揃えておくと6月の開幕ダッシュに乗り遅れません。',
        'products': [
            ('🔦', '充電式ヘッドライト（300lm以上）', '今のうちに購入', '6月のシーズン開幕前にチェック・購入しておこう。300lm以上・USB充電・防水の3点確認。5月のうちに試し使いもしておくと安心。', '2,000〜4,500円', 'ヘッドライト+充電式+防水+アウトドア', '%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88+%E5%85%85%E9%9B%BB%E5%BC%8F'),
            ('🪣', '飼育ケース（コバエシャッター付き）', 'シーズン前準備', 'クワガタが採れてから慌てて買うのではなく、5月のうちに用意しておくと安心。コバエシャッター付きSサイズとMサイズを1個ずつ揃えておくと対応できる。', '900〜2,500円', '飼育ケース+コバエシャッター+クワガタ', '%E9%A3%BC%E8%82%B2%E3%82%B1%E3%83%BC%E3%82%B9+%E3%82%B3%E3%83%90%E3%82%A8%E9%98%B2%E6%AD%A2'),
            ('🌿', '昆虫マット（クワガタ・カブトムシ用）', '今のうちに購入', '採集後すぐ飼育できるようにマットを用意しておこう。カブトムシ幼虫飼育を考えているなら発酵マット（高発酵タイプ）を選ぶ。', '600〜1,500円', '昆虫マット+クワガタ+カブトムシ+飼育', '%E6%98%86%E8%99%AB%E3%83%9E%E3%83%83%E3%83%88+%E3%82%AF%E3%83%AF%E3%82%AC%E3%82%BF+%E9%A3%BC%E8%82%B2'),
        ]
    },
}

# カード生成ヘルパー
def make_product_card(emoji, title, badge, description, price, amz_kw, rkt_kw):
    badge_colors = {
        '必須': '#e53935', '今のうちに購入': '#e53935',
        '7月必須': '#e65100', '8月特有': '#e65100', '9月から必要': '#e65100',
        '10月必須': '#1565c0', '今のうちに購入': '#1565c0',
        'シーズン前準備': '#2e7d32', '6月必須': '#e65100',
        'おすすめ': '#2e7d32', '強くおすすめ': '#2e7d32',
        'あると便利': '#555',
    }
    badge_color = badge_colors.get(badge, '#888')
    amz_url = f"https://www.amazon.co.jp/s?k={amz_kw.replace(' ', '+')}&tag=beetlefinder-22"
    rkt_url = f"https://af.moshimo.com/af/c/click?a_id=5563442&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fsearch.rakuten.co.jp%2Fsearch%2Fmall%2F{rkt_kw}%2F"

    badge_html = f'<span style="background:{badge_color};color:#fff;font-size:.65rem;font-weight:700;padding:2px 7px;border-radius:10px;white-space:nowrap">{badge}</span>' if badge else ''

    return f'''  <div style="background:#fff;border:1px solid #e0e0e0;border-radius:12px;padding:16px;box-shadow:0 2px 6px rgba(0,0,0,.06)">
   <div style="display:flex;align-items:flex-start;gap:12px;flex-wrap:wrap">
    <div style="flex:1;min-width:200px">
     <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap">
      <span style="font-size:1.4rem">{emoji}</span>
      <span style="font-weight:700;font-size:.95rem;color:#1b5e20">{title}</span>
      {badge_html}
     </div>
     <p style="font-size:.82rem;color:#444;margin:0 0 6px;line-height:1.6">{description}</p>
     <p style="font-size:.8rem;color:#e65100;font-weight:700;margin:0">参考価格：{price}</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0;min-width:160px">
     <a href="{amz_url}" target="_blank" rel="noopener sponsored" style="display:block;background:#ff9900;color:#fff;font-weight:700;font-size:.82rem;padding:9px 14px;border-radius:7px;text-decoration:none;text-align:center">🛒 Amazonで価格を見る →</a>
     <a href="{rkt_url}" target="_blank" rel="noopener sponsored" style="display:block;background:#bf0000;color:#fff;font-weight:700;font-size:.82rem;padding:9px 14px;border-radius:7px;text-decoration:none;text-align:center">楽天で価格を比較する →</a>
    </div>
   </div>
  </div>'''


def find_and_replace_amz_box(content, page_data):
    """amz-box を新しいカード型に置き換える"""
    # amz-box div を正規表現で検出
    pattern = r'<div class="amz-box">.*?</div>\s*(?:<p class="amz-note">.*?</p>)?'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return content, False

    cards = '\n'.join([make_product_card(*p) for p in page_data['products']])
    new_section = f''' <h2 class="section">{page_data['section_title']}</h2>
 <p style="font-size:.88rem;color:#555;margin-bottom:16px">{page_data['intro']}</p>

 <div style="display:flex;flex-direction:column;gap:14px;margin-bottom:20px">
{cards}
 </div>
 <p style="font-size:.72rem;color:#aaa;margin-top:-8px;margin-bottom:20px">※Amazon：アソシエイト参加。楽天：もしもアフィリエイト経由。リンクをクリックしても価格は変わりません。</p>'''

    # h2 + amz-box の組み合わせを探して置換
    full_pattern = r'<h2 class="section">[^<]*グッズ[^<]*</h2>\s*<div class="amz-box">.*?</div>(?:\s*<p class="amz-note">.*?</p>)?'
    new_content, n = re.subn(full_pattern, new_section, content, flags=re.DOTALL)
    if n > 0:
        return new_content, True

    # h2 が見つからない場合は amz-box だけ置換
    cards_only = f'''<div style="display:flex;flex-direction:column;gap:14px;margin-bottom:20px">
{cards}
 </div>
 <p style="font-size:.72rem;color:#aaa;margin-top:-8px;margin-bottom:20px">※Amazon：アソシエイト参加。楽天：もしもアフィリエイト経由。リンクをクリックしても価格は変わりません。</p>'''
    new_content = content[:match.start()] + cards_only + content[match.end():]
    return new_content, True


updated = 0
for fname, page_data in PAGE_PRODUCTS.items():
    path = os.path.join(TEMPLATES_DIR, fname)
    if not os.path.exists(path):
        print(f'  ⚠ ファイルなし: {fname}')
        continue
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content, changed = find_and_replace_amz_box(content, page_data)
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        updated += 1
        print(f'  ✅ {fname}')
    else:
        print(f'  ⚠ amz-box が見つからず: {fname}')

print(f'\n完了: {updated}ファイル更新')
