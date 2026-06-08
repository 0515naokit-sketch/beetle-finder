#!/usr/bin/env python3
"""
もしもアフィリエイトの msmaflink ウィジェットを主要ガイドページに組み込む
静的 Pochipp カード → msmaflink 自動更新ウィジェット
"""
import os

TEMPLATE_DIR = "/Users/naokitakahashi/beetle-finder/templates"

INIT = """(function(b,c,f,g,a,d,e){b.MoshimoAffiliateObject=a;
b[a]=b[a]||function(){arguments.currentScript=c.currentScript
||c.scripts[c.scripts.length-2];(b[a].q=b[a].q||[]).push(arguments)};
c.getElementById(a)||(d=c.createElement(f),d.src=g,
d.id=a,e=c.getElementsByTagName("body")[0],e.appendChild(d))})
(window,document,"script","//dn.msmstatic.com/site/cardlink/bundle.js?20220329","msmaflink");"""

PRODUCTS = {
    'headlight': {
        'eid': 'wgfjX',
        'call': 'msmaflink({"n":"【東証上場の安心企業】GENTOS(ジェントス) LED ヘッドライト Gシリーズ GH-200RG 充電式","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"","p":["\\/\\@0_mall\\/mitenekakakubamboo\\/cabinet\\/01113290\\/imgrc0086738224.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/mitenekakakubamboo\\/gh-200rg\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/mitenekakakubamboo\\/gh-200rg\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=GENTOS+GH-200RG+%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=GENTOS+GH-200RG+%E3%83%98%E3%83%83%E3%83%89%E3%83%A9%E3%82%A4%E3%83%88","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"wgfjX","s":"s"});',
    },
    'net': {
        'eid': 'agvtz',
        'call': 'msmaflink({"n":"昆虫ネット 虫取り網 伸縮式5段調節可能 軽量設計 子供用おもちゃ・採集ツール","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/\\@0_mall\\/ihoveninter\\/cabinet\\/11485545","p":["\\/h858.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/ihoveninter\\/pca-ca-sports16058\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/ihoveninter\\/pca-ca-sports16058\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E8%99%AB%E5%8F%96%E3%82%8A%E7%B6%B2+%E4%BC%B8%E7%B8%AE%E5%BC%8F+%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E8%99%AB%E5%8F%96%E3%82%8A%E7%B6%B2+%E4%BC%B8%E7%B8%AE%E5%BC%8F","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"agvtz","s":"s"});',
    },
    'cage': {
        'eid': '8DUcb',
        'call': 'msmaflink({"n":"虫かご 昆虫ケース 飼育ケース 昆虫 観察 むしとり 昆虫ケージ 観察ケース 昆虫採集 カブトムシ クワガタ","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/\\@0_mall\\/yukinosizuku\\/cabinet\\/10093341","p":["\\/1.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/yukinosizuku\\/n-musikago-1\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/yukinosizuku\\/n-musikago-1\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E8%99%AB%E3%81%8B%E3%81%94+%E6%98%86%E8%99%AB%E3%82%B1%E3%83%BC%E3%82%B9+%E3%82%AF%E3%83%AF%E3%82%AC%E3%82%BF","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E8%99%AB%E3%81%8B%E3%81%94+%E6%98%86%E8%99%AB%E3%82%B1%E3%83%BC%E3%82%B9","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"8DUcb","s":"s"});',
    },
    'set': {
        'eid': 'v4etf',
        'call': 'msmaflink({"n":"昆虫採集セット 自然観察 昆虫観察キット 6点セット 知育玩具 虫取り 拡大鏡付き 虫取り網 金属製 昆虫ケース 子供","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/\\@0_mall\\/zakkashop2023\\/cabinet\\/11010402","p":["\\/imgrc0139731060.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/zakkashop2023\\/toy57\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/zakkashop2023\\/toy57\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86%E3%82%BB%E3%83%83%E3%83%88+%E6%8B%A1%E5%A4%A7%E9%8F%A1%E4%BB%98%E3%81%8D","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E6%98%86%E8%99%AB%E6%8E%A1%E9%9B%86%E3%82%BB%E3%83%83%E3%83%88","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"v4etf","s":"s"});',
    },
    'jelly': {
        'eid': 'rDdXc',
        'call': 'msmaflink({"n":"【DDA】プロゼリー 16g 50個入×1袋 dda クワガタゼリー カブトムシゼリー 昆虫ゼリー","b":"","t":"","d":"https:\\/\\/thumbnail.image.rakuten.co.jp","c_p":"\\/","p":["@0_gold\\/ddaism\\/bn\\/item\\/main-image\\/pro-j\\/20231001103255_1.jpg"],"u":{"u":"https:\\/\\/item.rakuten.co.jp\\/ddaism\\/pro-j\\/","t":"rakuten","r_v":""},"v":"2.1","b_l":[{"id":1,"u_tx":"楽天市場で見る","u_bc":"#f76956","u_url":"https:\\/\\/item.rakuten.co.jp\\/ddaism\\/pro-j\\/","a_id":5563442,"p_id":54,"pl_id":27059,"pc_id":54,"s_n":"rakuten","u_so":1},{"id":3,"u_tx":"Amazonで見る","u_bc":"#f79256","u_url":"https:\\/\\/www.amazon.co.jp\\/s?k=%E3%83%97%E3%83%AD%E3%82%BC%E3%83%AA%E3%83%BC+%E6%98%86%E8%99%AB%E3%82%BC%E3%83%AA%E3%83%BC+%E3%82%AF%E3%83%AF%E3%82%AC%E3%82%BF","a_id":5563445,"p_id":170,"pl_id":27060,"pc_id":185,"s_n":"amazon","u_so":2},{"id":4,"u_tx":"Yahoo!ショッピングで見る","u_bc":"#66a7ff","u_url":"https:\\/\\/shopping.yahoo.co.jp\\/search?first=1&p=%E3%83%97%E3%83%AD%E3%82%BC%E3%83%AA%E3%83%BC+%E6%98%86%E8%99%AB%E3%82%BC%E3%83%AA%E3%83%BC","a_id":5563449,"p_id":1225,"pl_id":27061,"pc_id":1925,"s_n":"yahoo","u_so":3}],"eid":"rDdXc","s":"s"});',
    },
}

def build_widget(keys, title):
    calls = "\n".join(PRODUCTS[k]['call'] for k in keys)
    divs  = "\n".join(f'<div id="msmaflink-{PRODUCTS[k]["eid"]}">リンク</div>' for k in keys)
    return (
        f'<!-- START もしもアフィリエイト かんたんリンク -->\n'
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

def find_amz_section(content):
    """<div class="amz-section"> の開始位置と終了位置をdiv深さカウントで探す"""
    marker = '<div class="amz-section">'
    start = content.find(marker)
    if start == -1:
        return None, None
    depth = 0
    i = start
    while i < len(content):
        if content[i:i+4] == '<div':
            depth += 1
            i += 4
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = i + 6
                # skip trailing newline
                if end < len(content) and content[end] == '\n':
                    end += 1
                return start, end
            i += 6
        else:
            i += 1
    return None, None

pages = {
    'guide_july.html':      (['headlight','net','set','jelly'],         '🛒 7月の採集に持っていくもの'),
    'guide_august.html':    (['headlight','net','set','jelly'],         '🛒 8月の採集に持っていくもの'),
    'guide_june.html':      (['headlight','net','cage','jelly'],        '🛒 6月の採集に持っていくもの'),
    'guide_tools.html':     (['headlight','net','cage','set','jelly'],  '🛒 おすすめ採集道具'),
    'guide_beginners.html': (['headlight','net','cage'],                '🛒 初心者が最初に揃える道具'),
    'guide_night.html':     (['headlight','net'],                       '🛒 夜間採集の必須道具'),
}

for filename, (keys, title) in pages.items():
    filepath = os.path.join(TEMPLATE_DIR, filename)
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # 既存ウィジェットがあれば更新
    marker_start = '<!-- START もしもアフィリエイト かんたんリンク -->'
    marker_end   = '<!-- もしもアフィリエイト END -->\n'
    if marker_start in content:
        s = content.find(marker_start)
        e = content.find(marker_end) + len(marker_end)
        content = content[:s] + build_widget(keys, title) + content[e:]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename} (widget更新)")
        continue

    # amz-section を div深さカウントで置換
    start, end = find_amz_section(content)
    if start is not None:
        content = content[:start] + build_widget(keys, title) + content[end:]
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename} (amz-section置換)")
    else:
        print(f"  ⚠️  置換対象未検出: {filename}")

print("\n完了")
