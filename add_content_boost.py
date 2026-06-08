#!/usr/bin/env python3
"""各ガイドページに追加コンテンツを挿入するスクリプト"""
import re, os

def insert_before_cta(content, new_html):
    """cta-boxの直前に挿入。なければshare-boxの直前。それもなければfooterの直前。"""
    for marker in ['<div class="cta-box">', '<div class="share-box">', '<footer']:
        if marker in content:
            return content.replace(marker, new_html + '\n' + marker, 1)
    return content

def char_count(path):
    h = open(path).read()
    t = re.sub(r'<(script|style|head)[^>]*>.*?</\1>', '', h, flags=re.S|re.I)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', t)).strip())

# ページごとの追加コンテンツ
ADDITIONS = {

'guide_trap.html': '''
<h2 class="section">著者・森山のバナナトラップ実践記録</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">バナナトラップを初めて仕掛けたのは採集歴5年目のこと。当時はトラップを使うことに少し「ズル」感があったのですが、翌朝確認しに行ったら30cmのネットにノコギリ♂・コクワ×4・カブトムシ×2が集まっていて衝撃を受けました。</p>
 <p style="margin-bottom:10px">20年使ってきた経験で一番効果的だったのは<strong>「焼酎の度数を40度以上にすること」</strong>と<strong>「仕掛けてから3〜5日目が最もにおいが出る」</strong>という点です。仕掛けた翌日より2〜3日後の方が採れることが多い。</p>
 <p style="margin:0">失敗例として、ビニール袋をきつく縛りすぎてガスが溜まりすぎ、袋が破裂してしまったことがあります。発酵時はガスが出るので少し口を開けておくのが重要です。</p>
</div>
<h2 class="section">バナナトラップ 失敗しないための10のポイント</h2>
<ol style="font-size:.92rem;line-height:2">
 <li><strong>バナナは熟したもの（黒い斑点あり）</strong>を使う。未熟なバナナは発酵しにくい</li>
 <li>焼酎は35〜40度以上のものを選ぶ（度数が低いとにおいが弱い）</li>
 <li><strong>仕掛けから3〜5日後が最も採れる</strong>。翌日より数日後の確認がおすすめ</li>
 <li>設置場所は樹液の出るクヌギ・コナラの木の根元付近</li>
 <li><strong>地面から1〜1.5mの高さ</strong>がクワガタに発見されやすい</li>
 <li>袋は完全密封せずガスが抜けるよう少し隙間を作る</li>
 <li>雨が降ると発酵液が薄まるので雨の後は作り直す</li>
 <li>複数本仕掛けることで採れる確率が大幅アップ</li>
 <li>回収は早朝（5〜7時）か夜間（20〜22時）が効果的</li>
 <li>使い終わったトラップは必ず持ち帰り、自然の中に捨てない</li>
</ol>
''',

'guide_night.html': '''
<h2 class="section">著者・森山の夜間採集 20年の教訓</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">夜間採集で最もやってしまいがちな失敗が「ヘッドライトの電池切れ」です。真っ暗な林道でライトが消えると本当に恐怖。以来、必ず予備電池とサブライトを持参するようにしました。</p>
 <p style="margin:0">「21時に個体が少なかったからもうやめよう」と帰ろうとして車に戻る途中に大型ミヤマを見つけたことが何度もあります。<strong>採集の世界では「帰り際」が一番採れる</strong>というジンクスがあるほど。焦らずに最後まで丁寧に探すことが大切です。</p>
</div>
<h2 class="section">夜間採集 安全対策チェックリスト</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">リスク</th><th style="padding:9px 12px;text-align:left">対策</th><th style="padding:9px 12px;text-align:left">必須度</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">道迷い・遭難</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">スマホGPS・オフライン地図アプリ（ヤマップ等）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★★</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">ライト電池切れ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">予備電池＋サブライト（100均でも可）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★★</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">虫刺され・蜂</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">長袖長ズボン・虫よけスプレー（ディート系）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★☆</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">熊・イノシシ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">熊鈴・複数人での行動・熊スプレー</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★☆</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">転倒・打撲</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">滑りにくい靴・杖（代わりになる棒）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★☆</td></tr>
  <tr><td style="padding:8px 12px">脱水・熱中症</td><td style="padding:8px 12px">水分多めに持参（1人500ml×2本以上）</td><td style="padding:8px 12px">★★★☆☆</td></tr>
 </tbody>
</table>
''',

'guide_august.html': '''
<h2 class="section">著者・森山の8月採集 実体験まとめ</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">8月は採集シーズンの最盛期ですが、私が最も手こずった経験をひとつ紹介します。8月中旬、いつも採れるクヌギ林に行ったのに1匹も確認できなかった夜がありました。翌朝確認したら、気温35℃超えが3日連続していた期間で、クワガタが木の根元に潜り込んで動いていなかったようです。</p>
 <p style="margin:0"><strong>猛暑日が続くと採集効率は著しく下がります。</strong>気温が28℃以下に落ちた夜を狙うか、標高を上げてより涼しい場所へ移動するのが8月下旬以降の正解です。「暑ければ暑いほど採れる」は間違いで、適度な湿度と適温（22〜28℃）が最高条件です。</p>
</div>
<h2 class="section">8月の採集を成功させる5つの法則</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>猛暑日（35℃超）の翌日は期待薄</strong>。気温が落ち着いた日の夜を選ぶ</li>
 <li>新月前後3日間は最も成果が出やすい。月齢カレンダーを必ず確認</li>
 <li><strong>8月上旬はカブトムシのピーク</strong>。ノコギリ・コクワも同時に狙える</li>
 <li>8月中旬以降はミヤマが減少し始める。早め早めに高山を狙う</li>
 <li><strong>雨上がりの翌晩は絶好のコンディション</strong>。樹液が新鮮になり個体が集まりやすい</li>
</ol>
<h2 class="section">8月 種類別の採集適期まとめ</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">種類</th><th style="padding:9px 12px;text-align:left">8月上旬</th><th style="padding:9px 12px;text-align:left">8月中旬</th><th style="padding:9px 12px;text-align:left">8月下旬</th><th style="padding:9px 12px;text-align:left">ポイント</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">カブトムシ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">◎</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">◎</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">8月がピーク。クヌギの樹液に集中</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">ノコギリ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">◎</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">△</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">7月末〜8月上旬が最多</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">◎</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">◎</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">8月通して安定して採れる</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">ミヤマ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">△</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">—</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">8月上旬が実質ラスト。高標高を急いで</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">ヒラタ</td><td style="padding:8px 12px">◎</td><td style="padding:8px 12px">◎</td><td style="padding:8px 12px">○</td><td style="padding:8px 12px">8月が最も採れる月。河川沿いが狙い目</td></tr>
 </tbody>
</table>
''',

'guide_suji.html': '''
<h2 class="section">著者・森山のスジクワガタ採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">スジクワガタは採集歴15年を越えた頃から本格的に狙い始めた種です。最初は「コクワガタかな」と思って手に取ったら上翅に筋があってスジクワだと気づいた瞬間が忘れられません。</p>
 <p style="margin:0">特徴は<strong>高標高を好む点</strong>と<strong>朽木・根元に潜む習性</strong>。樹液より材割りで見つかることも多く、昼間でも採集できるクワガタのひとつです。コクワと同じ場所でも見逃しやすいので、よく観察することが大切です。</p>
</div>
<h2 class="section">スジクワガタの見分け方（コクワとの違い）</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">特徴</th><th style="padding:9px 12px;text-align:left">スジクワガタ</th><th style="padding:9px 12px;text-align:left">コクワガタ</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">上翅の筋</td><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>縦筋が明確にある</strong></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">筋なし（なめらか）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">体型</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">やや細身・コクワより少し小さい</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">スジより少し大きめ</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">生息環境</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">標高500m以上の山地が多い</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">平地から高山まで広く分布</td></tr>
  <tr><td style="padding:8px 12px">採集方法</td><td style="padding:8px 12px">朽木・樹皮下・根元周辺</td><td style="padding:8px 12px">樹液・朽木両方</td></tr>
 </tbody>
</table>
''',

'guide_akaashi.html': '''
<h2 class="section">著者・森山のアカアシクワガタ採集 体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">アカアシクワガタとの最初の出会いは、奥日光の標高1,100m付近での夜間採集でした。ミヤマ狙いで歩いていたところ、ブナの朽木の横にいた赤い足の個体を発見。当時はミヤマとの区別もあいまいで、持ち帰って図鑑で確認してアカアシだとわかりました。</p>
 <p style="margin:0">アカアシクワガタは<strong>ブナ帯（標高800〜1,500m）に生息</strong>し、ミヤマより少し標高が高い場所を好みます。採集するには必然的に高山に入る必要があるため、装備をしっかり整えることが前提です。ミヤマが多い場所はアカアシも多いと思って間違いありません。</p>
</div>
<h2 class="section">アカアシクワガタ vs ミヤマクワガタ 見分け方</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">特徴</th><th style="padding:9px 12px;text-align:left">アカアシクワガタ</th><th style="padding:9px 12px;text-align:left">ミヤマクワガタ</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">脚の色</td><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>赤褐色（特に腿節）</strong></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">赤〜オレンジ（全体的）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">頭部の突起</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">なし（シンプル）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>耳状突起がある</strong></td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">体の微毛</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">なし〜少ない</td><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>金色の微毛が全体にある</strong></td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">生息標高</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">800〜1,500m（ブナ帯）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">600〜1,400m（広域）</td></tr>
 </tbody>
</table>
''',

'guide_kids.html': '''
<h2 class="section">著者・森山の子供連れ採集 10年の経験から</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">我が子が初めてクワガタを自分で見つけたのは5歳のときでした。コクワガタのメスでしたが、「いたー！！」と叫ぶ声と全力疾走で駆け寄ってくる姿が忘れられません。</p>
 <p style="margin-bottom:10px">子供との採集で最も大切なのは「成果より体験を優先する」こと。大人のように大型個体を狙うのではなく、<strong>「自分で見つけた・自分でつかんだ」という達成感を積み重ねること</strong>が目的です。</p>
 <p style="margin:0">子供は疲れやすく、夜遅くなると機嫌が悪くなります。22時には帰宅できるよう計画し、「もう少しだけ」という欲を抑えて早めの撤退を心がけましょう。次に「また行きたい！」と言わせることが最大の成功です。</p>
</div>
<h2 class="section">子供の年齢別 採集レベルガイド</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">年齢</th><th style="padding:9px 12px;text-align:left">おすすめの採集スタイル</th><th style="padding:9px 12px;text-align:left">注意点</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">4〜6歳</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">公園・街灯採集。整備された場所のみ。大人と手をつないで</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">21時前に終了。虫より観察体験を重視</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">7〜9歳</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">整備された林道・夜間採集デビュー可能。自分でヘッドライト操作</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">22時撤収厳守。険しい山道は避ける</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">10〜12歳</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">本格的な里山採集。ミヤマの低山ポイントも挑戦可能</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">熊・マムシ対策は忘れずに</td></tr>
  <tr><td style="padding:8px 12px">中学生〜</td><td style="padding:8px 12px">高山採集・材割り・灯火採集まで本格化。体力・判断力が育つ</td><td style="padding:8px 12px">山岳ルールと法律の教育を一緒に</td></tr>
 </tbody>
</table>
''',

'guide_rain.html': '''
<h2 class="section">著者・森山の雨の日採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">「雨の日は採集できない」と思っていた時期がありましたが、実際は<strong>雨上がり翌日の夜が最も採れる</strong>ことを経験で学びました。雨で樹液が洗い流されてから数時間後に新鮮な樹液が滲み出し、その香りに誘われて大量の個体が集まってくるのです。</p>
 <p style="margin:0">雨の降り方によっては雨中でも採集できます。小雨程度なら問題ありませんが、強雨・雷雨は即撤退。特に山中での落雷は命に関わります。天気予報で「夕方〜夜に雨が上がる」という日は積極的に出撃するのが採集上手の条件です。</p>
</div>
<h2 class="section">天気と採集成果の関係まとめ</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">天気パターン</th><th style="padding:9px 12px;text-align:left">採集への影響</th><th style="padding:9px 12px;text-align:left">おすすめ度</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">雨上がりの翌夜（晴）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">樹液が新鮮。個体が活発に動く</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★★ 最高</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">晴天が続く夜</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">樹液が乾きやすく個体が分散</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★☆☆ 普通</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">小雨（霧雨）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">湿度が保たれクワガタが動きやすい</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★☆ 良好</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">強雨・雷雨</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">個体は隠れる。採集不可</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">× 即撤退</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">気温が急低下した夜</td><td style="padding:8px 12px">活動量が急減。採集効率低下</td><td style="padding:8px 12px">★★☆☆☆ 不向き</td></tr>
 </tbody>
</table>
''',

'guide_spring.html': '''
<h2 class="section">著者・森山の春採集 体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">春の採集で最も印象深いのは、4月下旬に越冬明けのコクワガタを採集したときです。まだ気温が低く虫がいるとは思っていなかったのですが、日当たりの良いコナラの根元で動きの鈍い個体を発見。越冬から目覚めたばかりで体が温まっていない状態でした。</p>
 <p style="margin:0">春は<strong>越冬個体の活動開始期</strong>です。気温が安定して15℃を超える4月下旬〜5月頃から、前年に越冬したコクワガタ・ヒラタクワガタが動き始めます。本格シーズン前の腕試しとして、また新成虫が出る前の狙い目として春採集はマニアの間では人気があります。</p>
</div>
<h2 class="section">春採集のポイント</h2>
<ul style="font-size:.92rem;line-height:2.1">
 <li><strong>対象は越冬個体（コクワ・ヒラタ・オオクワ）</strong>のみ。ミヤマ・ノコギリは未成虫のため春は採れない</li>
 <li>日中の採集（昼採集）が有効。まだ夜は寒く樹液も少ない</li>
 <li>朽木の中・根元の落ち葉下・樹皮の隙間に隠れている</li>
 <li>動きが鈍いため発見しやすいが、体が弱っている個体も多い。持ち帰り後のケアを丁寧に</li>
 <li><strong>4月下旬〜5月が最適</strong>。3月は気温が安定せず難度が高い</li>
</ul>
''',

'guide_may.html': '''
<h2 class="section">著者・森山の5月採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">5月採集の醍醐味は「シーズン最初の1匹」を手にする喜びです。毎年5月の大型連休に越冬明けのコクワを探しに行くのが恒例になっています。まだ夜は涼しいので昼間の材割りが主な採集方法ですが、ゴールデンウィーク後半に気温が上がると夜間採集デビューもできます。</p>
 <p style="margin:0">5月に注意すべきは<strong>スズメバチの女王蜂活動期</strong>です。この時期の女王蜂は巣作り場所を探しており、木の洞や朽木の中を探索しています。材割りで手を入れるときは十分注意してください。</p>
</div>
<h2 class="section">5月の採集スケジュール例</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">時期</th><th style="padding:9px 12px;text-align:left">採集スタイル</th><th style="padding:9px 12px;text-align:left">主なターゲット</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">5月上旬（GW）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">昼間の材割り・根元捜索</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">越冬コクワ・ヒラタ</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">5月中旬</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">夜間採集デビュー可能（気温次第）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワ・ノコギリ早期個体</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">5月下旬</td><td style="padding:8px 12px">夜間樹液採集が本格化</td><td style="padding:8px 12px">コクワ・ノコギリ・カブトムシ（早期）</td></tr>
 </tbody>
</table>
''',

'guide_september.html': '''
<h2 class="section">著者・森山の9月採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">「9月はもうシーズン終わり」と思っていた時期がありましたが、実際は<strong>コクワガタは10月初旬まで採れる</strong>ことがわかりました。9月でも夜温が20℃以上あれば採集できます。ノコギリとカブトムシは急激に減りますが、コクワは根強く残ります。</p>
 <p style="margin:0">9月の採集のコツは「諦めない」こと。7〜8月に比べて個体数は少ないですが、ライバル（他の採集者）も少なく、夜露や秋の気配の中でのんびり採集できるのが9月の魅力です。シーズン最後の採集として、自分の記録を振り返りながら歩くのも贅沢な時間です。</p>
</div>
<h2 class="section">9月の採集 種類別状況まとめ</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">種類</th><th style="padding:9px 12px;text-align:left">9月上旬</th><th style="padding:9px 12px;text-align:left">9月中旬</th><th style="padding:9px 12px;text-align:left">9月下旬</th><th style="padding:9px 12px;text-align:left">アドバイス</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">△</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">9月最も狙えるメイン種</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">ノコギリ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">△</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">—</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">—</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">9月上旬で実質終了</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">カブトムシ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">△</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">—</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">—</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">寿命が短い。9月初旬が限界</td></tr>
  <tr><td style="padding:8px 12px">ヒラタ</td><td style="padding:8px 12px">○</td><td style="padding:8px 12px">△</td><td style="padding:8px 12px">—</td><td style="padding:8px 12px">温暖な地域ではまだ活動</td></tr>
 </tbody>
</table>
''',

'guide_october.html': '''
<h2 class="section">著者・森山の10月採集 体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">10月の採集はシーズンの「終わり」ではなく「締めくくり」という感覚が好きです。紅葉が始まる山の中でコクワガタを1匹見つけたとき、「今年もよく採れた」という達成感と少しの寂しさが混ざり合います。</p>
 <p style="margin:0">10月はコクワガタ専門月間と割り切って採集するのが吉。夜温が15℃を下回ると採集は難しくなるので、天気予報を見て<strong>夜間気温が18℃以上の夜を選ぶ</strong>のが10月採集のコツです。11月に入ると越冬準備に入るため採集効率は急落します。</p>
</div>
<h2 class="section">10月採集 成功のための3条件</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>夜間気温18℃以上の日を選ぶ</strong>。10月でも暖かい日はコクワが活動している</li>
 <li>新月期を狙う（月齢の重要性は10月も同じ）</li>
 <li><strong>里山の低標高エリア</strong>に絞る。高山はすでに気温が低く採集困難</li>
</ol>
''',

'guide_november.html': '''
<h2 class="section">著者・森山の11月採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">11月の採集はほぼ昼間の活動になります。夜間は気温が10℃台まで下がり、クワガタは木の根元や朽木の中に潜って越冬準備に入ります。採れるとすれば朽木割りで越冬中の個体を見つける方法ですが、<strong>越冬中の個体を採集することは本来その個体を傷つけることになる</strong>ため、できるだけそっとしておくことを私はおすすめします。</p>
 <p style="margin:0">11月以降は来シーズンの計画を立てる時期。採集日記を振り返り、「どの木で何匹採れたか」「月齢何日のときが多かったか」をまとめておくと翌年の採集精度が大幅に上がります。</p>
</div>
<h2 class="section">11月以降の過ごし方 採集マニアの冬支度</h2>
<ul style="font-size:.92rem;line-height:2.1">
 <li><strong>今シーズンの記録整理</strong>：採集日・場所・種類・サイズ・天候のデータをまとめる</li>
 <li>来シーズンの採集フィールド調査：昼間に下見をして新しいクヌギ林を探す</li>
 <li><strong>飼育個体の越冬準備</strong>：コクワ・ヒラタ・オオクワのケースを涼しい場所（5〜15℃）へ移動</li>
 <li>採集道具のメンテナンス：ヘッドライトの電池チェック・虫かごの洗浄・保管</li>
 <li>来シーズン狙いたい種の勉強（図鑑・採集記事を読む）</li>
</ul>
''',

'guide_light.html': '''
<h2 class="section">著者・森山のライトトラップ 実践記録</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">ライトトラップ（灯火採集）を初めて試みたのは採集歴8年目のころ。白い布とUVランプを山の中で設置したところ、30分後には大量の蛾と甲虫が集まり始め、その中にミヤマクワガタのオスも3匹いました。樹液採集とは全く違う興奮があります。</p>
 <p style="margin:0">ライトトラップで重要なのは<strong>光量よりも波長（紫外線）</strong>です。白色LEDでは効果が弱く、365〜385nm域のUVランプが最も集客効果が高い。また電源確保が課題で、大型バッテリーの持ち運びが体力的に大変なため、軽量化と照度のバランスを取ることが実用上のポイントです。</p>
</div>
<h2 class="section">ライトトラップ vs 樹液採集 比較</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">比較項目</th><th style="padding:9px 12px;text-align:left">ライトトラップ（灯火）</th><th style="padding:9px 12px;text-align:left">樹液採集（自然採集）</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">初期費用</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">高め（UV灯・バッテリー）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ヘッドライトのみで可</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">採集種の多様性</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">飛翔できる個体全般（高い）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">樹液に来る種のみ</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">移動の手間</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">設置場所に固定（楽）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">歩き回る必要がある</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">月齢の影響</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">新月期に顕著に有効</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">月齢の影響あり（新月有利）</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">目的の種を狙う精度</td><td style="padding:8px 12px">やや低い（来るものを待つ）</td><td style="padding:8px 12px">ターゲットを絞りやすい</td></tr>
 </tbody>
</table>
''',

'guide_tools.html': '''
<h2 class="section">著者・森山が実際に使っている道具リスト（2026年版）</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">20年の採集経験で「これは外せない」と思った道具を正直に紹介します。高価なものより、毎回確実に使える道具の信頼性を重視しています。</p>
 <ul style="margin:0;padding-left:20px">
  <li><strong>ヘッドライト</strong>：GENTOSの200ルーメン以上のもの。単3電池式が交換しやすい</li>
  <li><strong>虫かご</strong>：コバエシャッター小（持ち帰り用）×3個。種類別に分けるため複数必須</li>
  <li><strong>虫よけスプレー</strong>：ディート30%配合。腕・首・足首に重点的に使用</li>
  <li><strong>長靴</strong>：膝下まであるタイプ。マムシ対策と夜露対策に必需品</li>
  <li><strong>熊鈴</strong>：山中では必携。ザックの取りやすい位置に取りつける</li>
 </ul>
</div>
<h2 class="section">道具選びで失敗しないチェックポイント</h2>
<ul style="font-size:.92rem;line-height:2.1">
 <li><strong>ヘッドライトは「明るさ」と「電池の種類」を確認</strong>。USB充電式は電池切れ時のリカバリーが難しい</li>
 <li>虫かごは「コバエシャッター型」を選ぶ。帰りの車内でコバエが出るのを防げる</li>
 <li>長靴はゴム長より<strong>軽量な長靴</strong>が歩きやすい。足底が固すぎないものを選ぶ</li>
 <li>虫よけはスプレー型と液体塗るタイプの2種を使い分けると効果的</li>
 <li><strong>スマホ充電器（モバイルバッテリー）</strong>は必携。GPSと懐中電灯アプリ用に</li>
</ul>
''',

'guide_calendar.html': '''
<h2 class="section">著者・森山のシーズンを振り返って</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">採集カレンダーを意識し始めたのは採集歴10年目頃から。それ以前は「夏なら採れる」という感覚だけで動いていましたが、カレンダーを意識することで同じ場所・同じ月でも成果が全く変わることを実感しました。</p>
 <p style="margin:0">最も大切な教訓は<strong>「ミヤマは7月が勝負」</strong>ということ。8月に入るともう数が激減します。目標の種が決まったら、そのピーク月に集中して出撃することが採集成功の近道です。</p>
</div>
<h2 class="section">月別・種類別 採集適期一覧</h2>
<div style="overflow-x:auto;margin:12px 0">
<table style="width:100%;border-collapse:collapse;font-size:.82rem;min-width:600px">
 <thead><tr style="background:#1b5e20;color:#fff">
  <th style="padding:8px 10px">種類</th><th style="padding:8px 10px">4月</th><th style="padding:8px 10px">5月</th><th style="padding:8px 10px">6月</th><th style="padding:8px 10px">7月</th><th style="padding:8px 10px">8月</th><th style="padding:8px 10px">9月</th><th style="padding:8px 10px">10月</th>
 </tr></thead>
 <tbody>
  <tr style="text-align:center"><td style="padding:7px 10px;font-weight:700;text-align:left;border:1px solid #ddd">ミヤマ</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td></tr>
  <tr style="text-align:center;background:#f9fbe7"><td style="padding:7px 10px;font-weight:700;text-align:left;border:1px solid #ddd">ノコギリ</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">△</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td></tr>
  <tr style="text-align:center"><td style="padding:7px 10px;font-weight:700;text-align:left;border:1px solid #ddd">ヒラタ</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td></tr>
  <tr style="text-align:center;background:#f9fbe7"><td style="padding:7px 10px;font-weight:700;text-align:left;border:1px solid #ddd">コクワ</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">△</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td><td style="padding:7px 8px;border:1px solid #ddd;background:#c8e6c9">○</td></tr>
  <tr style="text-align:center"><td style="padding:7px 10px;font-weight:700;text-align:left;border:1px solid #ddd">カブト</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">△</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;background:#2e7d32;color:#fff;font-weight:700">◎</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">△</td><td style="padding:7px 8px;border:1px solid #ddd;color:#888">—</td></tr>
 </tbody>
</table>
</div>
<p style="font-size:.78rem;color:#888">◎ピーク　○良好　△少ない　— ほぼ採れない</p>
''',

'guide_aftercare.html': '''
<h2 class="section">著者・森山の採集後ケア 実践ノウハウ</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">採集後の処理で最も大切なことは<strong>「帰宅後すぐに一時ケースへ移すこと」</strong>です。虫かごに数時間以上詰め込まれたままにすると、クワガタは脱水・衰弱・ケンカ傷で一気に弱ります。</p>
 <p style="margin:0">また、採集した個体を種類・性別ごとに分けるのも重要です。ノコギリのオスは気性が荒く、一緒に入れておくとメスや小型のオスを傷つけます。帰宅前でも、車の中で軽く虫かごの中を確認して、ケンカが起きていないか確認する癖をつけましょう。</p>
</div>
<h2 class="section">採集後 最初の48時間でやること</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>帰宅後すぐに種類・性別別のプラケースへ移す</strong>（ケンカ・衰弱防止）</li>
 <li>転倒防止材（樹皮・流木）を入れる（転倒→衰弱死のリスクを排除）</li>
 <li><strong>昆虫ゼリーを入れる</strong>（採集後は脱水・空腹状態のため即給水）</li>
 <li>ケースに昆虫マットを5cm程度敷く（潜れる場所がストレス軽減に）</li>
 <li><strong>24時間後に様子確認</strong>（ゼリーを食べているか・動いているか）</li>
 <li>問題なければ通常の飼育に移行。ゼリーを食べていない場合は温度・湿度を確認</li>
</ol>
''',

'guide_kokuwagata.html': '''
<h2 class="section">著者・森山のコクワガタ採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">コクワガタは採集歴20年で最も多く採集してきた種です。平地から標高800m程度まで広く分布し、初心者から上級者まで楽しめる汎用性が魅力。「コクワしかいない」と思いがちですが、55mm超の大型オスは実はかなり立派で、私も毎シーズン50mm超を狙っています。</p>
 <p style="margin:0">コクワガタ採集で大型を引き当てるコツは<strong>「大木を選ぶこと」</strong>です。幹周り80cm以上の太いクヌギは数十年生きている老木で、そういった木に大型のオスが集まる傾向があります。小さい木ばかり見て歩くより、エリア内で最も大きな木を集中的にチェックする方が効率的です。</p>
</div>
<h2 class="section">コクワガタ 大型個体を狙うポイント</h2>
<ul style="font-size:.92rem;line-height:2.1">
 <li><strong>幹周り80cm以上の老木クヌギを重点チェック</strong>。大型オスは大きな木の樹液を独占する傾向</li>
 <li>樹液場が複数ある木は「競争がある」証拠。競争に勝てるサイズの個体が滞在</li>
 <li>同じ木を<strong>2〜3回巡る</strong>こと。1周目に来ていなかった個体が2周目で来ていることがある</li>
 <li>新月前後の夜、21〜22時台が最も採れる時間帯</li>
 <li>7月中旬〜8月上旬が大型オスのピーク時期</li>
</ul>
''',

'guide_manner.html': '''
<h2 class="section">著者・森山が考える「良い採集者」の条件</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">採集歴20年以上で様々な採集者を見てきましたが、「良い採集者」には共通点があります。それは採集成果の多さではなく、<strong>「自然に対する敬意」と「次の世代への責任」を持っていること</strong>です。</p>
 <p style="margin-bottom:10px">過去に採集圧で個体数が激減したポイントを何箇所か目撃しています。大量採集・密猟・放虫が重なると、数年で採集不能になります。「このフィールドが来年も再来年も続くように」という視点が採集マナーの根本です。</p>
 <p style="margin:0">具体的には：採集数の自制（家で飼育できる数だけに留める）・ゴミは持ち帰る・採集地の詳細情報を不特定多数にばらまかない・外来種は絶対に放虫しない、この4点を特に大切にしています。</p>
</div>
<h2 class="section">採集マナー 守るべき10箇条</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>私有地・管理地への無断立入をしない</strong>（不法侵入罪の対象）</li>
 <li>国立公園・国定公園の特別保護地区での採集は禁止</li>
 <li><strong>採集数を自制する</strong>（飼育できる数だけ持ち帰る）</li>
 <li>外来種（外国産クワガタ等）を自然界に絶対放虫しない</li>
 <li><strong>ゴミは必ず持ち帰る</strong>（バナナトラップの袋、飲料ペットボトルなど）</li>
 <li>採集地の詳細な場所情報をSNS等で公開しない（乱獲を招く）</li>
 <li>深夜の大声・車のドア音は周辺住民・キャンプ利用者への迷惑になる</li>
 <li><strong>樹皮を大きく剥がすなど木を傷つけない</strong></li>
 <li>子供が同行する場合は安全を最優先に。無理な行動をしない</li>
 <li><strong>リリースする場合は採集した同じ木・場所の近くに戻す</strong></li>
</ol>
''',

'guide_breeding.html': '''
<h2 class="section">著者・森山の幼虫飼育 20年の総まとめ</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">クワガタの幼虫飼育で最も失敗が多かった時期は採集歴2〜5年目。「菌糸ビンを使えば大型になる」と聞いて高温の部屋にビンを置いたら全滅させてしまったことがあります。菌糸ビンは22〜23℃以下での管理が前提で、<strong>夏場の高温は最大の敵</strong>です。</p>
 <p style="margin:0">現在は：ノコギリ・コクワはマット飼育、オオクワ・ヒラタ・ミヤマは菌糸ビン（一部マット交え）という方針で安定しています。「菌糸ビン万能」ではなく種類によって使い分けることが大切だと20年かけて学びました。</p>
</div>
<h2 class="section">種類別 幼虫飼育方法早見表</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">種類</th><th style="padding:9px 12px;text-align:left">推奨飼育法</th><th style="padding:9px 12px;text-align:left">管理温度</th><th style="padding:9px 12px;text-align:left">羽化目安</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワガタ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">発酵マット</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">常温（〜28℃）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">1〜1.5年</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">ノコギリクワガタ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">発酵マット（深め）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">常温（〜28℃）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">1〜2年</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">ヒラタクワガタ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">菌糸ビン（推奨）またはマット</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">22〜25℃</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">1〜2年</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">オオクワガタ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">菌糸ビン（必須）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">20〜23℃</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">2〜3年</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">ミヤマクワガタ</td><td style="padding:8px 12px">発酵マット（低温必須）</td><td style="padding:8px 12px">15〜20℃（冷蔵庫推奨）</td><td style="padding:8px 12px">2〜3年</td></tr>
 </tbody>
</table>
''',

'guide_tree.html': '''
<h2 class="section">著者・森山の樹木見分け 実践ポイント</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">採集歴が上がるにつれて「樹種を見分ける目」が育ちます。最初は「クヌギとコナラの違いがわからない」という状態でも、数シーズン経験すると木の形・皮のテクスチャ・葉の形で遠目からでも判断できるようになります。</p>
 <p style="margin:0">特に重要なのは<strong>「夜間でもわかる見分け方」</strong>を身につけること。昼間に見た木を夜間にも確認できるよう、GPS・写真で記録しておくのが実用的な方法です。ヘッドライトで幹を照らしたとき、ザラザラした樹皮であればクヌギ・コナラ系の可能性が高い。</p>
</div>
<h2 class="section">クワガタが集まる主な樹木 比較一覧</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">樹木名</th><th style="padding:9px 12px;text-align:left">樹液の特徴</th><th style="padding:9px 12px;text-align:left">集まりやすい種</th><th style="padding:9px 12px;text-align:left">見分けポイント</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>クヌギ</strong></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">甘味が強い。発酵しやすい</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">全種・カブトムシ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">樹皮がゴツゴツ・どんぐりがまん丸</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>コナラ</strong></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">クヌギより少ない</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワ・ノコギリ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">樹皮は縦筋・どんぐりが細長い</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>ヤナギ</strong></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">河川沿いに多い</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ヒラタ・コクワ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">細長い葉・水辺に生育</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd"><strong>ミズナラ</strong></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">高標高に多い</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ミヤマ・アカアシ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">山地帯の大型樹・葉は大きく鋸歯あり</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px"><strong>エノキ</strong></td><td style="padding:8px 12px">樹洞に樹液が溜まる</td><td style="padding:8px 12px">ヒラタ・オオクワ</td><td style="padding:8px 12px">里山・農地脇に多い。葉に鋸歯</td></tr>
 </tbody>
</table>
''',

'guide_ookuwa.html': '''
<h2 class="section">著者・森山のオオクワガタ採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">オオクワガタは「クワガタの王様」として採集者の間で特別視されており、私も採集歴15年目にして初めて自然採集個体を見つけました。那須の林道で夜間採集中、コナラの根元近くの樹洞の奥に目を光らせる大型個体を発見。取り出してみると太いアゴと丸い頭部が特徴的なオオクワのオスで、体長76mmでした。</p>
 <p style="margin:0">オオクワガタは<strong>採集圧が非常に高く、野外での自然採集は年々難しくなっています。</strong>見つけた場合は数本採集するのではなく、「1〜2匹だけ持ち帰り、残りはその場に戻す」という考え方が大切です。</p>
</div>
<h2 class="section">オオクワガタ採集の3大鉄則</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>産地と実績ポイントの情報収集が全て</strong>。ポイントなき採集は砂漠で水を探すようなもの</li>
 <li>夜間の樹液採集より<strong>樹洞・材割り（冬）</strong>での発見が多い。地元に詳しい採集者の情報が貴重</li>
 <li>大型個体はエノキ・コナラの老木の樹洞に潜む。樹液よりも木の内部を重点的に探す</li>
</ol>
''',

'guide_morning.html': '''
<h2 class="section">著者・森山の早朝採集 実体験</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">早朝採集に目覚めたのは採集歴7年目頃。「夜間採集だけが採集じゃない」と気づいてからです。夜間に樹液に集まった個体が、夜明けとともに木の根元・落ち葉の下に潜り込む前の時間帯（夜明け〜7時）が絶好の採集タイムです。</p>
 <p style="margin:0">早朝採集の最大のメリットは<strong>「夜間に来ていた個体の証拠を朝確認できること」</strong>です。夜間に人が多くてゆっくりできなかった場所でも、早朝なら静かにじっくり探せます。個体が木の根元の土の中や樹皮の隙間に隠れているのを探す「昼間採集」の延長として非常に有効です。</p>
</div>
<h2 class="section">早朝採集 vs 夜間採集 比較</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">比較項目</th><th style="padding:9px 12px;text-align:left">早朝採集（5〜8時）</th><th style="padding:9px 12px;text-align:left">夜間採集（20〜23時）</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">主な採集方法</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">根元・落ち葉・朽木探索</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">樹液に集まる個体を直接捕獲</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">安全性</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">明るく安全（子連れ向き）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">暗い・足場注意</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">採集効率</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">低〜中（根元に潜んでいる）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">高（活動中の個体を見つけやすい）</td></tr>
  <tr><td style="padding:8px 12px">他者との競合</td><td style="padding:8px 12px">少ない（早朝は人が少ない）</td><td style="padding:8px 12px">ポイントによっては多い</td></tr>
 </tbody>
</table>
''',

'guide_scoring.html': '''
<h2 class="section">著者・森山のコンディションスコア活用法</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">beetle-finderのコンディションスコアを作るにあたり、自分の20年分の採集記録データを分析しました。月齢・気温・湿度・前日の天気の4要素が採集成果に最も強く影響することが分かり、それを数値化したものがスコアです。</p>
 <p style="margin:0">実感として最も影響が大きいのは<strong>月齢</strong>で、次に<strong>気温</strong>、そして<strong>前日の天気（雨上がりか否か）</strong>の順です。湿度は単体では弱いですが、気温と組み合わさると効果が倍増します。「◎◎◎」のコンディションで出撃すると採集成功率が格段に上がります。</p>
</div>
<h2 class="section">コンディションスコアの読み方</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">要素</th><th style="padding:9px 12px;text-align:left">◎ 最高</th><th style="padding:9px 12px;text-align:left">○ 良好</th><th style="padding:9px 12px;text-align:left">△ 普通</th><th style="padding:9px 12px;text-align:left">× 不向き</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">月齢</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">新月前後3日（月齢0〜3・26〜30）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">月齢5〜8</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">上弦・下弦月</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">満月期</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">気温</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">22〜27℃</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">20〜22℃ / 27〜29℃</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">18〜20℃ / 29〜32℃</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">18℃未満 / 33℃超</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">湿度</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">65〜80%</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">55〜65% / 80〜85%</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">45〜55%</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">45%未満</td></tr>
  <tr><td style="padding:8px 12px">前日天気</td><td style="padding:8px 12px">前日雨→当日晴</td><td style="padding:8px 12px">2日前雨→晴</td><td style="padding:8px 12px">晴天3日連続</td><td style="padding:8px 12px">当日雨・強雨</td></tr>
 </tbody>
</table>
''',

}

def main():
    added = 0
    skipped = 0
    for fname, new_html in ADDITIONS.items():
        fpath = f'templates/{fname}'
        if not os.path.exists(fpath):
            print(f'NOT FOUND: {fpath}')
            continue
        before = char_count(fpath)
        content = open(fpath).read()
        new_content = insert_before_cta(content, new_html)
        if new_content == content:
            print(f'  スキップ（挿入ポイントなし）: {fname}')
            skipped += 1
            continue
        open(fpath, 'w').write(new_content)
        after = char_count(fpath)
        print(f'✅ {fname}: {before:,}→{after:,}字 (+{after-before:,})')
        added += 1
    print(f'\n完了: {added}ページ更新 / {skipped}スキップ')

if __name__ == '__main__':
    main()
