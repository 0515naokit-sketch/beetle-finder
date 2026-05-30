#!/usr/bin/env python3
"""
クワガタ種別飼育記事（自由研究スタイル）を一括生成する
6種 × 1ページ = 6ファイル → templates/guide_iku_*.html
"""

SPECIES = [
    {
        "slug": "kokuwagata",
        "name": "コクワガタ",
        "emoji": "🪲",
        "guide_path": "/guide/kokuwagata",
        "difficulty": "★☆☆",
        "difficulty_label": "やさしい（初めての飼育にぴったり！）",
        "adult_size": "オス 15〜55mm／メス 15〜30mm",
        "adult_life": "1〜3年（越冬可能）",
        "larva_period": "1〜1.5年",
        "season": "6〜9月",
        "habitat": "クヌギ・コナラの樹液、公園・雑木林",
        "feature": "日本全国で最も身近なクワガタ。体は小さくても飼育しやすく、幼虫からの成長が観察しやすいため自由研究に最適です。越冬もできるので翌年も生きている姿を見られます。",
        "larva_method": "発酵マット（ノコギリクワガタ用）または菌糸ビン（オオヒラタケ菌・800ml）のどちらでもOK。初心者はマットがおすすめです。",
        "temp": "18〜26℃（夏28℃以上は注意）",
        "spawn_method": "産卵木（コナラ・クヌギ等の細めの朽ち木）またはマット産み。産卵木を発酵マットに半分埋めるセットで産卵率アップ。",
        "spawn_tips": "産卵木は水に1〜2時間浸けてから表面の水分をふき取って使います。メスが産卵木に潜り込んでいれば産卵しているサインです。",
        "caution": "オスは気性がやや荒いので、同居はペアリング（交尾）のときだけにして、交尾後はオスを別居させましょう。",
        "adult_food": "昆虫ゼリー（高タンパク・フルーツ系がおすすめ）。2〜3日に1個取り替える。",
        "faq": [
            ("コクワガタは冬に死にますか？", "いいえ、越冬します。気温が下がるとマットの中に潜ってじっとしますが、死んでいるわけではありません。冬の間は霧吹きで乾燥を防ぐだけでOK。春になるとまた動き始めます。"),
            ("幼虫は朽ち木の中で見つかりました。そのまま育てられますか？", "はい、朽ち木ごと飼育ケースに入れてそのまま管理できます。ただし、成長とともにマットや菌糸ビンに移した方がより大きく育ちます。"),
            ("コクワガタは何年生きますか？", "成虫は1〜3年生きます。越冬を繰り返すので、採集した年の翌年・翌々年も生きていることがあります。"),
        ],
        "observation_points": [
            "樹液を吸っているときの口の動きを観察する",
            "昼と夜の活動の違いを記録する",
            "オスとメスの大あごの形の違いを比べる",
            "産卵木に穴が開いているか毎日観察する",
            "幼虫が食べた跡（食痕）の広がり方を記録する",
        ],
        "amazon_items": [
            ("コクワガタ飼育セット（産卵木・マット込み）", "コクワガタ 飼育セット 産卵木", "コクワガタ 飼育セット"),
            ("昆虫ゼリー（フルーツ・高タンパク）", "昆虫ゼリー クワガタ フルーツ", "昆虫ゼリー クワガタ"),
            ("菌糸ビン（オオヒラタケ・800ml）", "菌糸ビン クワガタ 800ml", "菌糸ビン クワガタ"),
        ],
        "next_slug": "nokogiri",
        "next_name": "ノコギリクワガタ",
        "prev_slug": None,
        "prev_name": None,
    },
    {
        "slug": "nokogiri",
        "name": "ノコギリクワガタ",
        "emoji": "🦌",
        "guide_path": "/guide/nokogiri",
        "difficulty": "★★☆",
        "difficulty_label": "ふつう（幼虫期間が長いが丈夫）",
        "adult_size": "オス 30〜75mm／メス 25〜40mm",
        "adult_life": "1〜2年（越冬しない場合が多い）",
        "larva_period": "約2年（長め）",
        "season": "6〜9月",
        "habitat": "クヌギ・コナラの樹液。平地〜低山地",
        "feature": "ノコギリのようなギザギザの大あごが特徴。日本各地の雑木林で見られる定番種です。幼虫期間が約2年と長く、粘り強く観察を続ける自由研究に向いています。",
        "larva_method": "発酵マット（ノコギリクワガタ用・二次発酵マット）が必須。菌糸ビンは合いません。容器は1〜2Lのボトルまたはコンテナを使用。",
        "temp": "20〜26℃（高温比較的強い）",
        "spawn_method": "マット産み（朽ち木不要）。発酵マットを固めに詰めた産卵セットにメスを入れるだけ。産卵数は多い（30〜60個）。",
        "spawn_tips": "マットはしっかり固く詰めることがポイント。メスが潜ったまま出てこなければ産卵しているサインです。1ヶ月後に割り出しを行います。",
        "caution": "成虫は越冬しない個体が多く、秋頃に寿命を迎えます。幼虫期間が2年と長いため、焦らずじっくり育てましょう。",
        "adult_food": "昆虫ゼリー（高タンパク・フルーツ系）。食欲旺盛なのでゼリーの減り具合を記録すると良い研究テーマになります。",
        "faq": [
            ("ノコギリクワガタの幼虫に菌糸ビンは使えますか？", "ノコギリクワガタの幼虫は菌糸ビンに合いません。発酵マット飼育が基本です。菌糸ビンに入れると食べずに弱ってしまうことがあります。"),
            ("幼虫期間が2年は本当ですか？", "はい、ノコギリクワガタは幼虫期間が約2年と長いクワガタです。採集した夏から数えると、翌々年の夏に成虫になります。じっくり観察する自由研究にぴったりです。"),
            ("産卵セットは何が必要ですか？", "発酵マット（10L程度）と産卵用コンテナがあれば十分です。朽ち木は必要ありません。マットを固く詰めてメスを投入するだけで産卵します。"),
        ],
        "observation_points": [
            "大あごのギザギザの形と数を記録する（オス大型・小型の違いも）",
            "マットに潜るスピードを時間で記録する",
            "昆虫ゼリーを1日でどれだけ食べるか計測する",
            "産卵マットの中に卵が何個あるか割り出して数える",
            "幼虫の体重を月1回計って成長グラフを作る",
        ],
        "amazon_items": [
            ("ノコギリクワガタ用発酵マット（10L）", "ノコギリクワガタ 発酵マット 幼虫", "ノコギリクワガタ 発酵マット"),
            ("産卵・幼虫飼育用コンテナ（2L）", "クワガタ 産卵 幼虫 ボトル 2L", "クワガタ 幼虫 飼育ボトル"),
            ("昆虫ゼリー（高タンパク）16g×50個", "昆虫ゼリー 高タンパク クワガタ", "昆虫ゼリー 高タンパク"),
        ],
        "next_slug": "miyama",
        "next_name": "ミヤマクワガタ",
        "prev_slug": "kokuwagata",
        "prev_name": "コクワガタ",
    },
    {
        "slug": "miyama",
        "name": "ミヤマクワガタ",
        "emoji": "👑",
        "guide_path": "/guide/miyama",
        "difficulty": "★★★",
        "difficulty_label": "むずかしい（温度管理が必須）",
        "adult_size": "オス 30〜78mm／メス 25〜42mm",
        "adult_life": "夏の1シーズン（越冬しない）",
        "larva_period": "2〜3年（長い）",
        "season": "6〜8月（高地・早朝が狙い目）",
        "habitat": "標高500m以上の山地。ブナ・ミズナラ林",
        "feature": "日本最大級の迫力ある大あごと、頭の両脇に耳のような突起（耳状突起）が特徴のクワガタの王様。高山の涼しい環境に生息するため、平地での飼育は温度管理が最大の難関です。",
        "larva_method": "発酵マット（二次発酵マット）必須。菌糸ビンは不向き。温度は15〜20℃を維持することが最重要。幼虫期間が長いため大型コンテナ（2L以上）を用意。",
        "temp": "15〜20℃（25℃以上は危険！）",
        "spawn_method": "マット産み。低温（15〜20℃）で飼育しているメスに産卵マットを準備。温度が適切なら自然に産卵します。",
        "spawn_tips": "産卵・飼育ともに低温管理が絶対条件。夏でも20℃以下をキープできる環境（地下室・冷蔵庫前・冷房部屋）が必要です。温度管理できない場合は幼虫のみ育てることをおすすめします。",
        "caution": "成虫は暑さに非常に弱く、気温が25℃を超えると数日で死んでしまいます。ミヤマクワガタの飼育は「冷却」が最大の課題です。小型のワインセラーがあると理想的です。",
        "adult_food": "昆虫ゼリー（フルーツ系・低温保管）。成虫は夏の1シーズンしか生きないため、元気なうちに観察・記録を急ぎましょう。",
        "faq": [
            ("ミヤマクワガタはなぜすぐ死んでしまうのですか？", "ミヤマクワガタは高山性のクワガタで、暑さにとても弱い性質があります。平地の夏の気温（30℃前後）では数日で弱ってしまいます。25℃以下、できれば20℃以下の環境が必要です。"),
            ("ミヤマクワガタの幼虫は育てられますか？", "育てられますが難しいです。発酵マットで15〜20℃を保って飼育します。幼虫は成虫より温度変化に強いので、成虫より飼育しやすいです。幼虫期間は2〜3年です。"),
            ("ミヤマクワガタの耳のようなものは何ですか？", "頭の両脇にある突起を「耳状突起（じじょうとっき）」といいます。ミヤマクワガタだけが持つ特徴で、これで他の種類と見分けられます。自由研究でスケッチするポイントのひとつです。"),
        ],
        "observation_points": [
            "頭の耳状突起の形を詳しくスケッチする",
            "温度と活動量の関係を記録する（涼しいほど元気？）",
            "体温を触って感じる変化を記録する（昆虫は変温動物）",
            "大あごの長さをノギスで正確に測って記録する",
            "同じ場所に生息するクワガタ（コクワガタ等）と体の特徴を比べる",
        ],
        "amazon_items": [
            ("ミヤマクワガタ用発酵マット（低温飼育対応）", "ミヤマクワガタ 幼虫 マット 低温", "ミヤマクワガタ 幼虫 マット"),
            ("デジタル温度計（アラーム機能付き）", "デジタル 温度計 アラーム 昆虫 飼育", "デジタル温度計 昆虫"),
            ("保冷ボックス（発泡スチロール）", "クーラーボックス 発泡スチロール 保冷", "保冷ボックス 発泡スチロール"),
        ],
        "next_slug": "hirata",
        "next_name": "ヒラタクワガタ",
        "prev_slug": "nokogiri",
        "prev_name": "ノコギリクワガタ",
    },
    {
        "slug": "hirata",
        "name": "ヒラタクワガタ",
        "emoji": "⚔️",
        "guide_path": "/guide/hirata",
        "difficulty": "★★☆",
        "difficulty_label": "ふつう（気性に注意）",
        "adult_size": "オス 35〜80mm以上（本州）／メス 25〜45mm",
        "adult_life": "2〜5年（長寿！）",
        "larva_period": "1〜1.5年",
        "season": "6〜9月",
        "habitat": "クヌギ・コナラの樹洞・樹液。低地〜山地",
        "feature": "体が平たい（ヒラタ）のが名前の由来。日本最強クラスの戦闘力を持ち、大型のオスは迫力満点。成虫は2〜5年と長生きするため、長期間観察できる自由研究テーマとして人気です。",
        "larva_method": "菌糸ビン（オオヒラタケ菌・800〜1100ml）が大型個体を狙うのに効果的。マット飼育でも育てられます。食欲旺盛で成長が早い。",
        "temp": "20〜26℃（高温に比較的強い）",
        "spawn_method": "マット産み＋産卵木の両方を使ったセットが効果的。産卵数は20〜50個。メスは産卵木の表面をかじって産卵します。",
        "spawn_tips": "オスとメスを同居させると、気性の荒いオスがメスを傷つけることがあります。交尾（ペアリング）後はすぐオスを別居させるのが鉄則です。",
        "caution": "オスは非常に気性が荒く、指に挟まれると出血することがあります。持つときは腹側を持ち、大あごには触れないようにしましょう。",
        "adult_food": "昆虫ゼリー（高タンパク・フルーツ系）。食欲があり長寿なので、何年もゼリーを食べ続ける姿を観察できます。",
        "faq": [
            ("ヒラタクワガタはなぜ体が平たいのですか？", "樹洞（木の穴）の中で生活するために体が平たく進化したと考えられています。狭い穴の中で生活しやすい形をしているのです。"),
            ("何年くらい生きますか？", "成虫は2〜5年と非常に長寿です。毎年冬は越冬し、夏になると活発になるサイクルを繰り返します。大切に育てれば小学校の間ずっと一緒にいられるかもしれません。"),
            ("大あごで挟まれると痛いですか？", "大型のオスはとても力が強く、挟まれると痛いです。血が出ることもあります。持つときは大あごを避けて腹側を持つか、虫かごの中で観察するようにしましょう。"),
        ],
        "observation_points": [
            "体の厚さを測って「平たさ」を数値で記録する",
            "大あごのはさむ力をバネばかりで測定する（理科的実験）",
            "産卵木にかじった跡を観察・スケッチする",
            "昆虫ゼリーを1週間でどれだけ食べるか記録する",
            "複数年にわたって成長・変化を観察する（長期研究）",
        ],
        "amazon_items": [
            ("菌糸ビン（オオヒラタケ菌・1100ml）", "菌糸ビン オオヒラタケ 1100ml クワガタ", "菌糸ビン オオヒラタケ 1100ml"),
            ("ヒラタクワガタ 産卵セット用マット", "ヒラタクワガタ 産卵 マット セット", "ヒラタクワガタ 産卵 マット"),
            ("産卵木（コナラ・クヌギ）Mサイズ", "産卵木 クワガタ コナラ クヌギ", "産卵木 クワガタ"),
        ],
        "next_slug": "ookuwa",
        "next_name": "オオクワガタ",
        "prev_slug": "miyama",
        "prev_name": "ミヤマクワガタ",
    },
    {
        "slug": "ookuwa",
        "name": "オオクワガタ",
        "emoji": "🏆",
        "guide_path": "/guide/ookuwa",
        "difficulty": "★★☆",
        "difficulty_label": "ふつう〜やや難（採集が最難関）",
        "adult_size": "オス 30〜85mm／メス 30〜50mm",
        "adult_life": "3〜5年（最長寿クラス！）",
        "larva_period": "1〜2年（菌糸ビン）/ 2〜3年（マット）",
        "season": "7〜8月（夜間・灯火採集）",
        "habitat": "クヌギ・コナラの樹洞。山地の雑木林（採集難易度が高い）",
        "feature": "「クワガタの王様」と呼ばれる最高峰の種。かつては幻のクワガタと言われていましたが、現在は飼育個体が流通しています。成虫は3〜5年と非常に長生きで、大切に育てれば何年も一緒にいられます。",
        "larva_method": "菌糸ビン（カワラタケ菌またはオオヒラタケ菌）飼育が基本。800ml→1100mlと段階的に大きくすると大型個体が生まれやすい。マットでも育てられますが成長に時間がかかります。",
        "temp": "20〜25℃（低めが◎）",
        "spawn_method": "産卵木産み（コナラ・クヌギの固めの朽ち木に産卵）。産卵木を発酵マットに半分埋め、メスが産卵木に潜るのを確認します。",
        "spawn_tips": "産卵木は水に3〜4時間浸けた後、陰干ししてから使います。カワラ材（カワラタケが回っている材）を使うと産卵率が大幅にアップします。",
        "caution": "採集個体を手に入れるのは非常に難しい（幻に近い）。自由研究では購入個体から始めるのが現実的です。違法採集には注意しましょう。",
        "adult_food": "昆虫ゼリー（高タンパク・フルーツ系）。長生きするので毎日ゼリーを取り替えて記録するとデータが多く集まります。",
        "faq": [
            ("オオクワガタはどこで手に入りますか？", "自然採集は非常に難しいため、ペットショップや昆虫専門店、ネット通販で飼育個体を購入するのが一般的です。初心者は飼育ペア（オス・メス）を購入して繁殖から始めるのがおすすめです。"),
            ("オオクワガタは何年生きますか？", "成虫は3〜5年、記録では6年以上生きた個体もあります。毎冬越冬して何年も生きることができます。大切に育てれば中学生になっても一緒にいられるかもしれません。"),
            ("菌糸ビンとマットはどちらがいいですか？", "大型個体を狙うなら菌糸ビン（カワラタケ菌）が断然おすすめです。マットでも育ちますが、菌糸ビンに比べて成長が遅く、サイズが小さくなりやすいです。"),
        ],
        "observation_points": [
            "体長をノギスで正確に測定し、成長記録をつける",
            "菌糸ビンの食痕の広がり方を週ごとに写真で記録する",
            "オスとメスの行動の違いを観察する",
            "産卵木に入った穴の数と位置をスケッチする",
            "羽化した日を記録し、採集（購入）からの日数を計算する",
        ],
        "amazon_items": [
            ("カワラタケ菌糸ビン（1100ml）オオクワガタ用", "カワラタケ 菌糸ビン 1100ml オオクワガタ", "カワラタケ 菌糸ビン"),
            ("オオクワガタ産卵木（カワラ材・Lサイズ）", "カワラ材 産卵木 オオクワガタ", "カワラ材 産卵木"),
            ("オオクワガタ飼育セット（産卵木・ケース込み）", "オオクワガタ 飼育セット 産卵 初心者", "オオクワガタ 飼育セット"),
        ],
        "next_slug": "akaashi",
        "next_name": "アカアシクワガタ",
        "prev_slug": "hirata",
        "prev_name": "ヒラタクワガタ",
    },
    {
        "slug": "akaashi",
        "name": "アカアシクワガタ",
        "emoji": "🦶",
        "guide_path": "/guide/akaashi",
        "difficulty": "★★☆",
        "difficulty_label": "ふつう（低温管理がポイント）",
        "adult_size": "オス 26〜58mm／メス 22〜38mm",
        "adult_life": "1〜2年（越冬可能）",
        "larva_period": "1〜1.5年",
        "season": "6〜8月（早朝・高地が狙い目）",
        "habitat": "標高500m以上の山地。ブナ・ミズナラ・シラカバ林",
        "feature": "脚の付け根が赤い（正確には赤褐色）のが名前の由来で、他のクワガタと一目で見分けられます。山地のブナ林に生息し、ミヤマクワガタと同じ環境で見られることが多いです。比較的飼育しやすい山地性クワガタです。",
        "larva_method": "菌糸ビン（オオヒラタケ菌・800ml）またはブナ・ナラ材を使った材飼育が効果的。発酵マットでも育てられます。",
        "temp": "18〜23℃（やや低温好み）",
        "spawn_method": "産卵木産み（ブナ・ミズナラなどの朽ち木を好む）。コナラ材でも産卵しますが、ブナ材の方が産卵率が高い傾向があります。",
        "spawn_tips": "産卵木はブナ材またはシラカバ材を使うと産卵しやすいです。飼育温度は20℃前後に保つと産卵が促進されます。",
        "caution": "高温（25℃以上）に弱いため、夏場の温度管理が必要です。ミヤマクワガタほどシビアではありませんが、涼しい環境を用意しましょう。",
        "adult_food": "昆虫ゼリー（フルーツ系）。活動量は他種より控えめで、食事量も少なめです。",
        "faq": [
            ("アカアシクワガタの脚はどこが赤いですか？", "脚全体ではなく、脚の付け根（転節・腿節）の部分が赤褐色になっています。胴体の黒と脚の赤が美しいコントラストで、自由研究のスケッチにおすすめのポイントです。"),
            ("コクワガタと見分けるポイントは？", "最大のポイントは脚の付け根の色です。コクワガタは脚が全体的に黒いですが、アカアシクワガタは脚の根元が赤褐色になっています。山地で採集したクワガタの脚をよく見てみましょう。"),
            ("どんな木に産卵しますか？", "ブナ・ミズナラ・シラカバなど、山地に生えている木の朽ち木を好みます。コナラ材でも産卵しますが、ブナ材が特に効果的です。"),
        ],
        "observation_points": [
            "脚の付け根の赤い部分を詳しくスケッチ・写真撮影する",
            "コクワガタと外見を比べて違いを記録する",
            "採集した標高・気温と飼育環境の温度差を記録する",
            "ブナ材とコナラ材でどちらに産卵するか実験する",
            "活動時間（昼・夜・夕方）を記録して行動パターンを調べる",
        ],
        "amazon_items": [
            ("ブナ材（産卵木・Mサイズ）アカアシ・ミヤマ向け", "産卵木 ブナ材 クワガタ アカアシ", "産卵木 ブナ材"),
            ("菌糸ビン（オオヒラタケ・800ml）", "菌糸ビン オオヒラタケ 800ml", "菌糸ビン 800ml"),
            ("クワガタ飼育ケース（コバエシャッター付き）", "クワガタ 飼育ケース コバエシャッター", "クワガタ 飼育ケース コバエ"),
        ],
        "next_slug": None,
        "next_name": None,
        "prev_slug": "ookuwa",
        "prev_name": "オオクワガタ",
    },
]

CSS = """    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:'Hiragino Sans','Meiryo',sans-serif;background:#f5f5f5;color:#333;line-height:1.95}
    a{color:#388e3c;text-decoration:none}a:hover{text-decoration:underline}
    #site-header{background:linear-gradient(135deg,#2e7d32,#43a047);padding:14px 20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
    #site-header h1{color:#fff;font-size:1rem;font-weight:700}
    .home-btn{background:rgba(255,255,255,.15);color:#fff;padding:6px 14px;border-radius:6px;font-size:.82rem;border:1px solid rgba(255,255,255,.3)}
    .home-btn:hover{background:rgba(255,255,255,.25);text-decoration:none;color:#fff}
    .container{max-width:800px;margin:0 auto;padding:24px 16px 60px}
    h1.page-title{font-size:1.6rem;color:#1b5e20;margin:20px 0 8px;line-height:1.4}
    .page-subtitle{color:#666;font-size:.9rem;margin-bottom:24px;border-bottom:2px solid #c8e6c9;padding-bottom:14px}
    .breadcrumb{font-size:.78rem;color:#888;margin-bottom:16px}.breadcrumb a{color:#388e3c}
    h2.section{font-size:1.2rem;color:#1b5e20;border-left:4px solid #43a047;padding-left:12px;margin:40px 0 12px}
    h3.sub{font-size:1rem;color:#2e7d32;margin:24px 0 8px;font-weight:700}
    p{margin-bottom:1.4em;font-size:1rem}
    ul,ol{padding-left:22px;margin-bottom:1.3em}li{margin-bottom:.6em;font-size:1rem}
    .toc{background:#fff;border:1px solid #c8e6c9;border-radius:8px;padding:18px 22px;margin:0 0 32px}
    .toc-title{font-weight:700;color:#1b5e20;margin-bottom:10px;font-size:.95rem}
    .toc ol{margin:0;padding-left:18px}.toc li{margin-bottom:4px;font-size:.88rem}
    .spec-table{width:100%;border-collapse:collapse;margin:16px 0;font-size:.9rem}
    .spec-table th{background:#2e7d32;color:#fff;padding:9px 12px;width:38%}
    .spec-table td{padding:9px 12px;border-bottom:1px solid #e0e0e0;background:#fff;vertical-align:top}
    .spec-table tr:nth-child(even) td{background:#f9f9f9}
    .diff-badge{display:inline-block;background:#e8f5e9;border:1px solid #a5d6a7;border-radius:20px;padding:4px 14px;font-weight:700;color:#1b5e20;font-size:.9rem;margin:8px 0}
    .step-box{background:#fff;border:1px solid #c8e6c9;border-radius:10px;padding:18px 22px;margin:18px 0;position:relative}
    .step-num{position:absolute;top:-14px;left:16px;background:#43a047;color:#fff;font-size:.8rem;font-weight:700;padding:3px 12px;border-radius:10px}
    .tip-box{background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:18px 22px;margin:16px 0}
    .tip-title{font-weight:700;color:#f57f17;margin-bottom:6px;font-size:.88rem}
    .warn-box{background:#fce4ec;border:1px solid #f48fb1;border-radius:8px;padding:18px 22px;margin:16px 0}
    .warn-title{font-weight:700;color:#c62828;margin-bottom:6px;font-size:.88rem}
    .info-box{background:#e3f2fd;border:1px solid #90caf9;border-radius:8px;padding:18px 22px;margin:16px 0}
    .info-title{font-weight:700;color:#1565c0;margin-bottom:6px;font-size:.88rem}
    .good-box{background:#e8f5e9;border:1px solid #a5d6a7;border-radius:8px;padding:18px 22px;margin:16px 0}
    .good-title{font-weight:700;color:#2e7d32;margin-bottom:6px;font-size:.88rem}
    .obs-list{list-style:none;padding:0;margin:14px 0}
    .obs-list li{display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid #e8f5e9;font-size:.92rem}
    .obs-list li::before{content:"📝";flex-shrink:0}
    .sheet-wrap{background:#fff;border:2px solid #43a047;border-radius:12px;padding:20px;margin:20px 0}
    .sheet-title{font-size:1.1rem;font-weight:700;color:#1b5e20;text-align:center;margin-bottom:16px;border-bottom:2px dashed #c8e6c9;padding-bottom:10px}
    .sheet-row{display:grid;grid-template-columns:120px 1fr;border-bottom:1px solid #e8f5e9}
    .sheet-label{font-size:.82rem;color:#555;padding:9px 8px;background:#f1f8e9;font-weight:600}
    .sheet-val{padding:9px 8px;font-size:.82rem;color:#aaa;font-style:italic}
    .print-btn{display:block;background:#43a047;color:#fff;border:none;padding:10px 24px;border-radius:8px;font-size:.88rem;font-weight:700;cursor:pointer;margin:14px auto 0;text-align:center;width:fit-content;text-decoration:none}
    .print-btn:hover{background:#388e3c;color:#fff}
    .faq-q{background:#e8f5e9;border-left:4px solid #43a047;padding:12px 16px;font-weight:700;font-size:.95rem;color:#1b5e20;border-radius:0 6px 0 0;margin-top:14px}
    .faq-a{background:#fff;border:1px solid #c8e6c9;border-top:none;border-radius:0 0 6px 6px;padding:14px 18px;font-size:.92rem;line-height:1.85;margin-bottom:8px}
    .nav-pager{display:flex;justify-content:space-between;gap:12px;margin:32px 0}
    .pager-btn{flex:1;background:#fff;border:1px solid #c8e6c9;border-radius:8px;padding:12px 16px;font-size:.85rem;color:#2e7d32;font-weight:700}
    .pager-btn:hover{background:#e8f5e9;text-decoration:none;color:#1b5e20}
    .pager-btn.right{text-align:right}
    .species-nav{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px;margin:16px 0}
    .sn-card{background:#fff;border:1px solid #c8e6c9;border-radius:8px;padding:10px;text-align:center;font-size:.82rem}
    .sn-card a{font-weight:700;color:#1b5e20}
    .sn-card.active{background:#e8f5e9;border-color:#43a047}
    .rec-box{background:#fffbf0;border:2px solid #f0c040;border-radius:10px;padding:14px 16px;margin:22px 0}
    .rec-title{font-weight:700;color:#c45000;font-size:.9rem;margin-bottom:10px}
    .rec-item{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:9px 0;border-bottom:1px solid #f5e7a0;flex-wrap:wrap}
    .rec-item:last-child{border-bottom:none}
    .rec-info{display:flex;align-items:center;gap:8px;flex:1}
    .rec-icon{font-size:1.3rem;flex-shrink:0}
    .rec-name{font-weight:700;font-size:.86rem;color:#333}
    .rec-sub{font-size:.74rem;color:#777}
    .rec-links{display:flex;gap:5px;flex-shrink:0}
    .rec-amz{background:#ff9900;color:#fff!important;padding:5px 10px;border-radius:5px;font-size:.75rem;font-weight:700;text-decoration:none!important;white-space:nowrap}
    .rec-rkt{background:#bf0000;color:#fff!important;padding:5px 10px;border-radius:5px;font-size:.75rem;font-weight:700;text-decoration:none!important;white-space:nowrap}
    .rec-note{font-size:.68rem;color:#aaa;margin:8px 0 0;text-align:right}
    .cta-box{background:linear-gradient(135deg,#1b2d1b,#2e4e2e);color:#a5d6a7;border-radius:10px;padding:22px;text-align:center;margin:40px 0}
    .cta-box h2{font-size:1.1rem;margin-bottom:8px;color:#fff}
    .cta-box p{font-size:.85rem;color:#81c784;margin-bottom:16px}
    .cta-btn{display:inline-block;background:#43a047;color:#fff;padding:12px 28px;border-radius:8px;font-weight:700;font-size:.92rem}
    .cta-btn:hover{background:#388e3c;text-decoration:none;color:#fff}
    .share-box{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:28px 0;padding:14px 18px;background:#f9f9f9;border-radius:10px;border:1px solid #e0e0e0}
    .share-label{font-size:.82rem;font-weight:700;color:#555}
    .share-x{background:#000;color:#fff!important;padding:7px 16px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none!important}
    .share-x:hover{background:#333!important}
    .share-hb{background:#00a4de;color:#fff!important;padding:7px 16px;border-radius:6px;font-size:.82rem;font-weight:700;text-decoration:none!important}
    .share-hb:hover{background:#0083b3!important}
    footer{background:#1b2d1b;color:#81c784;padding:28px 16px 16px;font-size:.78rem;margin-top:40px}
    .footer-nav{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:20px;max-width:800px;margin:0 auto 20px;padding:0 0 20px;border-bottom:1px solid #2e4e2e}
    .footer-nav-group{display:flex;flex-direction:column;gap:6px}
    .footer-nav-label{color:#a5d6a7;font-weight:700;font-size:.8rem;margin-bottom:2px}
    .footer-nav a{color:#81c784;text-decoration:none;font-size:.78rem;line-height:1.6}
    .footer-nav a:hover{color:#fff;text-decoration:underline}
    .footer-bottom{text-align:center;color:#4a7a4a}
    .footer-bottom a{color:#81c784}"""

FOOTER_NAV = """<footer>
  <nav class="footer-nav">
    <div class="footer-nav-group">
      <span class="footer-nav-label">🪲 種別飼育ガイド</span>
      <a href="/guide/iku/kokuwagata">コクワガタの飼育</a>
      <a href="/guide/iku/nokogiri">ノコギリクワガタ</a>
      <a href="/guide/iku/miyama">ミヤマクワガタ</a>
      <a href="/guide/iku/hirata">ヒラタクワガタ</a>
      <a href="/guide/iku/ookuwa">オオクワガタ</a>
      <a href="/guide/iku/akaashi">アカアシクワガタ</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">🐛 幼虫・飼育</span>
      <a href="/guide/larva">幼虫の育て方</a>
      <a href="/guide/breeding">飼育の基本</a>
      <a href="/guide/aftercare">採集後の管理</a>
      <a href="/guide/jiyukenkyu">自由研究ガイド</a>
      <a href="/guide/jiyukenkyu-kabuto">カブトムシ自由研究</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">📖 採集テクニック</span>
      <a href="/guide/night">夜間採集のコツ</a>
      <a href="/guide/morning">早朝採集のコツ</a>
      <a href="/guide/trap">トラップ採集</a>
      <a href="/guide/tree">樹液の出る木</a>
      <a href="/guide/tools">採集道具リスト</a>
      <a href="/guide/beginners">初心者向けガイド</a>
    </div>
    <div class="footer-nav-group">
      <span class="footer-nav-label">🗾 都道府県ガイド</span>
      <a href="/guide/pref/tokyo">東京都</a>
      <a href="/guide/pref/kanagawa">神奈川県</a>
      <a href="/guide/pref/osaka">大阪府</a>
      <a href="/guide/pref/aichi">愛知県</a>
      <a href="/guide/pref/hokkaido">北海道</a>
      <a href="/guide/pref">全都道府県一覧</a>
    </div>
  </nav>
  <div class="footer-bottom">
    <p style="margin:0 0 6px;font-size:.76rem;color:#5a8a5a">
      ✍️ 監修・執筆：<a href="/about" style="color:#81c784">森山春樹</a>（クワガタ採集歴20年以上 ／ 全国47都道府県フィールド経験）
    </p>
    <a href="/">クワガタ採集スポット検索 beetle-finder</a> ｜
    <a href="/app">🗺 スポット検索</a> ｜
    <a href="/guide">📖 ガイド一覧</a> ｜
    <a href="/about">サービスについて</a> ｜
    <a href="/privacy">プライバシーポリシー</a> ｜
    <a href="/terms">利用規約</a>
  </div>
</footer>"""

SEASON_JS = """<script>
(function(){
  var m=new Date().getMonth()+1;
  var map={5:['6月の採集準備を今から！コクワガタが動き出す季節','/guide/june','6月の採集ガイドを読む'],
           6:['クワガタシーズン開幕！6月の採集ガイド','/guide/june','今すぐ読む →'],
           7:['🔥 採集最盛期！7月は全種が揃うベストシーズン','/guide/july','7月ガイドを読む'],
           8:['カブトムシのピーク！8月の採集攻略法','/guide/august','8月ガイドを読む'],
           9:['9月もまだ間に合う！秋の採集ガイド','/guide/september','9月ガイドを読む'],
           10:['10月の採集はコクワが主役。シーズン終盤戦','/guide/october','10月ガイドを読む']};
  if(!map[m])return;
  var d=document.createElement('div');
  d.innerHTML='<div style="background:linear-gradient(135deg,#1b5e20,#2e7d32);color:#fff;padding:12px 18px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:.85rem;border-bottom:3px solid #4caf50"><span>📅 '+map[m][0]+'</span><a href="'+map[m][1]+'" style="background:#fff;color:#1b5e20;font-weight:700;padding:6px 14px;border-radius:20px;text-decoration:none;white-space:nowrap;font-size:.8rem">'+map[m][2]+'</a></div>';
  var header=document.getElementById('site-header');
  if(header&&header.nextSibling){header.parentNode.insertBefore(d.firstChild,header.nextSibling);}
  else{document.body.insertBefore(d.firstChild,document.body.firstChild);}
})();
</script>"""

ALL_SPECIES_NAV = [
    ("kokuwagata","コクワガタ","🪲"),
    ("nokogiri","ノコギリ","🦌"),
    ("miyama","ミヤマ","👑"),
    ("hirata","ヒラタ","⚔️"),
    ("ookuwa","オオクワ","🏆"),
    ("akaashi","アカアシ","🦶"),
]

def make_html(sp):
    slug = sp["slug"]
    name = sp["name"]
    emoji = sp["emoji"]

    # 種ナビ
    sn_items = ""
    for sslug, sname, semoji in ALL_SPECIES_NAV:
        active = ' active' if sslug == slug else ''
        sn_items += f'<div class="sn-card{active}"><a href="/guide/iku/{sslug}">{semoji} {sname}</a></div>\n    '

    # ページャー
    pager_prev = ""
    pager_next = ""
    if sp["prev_slug"]:
        pager_prev = f'<a href="/guide/iku/{sp["prev_slug"]}" class="pager-btn">← {sp["prev_name"]}の飼育</a>'
    else:
        pager_prev = '<span></span>'
    if sp["next_slug"]:
        pager_next = f'<a href="/guide/iku/{sp["next_slug"]}" class="pager-btn right">{sp["next_name"]}の飼育 →</a>'
    else:
        pager_next = '<span></span>'

    # FAQ
    faq_html = ""
    faq_schema = []
    for q, a in sp["faq"]:
        faq_html += f'<div class="faq-q">Q. {q}</div>\n    <div class="faq-a">A. {a}</div>\n    '
        faq_schema.append({"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}})

    import json
    faq_schema_str = json.dumps(faq_schema, ensure_ascii=False, indent=2)

    # Amazonリンク
    rec_html = ""
    for item_name, amz_q, rkt_q in sp["amazon_items"]:
        amz_url = f"https://www.amazon.co.jp/s?k={amz_q.replace(' ','+')}&tag=beetlefinder-22"
        rkt_url = f"https://search.rakuten.co.jp/search/mall/{rkt_q.replace(' ','+')}/"
        rec_html += f"""    <div class="rec-item">
      <div class="rec-info">
        <div class="rec-icon">🛒</div>
        <div>
          <p class="rec-name">{item_name}</p>
        </div>
      </div>
      <div class="rec-links">
        <a href="{amz_url}" class="rec-amz" target="_blank" rel="noopener">Amazon</a>
        <a href="{rkt_url}" class="rec-rkt" target="_blank" rel="noopener">楽天</a>
      </div>
    </div>
"""

    # 観察ポイント
    obs_html = "\n".join(f"      <li>{p}</li>" for p in sp["observation_points"])

    page_title = f"{name}の飼育方法と自由研究ガイド2026年版｜幼虫から成虫まで完全解説"
    page_desc = f"{name}の飼育方法を初心者向けに解説。飼育難易度・産卵セット・幼虫の育て方・温度管理・観察ポイントまで。夏休みの自由研究にも最適。著者：森山春樹（採集歴20年以上）"

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-D50YSSYFKN"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-D50YSSYFKN');</script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{page_title}</title>
  <meta name="description" content="{page_desc}">
  <meta name="keywords" content="{name} 飼育 幼虫 育て方 産卵 自由研究 小学生">
  <meta property="og:title" content="{page_title}">
  <meta property="og:description" content="{page_desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="https://beetle-finder.onrender.com/guide/iku/{slug}">
  <meta property="og:image" content="https://beetle-finder.onrender.com/static/ogp.png">
  <meta property="og:site_name" content="クワガタ採集スポット検索">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{page_title}">
  <meta name="twitter:description" content="{page_desc}">
  <meta name="twitter:image" content="https://beetle-finder.onrender.com/static/ogp.png">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9675243685208925" crossorigin="anonymous"></script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{page_title}",
    "description": "{page_desc}",
    "url": "https://beetle-finder.onrender.com/guide/iku/{slug}",
    "datePublished": "2026-05-30",
    "dateModified": "2026-05-30",
    "author": {{
      "@type": "Person",
      "name": "森山春樹",
      "url": "https://beetle-finder.onrender.com/about"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "beetle-finder",
      "url": "https://beetle-finder.onrender.com",
      "logo": {{
        "@type": "ImageObject",
        "url": "https://beetle-finder.onrender.com/static/img/icon-kuwagata.jpg"
      }}
    }},
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "https://beetle-finder.onrender.com/guide/iku/{slug}"
    }}
  }}
  </script>
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": {faq_schema_str}
  }}
  </script>
  <style>
{CSS}
  </style>
</head>
<body>
<header id="site-header">
  <a href="/" style="text-decoration:none"><h1>🪲 クワガタ採集スポット検索</h1></a>
  <a href="/guide" class="home-btn">📖 採集ガイド一覧</a>
  <a href="/app" class="home-btn">🗺️ スポット検索</a>
</header>
<div class="container">
  <div class="breadcrumb"><a href="/">ホーム</a> › <a href="/guide">採集ガイド</a> › <a href="/guide/iku/kokuwagata">種別飼育ガイド</a> › {name}</div>
  <h1 class="page-title">{emoji} {name}の飼育方法【2026年版】</h1>
  <p class="page-subtitle">幼虫から成虫まで・産卵セット・観察シート付き ／ 著者：森山春樹（採集歴20年以上）</p>

  <!-- 種ナビゲーション -->
  <div class="species-nav">
    {sn_items}
  </div>

  <div class="toc">
    <div class="toc-title">📋 目次</div>
    <ol>
      <li><a href="#spec">{name}の基本データ</a></li>
      <li><a href="#feature">特徴と採集場所</a></li>
      <li><a href="#setup">成虫飼育セットの作り方</a></li>
      <li><a href="#spawn">産卵セットの作り方</a></li>
      <li><a href="#larva">幼虫の育て方</a></li>
      <li><a href="#obs">自由研究の観察ポイント</a></li>
      <li><a href="#sheet">観察シート（印刷用）</a></li>
      <li><a href="#goods">おすすめ飼育グッズ</a></li>
      <li><a href="#faq">よくある質問</a></li>
    </ol>
  </div>

  <!-- 1. 基本データ -->
  <h2 class="section" id="spec">① {name}の基本データ</h2>
  <div class="diff-badge">飼育難易度：{sp["difficulty"]} {sp["difficulty_label"]}</div>
  <table class="spec-table">
    <tr><th>体長</th><td>{sp["adult_size"]}</td></tr>
    <tr><th>成虫寿命</th><td>{sp["adult_life"]}</td></tr>
    <tr><th>幼虫期間</th><td>{sp["larva_period"]}</td></tr>
    <tr><th>採集シーズン</th><td>{sp["season"]}</td></tr>
    <tr><th>生息場所</th><td>{sp["habitat"]}</td></tr>
    <tr><th>適温（飼育）</th><td>{sp["temp"]}</td></tr>
    <tr><th>幼虫の餌</th><td>{sp["larva_method"]}</td></tr>
  </table>

  <!-- 2. 特徴 -->
  <h2 class="section" id="feature">② 特徴と採集場所</h2>
  <p>{sp["feature"]}</p>
  <p><a href="{sp["guide_path"]}">→ {name}の採集ガイド（採集場所・時期・方法の詳細）</a></p>

  <!-- AdSense -->
  <ins class="adsbygoogle" style="display:block;text-align:center" data-ad-layout="in-article" data-ad-format="fluid" data-ad-client="ca-pub-9675243685208925" data-ad-slot="auto"></ins>
  <script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>

  <!-- 3. 成虫飼育セット -->
  <h2 class="section" id="setup">③ 成虫飼育セットの作り方</h2>

  <div class="step-box">
    <div class="step-num">STEP 1</div>
    <h3 class="sub" style="margin-top:8px">飼育ケースを選ぶ</h3>
    <p>体の大きさに合ったケースを選びます。{name}のオスには<strong>中〜大サイズのケース</strong>が適切です。コバエが入らない「コバエシャッター」タイプがおすすめです。</p>
  </div>

  <div class="step-box">
    <div class="step-num">STEP 2</div>
    <h3 class="sub" style="margin-top:8px">マットを敷く</h3>
    <p>飼育マット（発酵マットまたは昆虫マット）をケースの3分の1程度敷きます。{name}はマットに潜って休む習性があるため、深さを確保してあげましょう。</p>
  </div>

  <div class="step-box">
    <div class="step-num">STEP 3</div>
    <h3 class="sub" style="margin-top:8px">止まり木・隠れ場所を置く</h3>
    <p>転倒防止用の止まり木と、ゼリーを差し込む穴が開いたエサ台を置きます。複数のクワガタを入れる場合は隠れ場所を増やして縄張り争いを減らします。</p>
  </div>

  <div class="step-box">
    <div class="step-num">STEP 4</div>
    <h3 class="sub" style="margin-top:8px">昆虫ゼリーをセット</h3>
    <p>{sp["adult_food"]} ゼリーは転倒防止用のエサ台に差し込みます。夏場は傷みやすいので2〜3日に1回交換してください。</p>
  </div>

  <div class="warn-box">
    <div class="warn-title">⚠️ 注意</div>
    <p style="margin-bottom:0">{sp["caution"]}</p>
  </div>

  <!-- 4. 産卵セット -->
  <h2 class="section" id="spawn">④ 産卵セットの作り方</h2>
  <p>{sp["spawn_method"]}</p>

  <div class="step-box">
    <div class="step-num">STEP 1</div>
    <h3 class="sub" style="margin-top:8px">産卵材・マットを準備する</h3>
    <p>産卵セット用の大きめのケース（600〜1000mlのコンテナや飼育ケース）に発酵マットをしっかり詰めます。表面を軽く均します。</p>
  </div>

  <div class="step-box">
    <div class="step-num">STEP 2</div>
    <h3 class="sub" style="margin-top:8px">メスを投入する</h3>
    <p>交尾済みのメスを産卵セットに入れます。1〜2週間でメスが潜り込み始めたら産卵しているサインです。産卵中はなるべくケースを動かさないようにしましょう。</p>
  </div>

  <div class="step-box">
    <div class="step-num">STEP 3</div>
    <h3 class="sub" style="margin-top:8px">1〜2ヶ月後に割り出す</h3>
    <p>産卵から1〜2ヶ月後にマット・産卵木を慎重にほぐして卵・幼虫を取り出します（割り出し）。スプーンやピンセットで丁寧に探しましょう。</p>
  </div>

  <div class="tip-box">
    <div class="tip-title">💡 産卵のコツ</div>
    <p style="margin-bottom:0">{sp["spawn_tips"]}</p>
  </div>

  <!-- AdSense -->
  <ins class="adsbygoogle" style="display:block;text-align:center" data-ad-layout="in-article" data-ad-format="fluid" data-ad-client="ca-pub-9675243685208925" data-ad-slot="auto"></ins>
  <script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>

  <!-- 5. 幼虫の育て方 -->
  <h2 class="section" id="larva">⑤ 幼虫の育て方</h2>
  <p>{sp["larva_method"]}</p>
  <p>詳しい幼虫の育て方は <a href="/guide/larva">→ クワガタ幼虫の育て方完全ガイド</a> も参考にしてください。</p>

  <div class="info-box">
    <div class="info-title">ℹ️ 温度管理の目安</div>
    <p style="margin-bottom:0"><strong>適温：{sp["temp"]}</strong><br>温度が適温からずれると幼虫の成長が遅くなったり、最悪死んでしまうことがあります。夏の高温に特に注意しましょう。デジタル温度計で飼育場所の温度を毎日記録するのが理想です。</p>
  </div>

  <!-- 6. 観察ポイント -->
  <h2 class="section" id="obs">⑥ 自由研究の観察ポイント</h2>
  <p>夏休みの自由研究で{name}を選んだ場合、次のポイントを観察・記録すると充実したレポートができます。</p>
  <ul class="obs-list">
{obs_html}
  </ul>

  <div class="good-box">
    <div class="good-title">✅ 自由研究のまとめ方のヒント</div>
    <ul style="margin-bottom:0;padding-left:20px">
      <li>観察した内容を<strong>毎日同じ時間に記録</strong>する（習慣化）</li>
      <li>写真や手書きのスケッチを記録に加える</li>
      <li>「なぜそうなるのか？」という<strong>考察</strong>を加えると高評価</li>
      <li>温度・天気・活動量の関係をグラフにまとめる</li>
      <li>飼育前の「仮説」と、観察後の「結果」を比べる</li>
    </ul>
  </div>

  <!-- 7. 観察シート -->
  <h2 class="section" id="sheet">⑦ 観察シート（印刷して使おう）</h2>
  <div class="sheet-wrap">
    <div class="sheet-title">🔬 {name} 飼育観察シート</div>
    <div class="sheet-row"><div class="sheet-label">観察日</div><div class="sheet-val">　　　年　　月　　日（　　曜日）</div></div>
    <div class="sheet-row"><div class="sheet-label">気温・室温</div><div class="sheet-val">　　　℃</div></div>
    <div class="sheet-row"><div class="sheet-label">活動の様子</div><div class="sheet-val">活発・ふつう・おとなしい</div></div>
    <div class="sheet-row"><div class="sheet-label">ゼリーの減り</div><div class="sheet-val">たくさん食べた・少し食べた・食べなかった</div></div>
    <div class="sheet-row"><div class="sheet-label">いた場所</div><div class="sheet-val">マットの上・止まり木・マットの中・ゼリーの近く</div></div>
    <div class="sheet-row"><div class="sheet-label">特別な行動</div><div class="sheet-val">ケンカ・交尾・産卵行動・その他（　　　　　　）</div></div>
    <div class="sheet-row"><div class="sheet-label">スケッチ</div><div class="sheet-val" style="height:100px">（体の特徴をえがこう）</div></div>
    <div class="sheet-row"><div class="sheet-label">気づいたこと</div><div class="sheet-val" style="height:80px"></div></div>
  </div>
  <a href="javascript:window.print()" class="print-btn">🖨️ この観察シートを印刷する</a>

  <!-- 8. おすすめグッズ -->
  <h2 class="section" id="goods">⑧ おすすめ飼育グッズ</h2>
  <div class="rec-box">
    <div class="rec-title">🛒 {name}の飼育におすすめ</div>
{rec_html}
    <div class="rec-note">※ Amazonリンクはアソシエイトリンクです。価格は変動することがあります。</div>
  </div>

  <!-- 9. FAQ -->
  <h2 class="section" id="faq">❓ よくある質問</h2>
  {faq_html}

  <!-- ページャー -->
  <div class="nav-pager">
    {pager_prev}
    {pager_next}
  </div>

  <!-- CTA -->
  <div class="cta-box">
    <h2>🗺️ {name}の採集スポットを探す</h2>
    <p>beetle-finderで全国の採集スポットを検索できます。{name}が採れる場所を地図で確認しよう！</p>
    <a href="/app" class="cta-btn">採集スポットを検索する</a>
  </div>

  <!-- シェア -->
  <div class="share-box">
    <span class="share-label">📢 この記事をシェア</span>
    <div class="share-links">
      <a href="https://twitter.com/intent/tweet?text={name}の飼育ガイド2026&url=https://beetle-finder.onrender.com/guide/iku/{slug}&hashtags=クワガタ,{name},自由研究" target="_blank" rel="noopener" class="share-x">𝕏 ポスト</a>
      <a href="https://b.hatena.ne.jp/add?mode=confirm&url=https://beetle-finder.onrender.com/guide/iku/{slug}&title={name}の飼育ガイド2026" target="_blank" rel="noopener" class="share-hb">B! はてブ</a>
    </div>
  </div>
</div>

{FOOTER_NAV}

{SEASON_JS}
</body>
</html>"""
    return html


import os

os.makedirs("templates", exist_ok=True)

for sp in SPECIES:
    html = make_html(sp)
    path = f"templates/guide_iku_{sp['slug']}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ {path}")

print(f"\n完了: {len(SPECIES)} ファイル生成")
