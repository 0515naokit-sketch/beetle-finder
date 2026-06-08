#!/usr/bin/env python3
"""
種別ガイド8ページ・月別ガイド6ページにmsmaflink商品ウィジェットを追加
挿入位置: <div class="cta-box"> の直前（なければ <div class="share-box"> の直前）
"""
import os

TEMPLATE_DIR = "/Users/naokitakahashi/beetle-finder/templates"

INIT = """(function(b,c,f,g,a,d,e){b.MoshimoAffiliateObject=a;
b[a]=b[a]||function(){arguments.currentScript=c.currentScript
||c.scripts[c.scripts.length-2];(b[a].q=b[a].q||[]).push(arguments)};
c.getElementById(a)||(d=c.createElement(f),d.src=g,
d.id=a,e=c.getElementsByTagName("body")[0],e.appendChild(d))})
(window,document,"script","//dn.msmstatic.com/site/cardlink/bundle.js?20220329","msmaflink");"""

CALLS = {
    'headlight': ('wgfjX', 'msmaflink({"n":"【東証上場の安心企業】GENTOS(ジェントス) LED ヘッドライト Gシリーズ GH-200RG 充電式","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"","p":["\\/\\@0_mall\\/mitenekakakubamboo\\/cabinet\\/01113290\\/imgrc0086738224.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/mitenekakakubamboo\\/gh-200rg\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/mitenekakakubamboo\\/gh-200rg\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=GENTOS+GH-200RG+%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=GENTOS+GH-200RG+%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"wgfjX","s":"s"});'),
    'net':       ('agvtz', 'msmaflink({"n":"昆虫ネット 虫取り網 伸縮式5段調節可能 軽量設計 子供用おもちゃ・採集ツール","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/\\@0_mall\\/ihoveninter\\/cabinet\\/11485545","p":["\\/h858.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/ihoveninter\\/pca-ca-sports16058\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/ihoveninter\\/pca-ca-sports16058\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E8%99%AB%E5%8F%96%E3%82%8A%E7%B6%B2+%E4%BC%B8%E7%B8%AE%E5%BC%8F+%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E8%99%AB%E5%8F%96%E3%82%8A%E7%B6%B2+%E4%BC%B8%E7%B8%AE%E5%BC%8F","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"agvtz","s":"s"});'),
    'cage':      ('8DUcb', 'msmaflink({"n":"虫かご 昆虫ケース 飼育ケース 昆虫 観察 むしとり 昆虫ケージ 観察ケース 昆虫採集 カブトムシ クワガタ","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/\\@0_mall\\/yukinosizuku\\/cabinet\\/10093341","p":["\\/1.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/yukinosizuku\\/n-musikago-1\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/yukinosizuku\\/n-musikago-1\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E8%99%AB%E3%81%8B%E3%81%94+%E6%98%86%E8%99%AB%E3%82%B1%E3%83%BC%E3%82%B9+%E3%82%AF%E3%83%AF%E3%82%AC%E3%82%BF","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E8%99%AB%E3%81%8B%E3%81%94+%E6%98%86%E8%99%AB%E3%82%B1%E3%83%BC%E3%82%B9","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"8DUcb","s":"s"});'),
    'set':       ('v4etf', 'msmaflink({"n":"昆虫採集セット 自然観察 昆虫観察キット 6点セット 知育玩具 虫取り 拡大鏡付き 虫取り網 金属製 昆虫ケース 子供","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/\\@0_mall\\/zakkashop2023\\/cabinet\\/11010402","p":["\\/imgrc0139731060.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/zakkashop2023\\/toy57\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/zakkashop2023\\/toy57\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86%E3%82%BB%E3%83%83%E3%83%88+%E6%8B%A1%E5%A4%A7%E9%8F%A1%E4%BB%98%E3%81%8D","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86%E3%82%BB%E3%83%83%E3%83%88","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"v4etf","s":"s"});'),
    'jelly':     ('rDdXc', 'msmaflink({"n":"【DDA】プロゼリー 16g 50個入×1袋 dda クワガタゼリー カブトムシゼリー 昆虫ゼリー","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/","p":["@0_gold\\/ddaism\\/bn\\/item\\/main-image\\/pro-j\\/20231001103255_1.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/ddaism\\/pro-j\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/ddaism\\/pro-j\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E3%83%97%E3%83%AD%E3%82%BC%E3%83%AA%E3%83%BC+%E6%98%86%E8%99%AB%E3%82%BC%E3%83%AA%E3%83%BC+%E3%82%AF%E3%83%AF%E3%82%AC%E3%82%BF","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E3%83%97%E3%83%AD%E3%82%BC%E3%83%AA%E3%83%BC+%E6%98%86%E8%99%AB%E3%82%BC%E3%83%AA%E3%83%BC","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"rDdXc","s":"s"});'),
}

def build_widget(product_keys, title):
    calls = "\n".join(CALLS[k][1] for k in product_keys)
    divs  = "\n".join(f'<div id="msmaflink-{CALLS[k][0]}">リンク</div>' for k in product_keys)
    return (
        f'\n<!-- START もしもアフィリエイト かんたんリンク -->\n'
        f'<div style="margin:28px 0">\n'
        f'<p style="font-size:.88rem;font-weight:700;color:#c45000;margin-bottom:4px">{title}</p>\n'
        f'<script type="text/javascript">\n'
        f'{INIT}\n'
        f'{calls}\n'
        f'</script>\n'
        f'{divs}\n'
        f'<p style="font-size:.6rem;color:#bbb;text-align:right;margin-top:4px">※ 価格・在庫は変動する場合があります</p>\n'
        f'</div>\n'
        f'<!-- もしもアフィリエイト END -->\n'
    )

# ページ定義: (ファイル名, 商品キー群, タイトル)
pages = [
    # 種別ガイド（採集道具：ヘッドライト・虫取り網・虫かご・プロゼリー）
    ('guide_miyama.html',     ['headlight','net','cage','jelly'], '🛒 ミヤマ採集に持っていくもの'),
    ('guide_nokogiri.html',   ['headlight','net','cage','jelly'], '🛒 ノコギリ採集に持っていくもの'),
    ('guide_hirata.html',     ['headlight','net','cage','jelly'], '🛒 ヒラタ採集に持っていくもの'),
    ('guide_kabuto.html',     ['headlight','net','cage','jelly'], '🛒 カブトムシ採集に持っていくもの'),
    ('guide_ookuwa.html',     ['headlight','net','cage','jelly'], '🛒 オオクワガタ採集に持っていくもの'),
    ('guide_kokuwagata.html', ['headlight','net','cage','jelly'], '🛒 コクワガタ採集に持っていくもの'),
    ('guide_akaashi.html',    ['headlight','net','cage','jelly'], '🛒 アカアシクワガタ採集に持っていくもの'),
    ('guide_suji.html',       ['headlight','net','cage','jelly'], '🛒 スジクワガタ採集に持っていくもの'),
    # 月別・方法別ガイド
    ('guide_may.html',        ['headlight','net','cage','set'],   '🛒 5月の採集に持っていくもの'),
    ('guide_light.html',      ['headlight','net'],                '🛒 街灯採集の必須道具'),
    ('guide_morning.html',    ['headlight','net','cage'],         '🛒 朝採集に持っていくもの'),
    ('guide_october.html',    ['headlight','net','jelly'],        '🛒 10月の採集に持っていくもの'),
    ('guide_september.html',  ['headlight','net','jelly'],        '🛒 9月の採集に持っていくもの'),
    ('guide_november.html',   ['headlight','net'],                '🛒 11月の採集に持っていくもの'),
]

for filename, keys, title in pages:
    fp = os.path.join(TEMPLATE_DIR, filename)
    with open(fp, encoding='utf-8') as f:
        content = f.read()

    # 既に実装済みならスキップ
    if 'msmaflink' in content:
        print(f"  スキップ（実装済み）: {filename}")
        continue

    widget = build_widget(keys, title)

    # 挿入位置: cta-box の直前、なければ share-box の直前
    anchor = '<div class="cta-box">'
    if anchor not in content:
        anchor = '<div class="share-box">'

    idx = content.find(anchor)
    if idx == -1:
        print(f"  ⚠️  挿入位置未検出: {filename}")
        continue

    content = content[:idx] + widget + content[idx:]
    with open(fp, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ {filename}  ({len(keys)}商品)")

print("\n完了")
