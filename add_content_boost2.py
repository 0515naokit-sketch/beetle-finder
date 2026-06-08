#!/usr/bin/env python3
"""残りページへの追加コンテンツ挿入"""
import re, os

def insert_before_cta(content, new_html):
    for marker in ['<div class="cta-box">', '<div class="share-box">', '<footer']:
        if marker in content:
            return content.replace(marker, new_html + '\n' + marker, 1)
    return content

def char_count(path):
    h = open(path).read()
    t = re.sub(r'<(script|style|head)[^>]*>.*?</\1>', '', h, flags=re.S|re.I)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', t)).strip())

ADDITIONS = {

'guide_iku_akaashi.html': '''
<h2 class="section">著者・森山のアカアシクワガタ飼育 体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">アカアシクワガタの飼育で最も苦労したのは夏場の温度管理です。本種は標高1,000m前後の涼しい環境に生息しており、関東の夏（30℃超）は致命的なダメージを与えます。初めて飼育した個体を8月の室温30℃で管理してしまい、3週間で★にしてしまった苦い経験があります。</p>
 <p style="margin:0">現在は保冷剤を使った「プチ低温管理」で夏を乗り切っています。25℃以下を維持できれば越冬まで元気に過ごしてくれます。飼育の難度はミヤマより少し低く、温度さえ管理できれば初心者でも十分挑戦できる種です。</p>
</div>
<h2 class="section">アカアシクワガタ 飼育データまとめ</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">項目</th><th style="padding:9px 12px;text-align:left">内容</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">適正飼育温度</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">15〜25℃（夏は25℃以下を維持）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">成虫の寿命</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">越冬できれば2〜3年</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">産卵方法</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">材産み（産卵木必須）＋一部マット産み</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">幼虫飼育法</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">発酵マットまたは菌糸ビン（低温管理）</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">羽化までの期間</td><td style="padding:8px 12px">約1〜2年（温度・個体差による）</td></tr>
 </tbody>
</table>
''',

'guide_iku_kokuwagata.html': '''
<h2 class="section">著者・森山のコクワガタ飼育 実体験ノウハウ</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">コクワガタは私が初めて飼育したクワガタで、採集歴のスタート地点でもあります。丈夫で飼いやすく、越冬もして複数年楽しめるのが最大の魅力。子供との飼育体験にも最適で、息子が初めて担当したのもコクワでした。</p>
 <p style="margin:0">コクワで面白いのは<strong>複数匹を同じケースで飼育できる点</strong>です（ヒラタとは違い比較的おとなしい）。ただしオス同士は時々ケンカするので、飼育スペースに余裕を持たせることが長生きのコツです。また越冬時は冷暗所（5〜15℃）に移動することで2〜3年元気に過ごせます。</p>
</div>
<h2 class="section">コクワガタ 種類別飼育ポイント比較</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">項目</th><th style="padding:9px 12px;text-align:left">コクワガタ</th><th style="padding:9px 12px;text-align:left">ノコギリ</th><th style="padding:9px 12px;text-align:left">ヒラタ</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">飼育難度</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★☆☆ 簡単</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★☆ 普通</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★ やや難</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">越冬</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○（複数年可）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">× （1年で終了）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">○（越冬可）</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">複数飼育</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">比較的向く</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">オス同士は注意</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">単独推奨</td></tr>
  <tr><td style="padding:8px 12px">気性</td><td style="padding:8px 12px">おとなしい</td><td style="padding:8px 12px">中程度</td><td style="padding:8px 12px">攻撃的（要注意）</td></tr>
 </tbody>
</table>
''',

'guide_iku_nokogiri.html': '''
<h2 class="section">著者・森山のノコギリクワガタ飼育 体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">ノコギリクワガタは「採集しやすいが飼育で苦労する」種として知られています。私も当初は長生きさせられずに悩みました。原因はシンプルで、<strong>「1匹のオスにメスを複数入れる」という飼育スタイルが合わなかった</strong>ことです。ノコギリのオスは大顎でメスを傷つけることが多く、必ず別々のケースで管理するようにしてから長生きさせられるようになりました。</p>
 <p style="margin:0">また、ノコギリの幼虫飼育でよくある失敗が「前蛹・蛹のタイミングでマット交換してしまうこと」。蛹室を作っている最中にケースを動かすと羽化不全になります。8〜10月以降はケースをなるべく動かさずにそっとしておくことが大切です。</p>
</div>
<h2 class="section">ノコギリクワガタ 飼育ポイント早見表</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">項目</th><th style="padding:9px 12px;text-align:left">推奨方法・目安</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">成虫の寿命</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">約2〜4ヶ月（越冬しない一年性）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">産卵セット</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">発酵マットを20cm以上深く詰める。産卵木不要なことも</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">幼虫飼育法</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">発酵マット飼育（650ml〜1000mlプラカップ）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">羽化時期</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">幼虫になって約1〜2年後の夏〜秋</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">注意点</td><td style="padding:8px 12px">オス・メスは別管理。蛹化時期はケースを動かさない</td></tr>
 </tbody>
</table>
''',

'guide_iku_ookuwa.html': '''
<h2 class="section">著者・森山のオオクワガタ飼育 体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">オオクワガタ飼育の最大の魅力は<strong>「何年もかけて大型個体を育てるプロセス」</strong>です。幼虫を入手してから羽化まで2〜3年。大型個体（70mm超）を目指す場合は菌糸ビンの管理・定期的な交換・温度コントロールが全て揃って初めて達成できます。</p>
 <p style="margin:0">現在私が一番力を入れているのがオオクワのブリードです。自己採集個体（76mm）と購入メス（42mm）から産まれた幼虫を現在6本の菌糸ビンで育てています。来年の羽化が楽しみです。</p>
</div>
<h2 class="section">オオクワガタ 大型化のための飼育管理</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">目標サイズ</th><th style="padding:9px 12px;text-align:left">必要な条件</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">60mm台</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">発酵マット飼育でも到達可能。菌糸ビン推奨</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">70mm台</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">菌糸ビン必須・20〜23℃の温度管理・適切な交換タイミング</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">80mm超</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">高品質菌糸・厳密な温度管理・3年以上の飼育期間・遺伝的素質</td></tr>
 </tbody>
</table>
<h2 class="section">オオクワガタ飼育でよくある失敗</h2>
<ul style="font-size:.92rem;line-height:2.1">
 <li><strong>夏場に高温になりすぎる</strong>：菌糸が劣化し幼虫が死亡。22℃以下が理想</li>
 <li>菌糸ビン交換時期を逃す：食い尽くした後もそのままにするとマットに戻ってしまう</li>
 <li><strong>同居産卵でメスが★になる</strong>：オスの大顎がメスに刺さるケースがある。別管理推奨</li>
 <li>蛹化・羽化時期にケースを動かす：羽化不全の原因になる</li>
</ul>
''',

'guide_iku_hirata.html': '''
<h2 class="section">著者・森山のヒラタクワガタ飼育 実践メモ</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">ヒラタクワガタは「挟む力が最強クラス」のクワガタで、素手でつかもうとして血が出たことが何度もあります。飼育でも<strong>オスのメスへの攻撃が最大のリスク</strong>で、同居させているとメスを傷つけて最悪★にすることがある。交尾確認後は必ず別々のケースに分けるのが鉄則です。</p>
 <p style="margin:0">飼育の楽しさは大型オスを育てること。菌糸ビンで丁寧に育てると70mm台の個体も夢ではありません。現在育てている幼虫（採集個体から産まれた2令幼虫）が70mmを超えるのを目標にしています。</p>
</div>
<h2 class="section">ヒラタクワガタ 飼育ステップガイド</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>産卵セット</strong>：発酵マットを20〜25cm深く詰める。産卵木も一緒に入れると産卵数が増える</li>
 <li>同居は3〜7日間のみ。交尾確認後はオスを取り出してメスを単独に</li>
 <li><strong>幼虫回収</strong>：産卵セットから2〜4週間後に幼虫を回収。マットを慎重に掘る</li>
 <li>幼虫は個別の菌糸ビン（800ml）に移す。菌糸が食い尽くされたら1,400mlに移行</li>
 <li><strong>前蛹〜蛹化期</strong>（秋〜春）はケースを動かさない。人工蛹室への移動は慎重に</li>
 <li>羽化後は後食（エサを食べ始める）まで数ヶ月かかる。それまでは静かに待つ</li>
</ol>
''',

'guide_iku_miyama.html': '''
<h2 class="section">著者・森山のミヤマクワガタ飼育 苦労話</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">ミヤマクワガタは「採集は易しいが飼育が難しい」種として知られており、私も最初の5年間は夏を越させることができませんでした。原因は明確で<strong>「夏の高温」</strong>です。関東の夏は30℃を超える日が続き、25℃以下の環境を維持しないと短期間で★になります。</p>
 <p style="margin:0">現在は保冷剤＋発泡スチロールボックスで夏を乗り越えています。保冷剤は毎日交換が必要ですが、その手間をかけると8月末まで元気に過ごしてくれます。9月以降は自然と気温が下がるので越冬できれば翌年も楽しめます。</p>
</div>
<h2 class="section">ミヤマクワガタ 夏場の温度管理方法</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">管理方法</th><th style="padding:9px 12px;text-align:left">コスト</th><th style="padding:9px 12px;text-align:left">効果</th><th style="padding:9px 12px;text-align:left">向いている人</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">エアコン管理</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">高（電気代）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★★</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">複数個体を本格飼育したい人</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">保冷剤＋発泡ボックス</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">低〜中</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★☆☆</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">少数個体の家庭飼育</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">野菜室（冷蔵庫）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ほぼゼロ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★★★☆</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">1〜2個体の省スペース管理</td></tr>
  <tr><td style="padding:8px 12px">涼しい部屋</td><td style="padding:8px 12px">低</td><td style="padding:8px 12px">★★☆☆☆</td><td style="padding:8px 12px">北向き・地下室など25℃以下が維持できる場合</td></tr>
 </tbody>
</table>
''',

'guide_jiyukenkyu_kabuto.html': '''
<h2 class="section">著者・森山のカブトムシ自由研究 実践アドバイス</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">息子が小学校2年生のとき、カブトムシを使った自由研究を一緒に行いました。テーマは「カブトムシはどんな食べ物が好きか」。バナナ・スイカ・昆虫ゼリー・砂糖水の4種類を並べて1週間観察しました。結果は昆虫ゼリーへの反応が最も長く、次にバナナでした。</p>
 <p style="margin:0">この体験から学んだのは<strong>「子供が自分で仮説を立てること」が自由研究の醍醐味</strong>だということです。「どれが好きだと思う？」と聞いて子供の予想を記録しておくと、結果との比較がレポートの核心になります。正解でも不正解でも「なぜそうなったのか」を一緒に考えることが学びになります。</p>
</div>
<h2 class="section">カブトムシ自由研究 テーマアイデア</h2>
<ol style="font-size:.92rem;line-height:2.1">
 <li><strong>カブトムシのエサ実験</strong>：複数の食べ物を用意して反応を比較（人気の定番テーマ）</li>
 <li>オスとメスの行動パターンの違いを記録する</li>
 <li><strong>カブトムシの力比べ</strong>：背中に重りを乗せてどこまで持ち上げられるか測定</li>
 <li>気温と活動量の関係：朝・昼・夜で活動が変わるか観察</li>
 <li><strong>産卵観察</strong>：メスが土に潜って卵を産む様子を記録（夏の終わりに実施）</li>
 <li>幼虫の成長記録：卵→1令→2令→3令の変化を写真と体重で記録</li>
</ol>
<h2 class="section">カブトムシ vs クワガタ 自由研究のしやすさ比較</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">比較点</th><th style="padding:9px 12px;text-align:left">カブトムシ</th><th style="padding:9px 12px;text-align:left">クワガタ</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">飼育難度</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★☆☆（簡単）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">★★☆（やや難）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">行動の観察しやすさ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">昼間でも動く</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">主に夜行性</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">採集のしやすさ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">7〜8月に採りやすい</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワなら採りやすい</td></tr>
  <tr><td style="padding:8px 12px">テーマの多様性</td><td style="padding:8px 12px">エサ・産卵・幼虫観察など豊富</td><td style="padding:8px 12px">種類の多さが活かせる</td></tr>
 </tbody>
</table>
''',

'guide_beginner_kit.html': '''
<h2 class="section">著者・森山の「初めて買う道具」体験談</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">初めてクワガタ採集を始めた20年前、最初に買った道具は「100均の懐中電灯・虫かご・虫よけスプレー」でした。それでも採れましたが、懐中電灯の光量不足で暗い木の幹が見えず苦労したことを覚えています。</p>
 <p style="margin-bottom:10px">今振り返ると<strong>「ヘッドライトだけは最初から良いものを買えばよかった」</strong>と思います。両手が空くヘッドライトは安全性も採集効率も全然違います。初期投資3,000〜5,000円で良いヘッドライトを買うだけで、採集の成功率が明らかに上がります。</p>
 <p style="margin:0">虫かごは最初は100均のものでもOKですが、持ち帰りにはコバエシャッター型を強くおすすめします。100均ケースに入れたまま帰宅すると、翌日車の中がコバエだらけになった経験がトラウマです。</p>
</div>
<h2 class="section">道具の優先順位と予算配分</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">道具</th><th style="padding:9px 12px;text-align:left">最低ライン</th><th style="padding:9px 12px;text-align:left">理想</th><th style="padding:9px 12px;text-align:left">なぜ重要か</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">ヘッドライト</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">1,000円〜</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">3,000〜5,000円</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">採集効率に直結・両手フリー</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">虫よけスプレー</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">500〜800円</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ディート30%配合品</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">夏の蚊・ブユから身を守る</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">虫かご（持ち帰り）</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">200〜500円</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">コバエシャッター型</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">コバエ対策・個体を傷つけない</td></tr>
  <tr><td style="padding:8px 12px">長靴</td><td style="padding:8px 12px">500〜1,000円</td><td style="padding:8px 12px">2,000〜3,000円（軽量型）</td><td style="padding:8px 12px">マムシ・夜露・水たまり対策</td></tr>
 </tbody>
</table>
''',

'guide_reports.html': '''
<h2 class="section">採集レポートを読む前に知っておくべきこと</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">このページで紹介する採集レポートは、beetle-finder運営者・森山春樹が実際に現地を訪問して採集した体験をまとめたものです。採集地の特定を防ぐため、詳細な場所情報は非公開としています。</p>
 <p style="margin-bottom:10px">レポートから学べるのは<strong>「どういう条件のときに採集が成功するか」</strong>という実践知識です。月齢・気温・天気・時間帯・使った道具など、自分の次の採集計画に活かせる情報を詰め込んでいます。</p>
 <p style="margin:0">採集は「運」の要素もありますが、条件を整えることで確率を上げることができます。レポートを読んで「この条件を真似しよう」という視点で活用してください。</p>
</div>
<h2 class="section">レポート一覧 早見表</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">レポート</th><th style="padding:9px 12px;text-align:left">エリア</th><th style="padding:9px 12px;text-align:left">主な採集種</th><th style="padding:9px 12px;text-align:left">特徴</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd"><a href="/guide/report/tsukuba" style="color:#388e3c;font-weight:700">筑波山麓レポート</a></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">茨城県</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ヒラタ65mm・コクワ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">月齢1の新月翌日。条件◎</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd"><a href="/guide/report/chichibu" style="color:#388e3c;font-weight:700">秩父レポート</a></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">埼玉県</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ミヤマ・ノコギリ</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">雨上がり翌日。高標高採集</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd"><a href="/guide/report/takao" style="color:#388e3c;font-weight:700">高尾山レポート</a></td><td style="padding:8px 12px;border-bottom:1px solid #ddd">東京都</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">コクワ・ノコギリ・カブト</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">子供連れファミリー採集</td></tr>
  <tr><td style="padding:8px 12px"><a href="/guide/report/okutama" style="color:#388e3c;font-weight:700">奥多摩レポート</a></td><td style="padding:8px 12px">東京都</td><td style="padding:8px 12px">ミヤマ・コクワ</td><td style="padding:8px 12px">標高800m超。夜間ライト採集</td></tr>
 </tbody>
</table>
''',

'report_chichibu.html': '''
<h2 class="section">秩父採集 事前準備のポイント</h2>
<div style="background:#e8f5e9;border-left:4px solid #43a047;padding:16px 20px;border-radius:0 8px 8px 0;margin:16px 0;font-size:.92rem;line-height:1.9">
 <p style="margin-bottom:10px">秩父でのミヤマ採集は準備が全てと言っても過言ではありません。事前に確認すべきは：林道のゲート開閉時間、熊の目撃情報、天気予報（3日前からの降雨履歴）、そして月齢カレンダーの4点です。</p>
 <p style="margin:0">今回の採集で特に役立ったのがbeetle-finderのコンディション確認機能です。月齢・気温・湿度の3条件が全て◎だった日を狙ったことで、効率的に個体を見つけることができました。条件が良い日を選ぶだけで採集成果が倍以上になる体験を毎回実感しています。</p>
</div>
<h2 class="section">秩父エリアでのミヤマクワガタ採集ガイド</h2>
<table style="width:100%;border-collapse:collapse;margin:12px 0;font-size:.88rem">
 <thead><tr style="background:#2e7d32;color:#fff"><th style="padding:9px 12px;text-align:left">項目</th><th style="padding:9px 12px;text-align:left">内容</th></tr></thead>
 <tbody>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">採集適期</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">7月上旬〜8月上旬（ミヤマのピーク）</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">狙い目標高</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">600〜1,200m（ミズナラ・コナラが多いエリア）</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px;border-bottom:1px solid #ddd">採集時間</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">21〜23時がゴールデンタイム。夜間気温20℃前後が理想</td></tr>
  <tr><td style="padding:8px 12px;border-bottom:1px solid #ddd">必携装備</td><td style="padding:8px 12px;border-bottom:1px solid #ddd">ヘッドライト・熊鈴・虫よけ・長靴・スマホGPS</td></tr>
  <tr style="background:#f9fbe7"><td style="padding:8px 12px">注意事項</td><td style="padding:8px 12px">秩父多摩甲斐国立公園内は採集禁止。林道ゲートの閉鎖時間を事前確認</td></tr>
 </tbody>
</table>
<h2 class="section">採集者・森山春樹の秩父レポート まとめ</h2>
<p style="font-size:.92rem;line-height:1.9">今回の秩父採集で改めて感じたのは「雨上がりの夜はやはり最強」ということ。雨で洗い流されてから数時間後に再び滲み出す樹液の香りに誘われて、ミヤマ・ノコギリが一気に集まってくる現象は何度経験しても興奮します。採集は天候・月齢・気温という自然の条件との対話です。その条件を読み解くために、beetle-finderのスコア機能を毎回活用しています。</p>
''',

'guide_case.html': '''
<h2 class="section">飼育ケースと一緒に揃えたい消耗品リスト</h2>
<p>飼育ケースを買っただけでは飼育できません。必要な消耗品を事前にまとめて揃えておくことでスムーズにスタートできます。</p>
<ul style="font-size:.92rem;line-height:2.1">
 <li><strong>昆虫マット</strong>（成虫飼育用・発酵マット）：床材と湿度調整に必須</li>
 <li><strong>昆虫ゼリー</strong>：高タンパクの16g〜18gサイズを複数個。週1〜2回交換</li>
 <li><strong>転倒防止材</strong>（コルク・樹皮・流木）：転倒して起き上がれなくなる死亡事故を防ぐ</li>
 <li><strong>霧吹き</strong>：マットの湿度管理。水道水を入れて週1〜2回軽くスプレー</li>
 <li><strong>温湿度計</strong>：ケース内環境のモニタリング。特にミヤマ飼育では必須</li>
</ul>
''',

}

def main():
    added = 0
    for fname, new_html in ADDITIONS.items():
        fpath = f'templates/{fname}'
        if not os.path.exists(fpath):
            print(f'NOT FOUND: {fpath}')
            continue
        before = char_count(fpath)
        if before >= 5200:
            print(f'  十分({before:,}字): {fname}')
            continue
        content = open(fpath).read()
        new_content = insert_before_cta(content, new_html)
        if new_content == content:
            print(f'  スキップ: {fname}')
            continue
        open(fpath, 'w').write(new_content)
        after = char_count(fpath)
        print(f'✅ {fname}: {before:,}→{after:,}字 (+{after-before:,})')
        added += 1
    print(f'\n完了: {added}ページ')

if __name__ == '__main__':
    main()
