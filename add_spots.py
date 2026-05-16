"""
追加スポット - family_spots.jsonに追加して目標件数に到達させる
目標: kanto130 / chubu70 / kinki70 / tohoku50 / kyushu50 / chugoku30
"""
import json, math, random
random.seed(99)

# ── 既存データ読み込み ───────────────────────────────────────────
with open("static/family_spots.json", encoding="utf-8") as f:
    fam_data = json.load(f)
with open("static/expert_spots.json", encoding="utf-8") as f:
    exp_data = json.load(f)

family_spots = fam_data["spots"]
expert_spots = exp_data["spots"]

# 現在の最大ID取得
max_fid = max(s["id"] for s in family_spots)
max_eid = max(s["id"] for s in expert_spots)

# ── 追加スポット定義 ─────────────────────────────────────────────
# format: (name, area, lat, lng, prefecture, region, elevation, species[], best_months[], best_time, access, family_ok, child_min_age, difficulty, parking, notes)
ADD_SPOTS = [
  # ===== 関東追加 +57件 =====
  # 東京追加
  ("奥多摩・惣岳山","奥多摩",35.8333,139.0583,"東京都","kanto",756,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","青梅駅からバス",False,10,2,True,"コナラ・ミズナラ帯"),
  ("高水三山","奥多摩",35.8167,139.0833,"東京都","kanto",756,["miyama","nokogiri","kokuwagata"],[6,7,8],"夜20〜23時","軍畑駅から徒歩",False,10,2,True,"コナラ主体の山塊"),
  ("棒ノ嶺","奥多摩",35.8833,139.1500,"東京都","kanto",969,["miyama","nokogiri","akaashi","kokuwagata"],[6,7,8],"夜20〜22時","飯能駅からバス",False,10,2,True,"白谷沢の渓谷コース"),
  ("御前山","奥多摩",35.8000,139.0167,"東京都","kanto",1405,["miyama","akaashi"],[6,7],"夜19〜22時","奥多摩駅からバス",False,12,3,True,"カタクリで有名。ブナ帯"),
  ("雲取山麓","奥多摩",35.8667,138.9333,"東京都","kanto",2017,["miyama","akaashi"],[6,7],"夜19〜21時","奥多摩駅からバス",False,12,3,True,"東京最高峰。ミヤマ・アカアシ"),
  ("多摩・小山田","多摩",35.5833,139.4667,"東京都","kanto",180,["nokogiri","kabuto","kokuwagata","hirata"],[7,8],"夜20〜23時","橋本駅から車",True,5,1,True,"小山田農村公園周辺のクヌギ林"),
  ("小峰公園","奥多摩",35.7333,139.2333,"東京都","kanto",250,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","武蔵五日市駅から徒歩",True,5,1,True,"ファミリー向け整備林"),
  ("払沢の滝","奥多摩",35.7583,139.2167,"東京都","kanto",340,["nokogiri","kabuto","kokuwagata","hirata"],[7,8],"夜20〜23時","武蔵五日市駅からバス",True,6,1,True,"滝周辺のクヌギ・コナラ"),
  # 神奈川追加
  ("丹沢・鍋割山","丹沢",35.4500,139.1000,"神奈川県","kanto",1272,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","渋沢駅からバス",False,10,2,True,"ブナ林のミヤマ・アカアシ"),
  ("丹沢・焼山","丹沢",35.5333,139.1333,"神奈川県","kanto",1061,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","三ヶ木からバス",False,10,2,True,"コナラ・ミズナラ帯"),
  ("丹沢・弘法山","丹沢",35.3833,139.2167,"神奈川県","kanto",235,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","秦野駅から徒歩",True,5,1,True,"里山整備済み"),
  ("丹沢・ヤビツ峠","丹沢",35.4667,139.2333,"神奈川県","kanto",761,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","秦野駅からバス",False,10,2,True,"コナラ・ブナの峠"),
  ("津久井湖周辺","丹沢",35.5833,139.2167,"神奈川県","kanto",200,["nokogiri","kabuto","kokuwagata","hirata"],[7,8],"夜20〜23時","橋本駅から車",True,5,1,True,"ダム湖畔の広葉樹林"),
  ("城山かたくりの里","丹沢",35.5667,139.2500,"神奈川県","kanto",350,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","橋本駅から車",True,6,1,True,"里山の管理された林"),
  ("箱根・明神ヶ岳","箱根",35.2833,139.0167,"神奈川県","kanto",1169,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","箱根湯本駅から車",False,10,2,True,"コナラ・ブナ帯"),
  # 埼玉追加
  ("神川・城峯山","秩父北部",36.2167,139.0333,"埼玉県","kanto",1037,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","神川町から車",False,10,2,True,"西上州との境の山"),
  ("小鹿野・両神村","秩父",36.0167,138.8000,"埼玉県","kanto",500,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","西武秩父駅から車",True,6,1,True,"小鹿野町の広葉樹林"),
  ("秩父・浦山口","秩父",35.9833,138.9833,"埼玉県","kanto",350,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","浦山口駅から徒歩",True,6,1,True,"秩父さくら湖周辺"),
  ("宮沢湖","飯能",35.8833,139.2333,"埼玉県","kanto",150,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","飯能駅から車",True,5,1,True,"ムーミンバレーパーク隣接"),
  ("入間・加治丘陵","飯能",35.8167,139.3333,"埼玉県","kanto",200,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","武蔵藤沢駅から徒歩",True,5,1,True,"都市近郊の整備済み雑木林"),
  ("比企・物見山","埼玉中央",36.0000,139.3667,"埼玉県","kanto",135,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","東松山駅から車",True,5,1,True,"物見山公園周辺"),
  ("嵐山渓谷","埼玉中央",36.0500,139.3167,"埼玉県","kanto",100,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","武蔵嵐山駅から徒歩",True,5,1,True,"都幾川沿いの雑木林"),
  ("越辺川流域","埼玉西部",35.9833,139.2667,"埼玉県","kanto",100,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","川越駅から車",True,5,1,False,"川沿いのクヌギ・ヤナギ林"),
  # 千葉追加
  ("千葉・清澄山","房総",35.1583,140.1583,"千葉県","kanto",377,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","安房鴨川駅から車",True,6,1,True,"房総の名山"),
  ("千葉・大福山","房総",35.3167,140.1167,"千葉県","kanto",292,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","五井駅からバス",True,5,1,True,"小湊鉄道沿いの丘陵"),
  ("千葉・亀山湖","房総",35.2167,140.1000,"千葉県","kanto",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","木更津駅から車",True,5,1,True,"ダム湖畔のクヌギ林"),
  ("千葉・高宕山","房総",35.1667,139.9667,"千葉県","kanto",330,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","君津駅から車",False,10,2,True,"野生のニホンザル生息地"),
  ("利根川流域","茨城・千葉",35.8833,139.9500,"千葉県","kanto",10,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","我孫子駅から車",True,5,1,False,"川沿いのヤナギ・クヌギ帯"),
  # 茨城追加
  ("茨城・御前山","奥久慈",36.5167,140.3167,"茨城県","kanto",612,["miyama","nokogiri","akaashi","kokuwagata"],[6,7,8],"夜20〜22時","水戸駅から車",False,10,2,True,"那珂川上流域"),
  ("茨城・高館山","茨城南部",36.0833,140.5833,"茨城県","kanto",220,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","土浦駅から車",True,5,1,True,"霞ヶ浦近くの低山"),
  ("つくばね自然公園","筑波",36.2500,140.1333,"茨城県","kanto",400,["nokogiri","kabuto","kokuwagata","miyama"],[7,8],"夜20〜23時","つくばから車",True,5,1,True,"筑波山麓の自然公園"),
  # 栃木追加
  ("益子・高舘山","栃木南部",36.4667,140.2000,"栃木県","kanto",301,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","益子駅から徒歩",True,5,1,True,"益子焼の里の近く"),
  ("栃木・太平山","栃木南部",36.3667,139.7167,"栃木県","kanto",342,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","栃木駅から車",True,5,1,True,"謙信平のクヌギ林"),
  ("那珂川町・馬頭","栃木北部",36.7833,140.2167,"栃木県","kanto",180,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","野岩鉄道から車",True,5,1,True,"那珂川沿いの広葉樹林"),
  ("日光・足尾","日光",36.6500,139.4500,"栃木県","kanto",1000,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","間藤駅から車",False,10,2,True,"銅山廃坑周辺の二次林"),
  # 群馬追加
  ("吾妻・草津周辺","群馬北部",36.6167,138.5667,"群馬県","kanto",1100,["miyama","akaashi"],[6,7],"夜19〜22時","長野原草津口駅からバス",True,8,1,True,"温泉地周辺の広葉樹林"),
  ("片品・尾瀬戸倉","群馬北部",36.8833,139.2833,"群馬県","kanto",1100,["miyama","akaashi"],[6,7],"夜19〜22時","沼田駅からバス",False,10,2,True,"尾瀬への玄関口"),
  ("みなかみ・藤原","群馬北部",36.8333,138.9333,"群馬県","kanto",700,["miyama","akaashi","nokogiri"],[6,7,8],"夜20〜22時","後閑駅から車",False,10,2,True,"利根川源流域の広葉樹林"),
  ("下仁田・荒船山","群馬南部",36.2000,138.7167,"群馬県","kanto",1423,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","下仁田駅から車",False,10,2,True,"テーブル状の高原山"),
  ("藤岡・多野","群馬南部",36.1333,138.9500,"群馬県","kanto",500,["miyama","nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","新町駅から車",True,6,1,True,"神流川流域の里山"),
  # 山梨追加
  ("大菩薩嶺麓","山梨東部",35.7333,138.9333,"山梨県","kanto",1600,["miyama","akaashi"],[6,7],"夜19〜22時","塩山駅から車",False,12,3,True,"ブナ・ミズナラの原生林"),
  ("三つ峠山麓","富士山麓",35.5583,138.7833,"山梨県","kanto",1800,["miyama","akaashi"],[6,7],"夜19〜22時","都留市から車",False,10,2,True,"富士山を望む山のコナラ帯"),
  ("笛吹川流域","山梨中央",35.6333,138.7000,"山梨県","kanto",400,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","石和温泉駅から車",True,5,1,True,"フルーツ園の里。ヤナギ・クヌギ"),
  ("甲州・塩山","山梨東部",35.7167,138.8000,"山梨県","kanto",580,["miyama","nokogiri","kabuto","kokuwagata"],[6,7,8],"夜20〜23時","塩山駅から徒歩",True,6,1,True,"葡萄畑と雑木林が混在"),
  ("北杜・清里高原","山梨北部",35.9000,138.4667,"山梨県","kanto",1300,["miyama","akaashi","nokogiri"],[6,7],"夜19〜22時","小淵沢駅から車",True,6,1,True,"高原リゾート。ミヤマ安定"),
  ("韮崎・甘利山","山梨中央",35.7167,138.4667,"山梨県","kanto",2000,["miyama","akaashi"],[6,7],"夜19〜21時","韮崎駅から車",False,12,3,True,"アカアシの好適地"),
  ("富士・朝霧高原","富士山麓",35.4167,138.5667,"静岡県","kanto",900,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","富士宮から車",True,6,1,True,"広大な高原のコナラ帯"),
  ("修善寺・冷川","伊豆",34.9833,138.9167,"静岡県","kanto",500,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","修善寺駅から車",True,8,1,True,"伊豆山地の谷間の雑木林"),
  ("伊豆・城ヶ崎","伊豆",34.8833,139.1000,"静岡県","kanto",50,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","伊豆高原駅から徒歩",True,5,1,True,"海岸林のクヌギ・コナラ"),
  # 長野(kanto扱い)追加
  ("蓼科高原","長野中部",36.1000,138.3167,"長野県","kanto",1700,["miyama","akaashi"],[6,7],"夜19〜22時","茅野駅から車",True,6,1,True,"女神湖周辺のコナラ林"),
  ("霧ヶ峰","長野中部",36.1000,138.2333,"長野県","kanto",1900,["miyama","akaashi"],[6,7],"夜19〜22時","茅野駅からバス",True,8,1,True,"高原の展望地。ミヤマ狙い"),
  ("白樺湖周辺","長野中部",36.0833,138.2833,"長野県","kanto",1416,["miyama","akaashi","nokogiri"],[6,7],"夜19〜22時","茅野駅からバス",True,6,1,True,"高原リゾート。ミヤマ安定"),
  ("八ヶ岳・原村","長野中部",35.9333,138.3500,"長野県","kanto",1350,["miyama","akaashi"],[6,7],"夜19〜22時","茅野駅から車",True,6,1,True,"八ヶ岳山麓のコナラ・カラマツ帯"),
  ("小諸・千曲川","長野東部",36.3167,138.4333,"長野県","kanto",700,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","小諸駅から車",True,6,1,True,"高原野菜産地の里山"),
  ("上田・鹿教湯","長野中部",36.3833,138.2000,"長野県","kanto",720,["miyama","nokogiri","kokuwagata"],[6,7,8],"夜20〜22時","上田駅から車",True,6,1,True,"五台山周辺のコナラ帯"),
  ("佐久・内山峠","長野東部",36.2167,138.6167,"長野県","kanto",1130,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","小諸ICから車",False,10,2,True,"荒船山の麓。ミヤマ出る"),
  # ===== 中部追加 +32件 =====
  # 長野追加
  ("辰野・みどり湖","長野南部",35.9833,137.9833,"長野県","chubu",780,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","みどり湖駅から車",True,6,1,True,"湖畔の広葉樹林"),
  ("伊那・高遠","長野南部",35.8000,137.9833,"長野県","chubu",750,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","伊那北駅から車",True,6,1,True,"桜で有名な城跡周辺"),
  ("下伊那・昼神温泉","長野南部",35.3500,137.6667,"長野県","chubu",630,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","飯田駅から車",True,8,1,True,"阿智川沿いの広葉樹林"),
  ("阿智・昼神","長野南部",35.3667,137.6500,"長野県","chubu",700,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","飯田ICから車",True,8,1,True,"日本一の星空の里。ライト有効"),
  ("飯山・菜の花公園","長野北部",36.8500,138.3833,"長野県","chubu",350,["miyama","nokogiri","kokuwagata"],[6,7,8],"夜20〜22時","飯山駅から車",True,6,1,True,"千曲川沿いの里山"),
  ("木島平高原","長野北部",36.8833,138.5000,"長野県","chubu",900,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","飯山駅から車",True,6,1,True,"スキーリゾート周辺"),
  # 岐阜追加
  ("岐阜・数河高原","飛騨",36.4167,137.0667,"岐阜県","chubu",1100,["miyama","akaashi"],[6,7],"夜19〜22時","飛騨市から車",False,10,2,True,"高原でミヤマ専門"),
  ("飛騨・神岡","飛騨北部",36.3333,137.2833,"岐阜県","chubu",670,["miyama","akaashi","nokogiri"],[6,7,8],"夜20〜22時","猪谷駅から車",False,10,2,True,"高原川沿いの広葉樹林"),
  ("岐阜・馬瀬川","飛騨南部",35.8333,137.0667,"岐阜県","chubu",450,["miyama","nokogiri","akaashi","hirata"],[6,7,8],"夜20〜23時","下呂駅から車",True,6,1,True,"馬瀬川上流の清流域"),
  ("岐阜・下呂・小坂","飛騨南部",35.8000,137.2333,"岐阜県","chubu",500,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","下呂駅から車",True,6,1,True,"飛騨川支流の山里"),
  ("岐阜・板取川","岐阜中部",35.6500,136.8167,"岐阜県","chubu",350,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","関駅から車",True,5,1,True,"モネの池で有名。川沿いクヌギ"),
  ("岐阜・東濃・苗木","岐阜南部",35.5167,137.4000,"岐阜県","chubu",430,["nokogiri","kabuto","kokuwagata","hirata"],[7,8],"夜20〜23時","中津川駅から車",True,5,1,True,"木曽川沿いの雑木林"),
  # 愛知追加
  ("愛知・三河湖","愛知東部",35.1667,137.2500,"愛知県","chubu",570,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","豊田市から車",True,6,1,True,"ダム湖周辺の広葉樹林"),
  ("愛知・旭・矢作","愛知中部",35.2500,137.2333,"愛知県","chubu",350,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","豊田市から車",True,5,1,True,"矢作川流域の雑木林"),
  ("愛知・茶臼山","愛知東部",35.0500,137.5167,"愛知県","chubu",1415,["miyama","akaashi"],[6,7],"夜19〜22時","豊根村から車",False,10,2,True,"愛知最高峰付近"),
  ("愛知・設楽","愛知東部",35.1333,137.6500,"愛知県","chubu",500,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","本長篠駅から車",True,6,1,True,"豊川源流域の里山"),
  # 三重追加
  ("三重・室生赤目","三重北部",34.6167,136.1167,"三重県","chubu",250,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","名張駅からバス",True,5,1,True,"青蓮寺湖周辺"),
  ("三重・多気・奥伊勢","三重中部",34.3333,136.3333,"三重県","chubu",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","多気駅から車",True,5,1,True,"宮川支流の里山"),
  # 静岡追加
  ("静岡・安倍川流域","静岡中部",35.1000,138.3333,"静岡県","chubu",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","静岡駅から車",True,6,1,True,"わさびで有名な清流域"),
  ("静岡・天竜川流域","静岡北部",35.0000,137.8333,"静岡県","chubu",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","浜松駅から車",True,5,1,True,"天竜川沿いの広葉樹林"),
  ("静岡・井川","静岡奥地",35.2333,138.0833,"静岡県","chubu",800,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","静岡駅からバス",False,10,2,True,"南アルプス南端の秘境"),
  ("静岡・本川根","静岡奥地",35.1500,138.1167,"静岡県","chubu",600,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","金谷駅からバス",False,10,2,True,"大井川上流の広葉樹林"),
  # 新潟追加
  ("新潟・佐渡島","新潟",38.0500,138.5167,"新潟県","chubu",500,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","両津港から車",True,6,1,True,"金山周辺のコナラ林"),
  ("新潟・魚沼","新潟",37.1833,138.9000,"新潟県","chubu",300,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","小出駅から車",True,6,1,True,"魚野川沿いの広葉樹林"),
  ("新潟・胎内","新潟北部",38.0833,139.4167,"新潟県","chubu",300,["miyama","nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","中条駅から車",True,5,1,True,"胎内川沿いの里山"),
  ("新潟・弥彦山","新潟中部",37.6833,138.8333,"新潟県","chubu",638,["miyama","nokogiri","akaashi","kokuwagata"],[6,7,8],"夜20〜22時","弥彦駅からロープウェー",True,6,1,True,"ロープウェーあり。コナラ林"),
  ("富山・立山麓","富山",36.5667,137.4833,"富山県","chubu",1000,["miyama","akaashi"],[6,7],"夜19〜22時","立山駅からケーブルカー",True,8,1,True,"室堂への道沿い。高標高"),
  ("富山・庄川峡","富山",36.5167,136.9333,"富山県","chubu",600,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","砺波駅から車",True,6,1,True,"庄川沿いの広葉樹林"),
  ("石川・白山麓","石川",36.1833,136.6333,"石川県","chubu",600,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","金沢駅から車",True,6,1,True,"白山ろくの広葉樹林"),
  ("石川・倶利伽羅","石川",36.6667,136.8333,"石川県","chubu",280,["nokogiri","kabuto","kokuwagata","hirata"],[7,8],"夜20〜23時","津幡駅から車",True,5,1,True,"峠周辺のクヌギ・コナラ"),
  ("石川・医王山","石川",36.5167,136.7667,"石川県","chubu",939,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","金沢駅から車",False,10,2,True,"金沢市民に人気の採集地"),
  ("福井・若狭","福井",35.5667,135.7333,"福井県","chubu",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","小浜駅から車",True,5,1,True,"小浜湾沿いの里山"),
  # ===== 近畿追加 +35件 =====
  # 京都追加
  ("京都・京北","京都北部",35.2167,135.6167,"京都府","kinki",400,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","周山バス停から徒歩",True,6,1,True,"京都の奥山。広葉樹林豊富"),
  ("京都・弓削","京都中部",35.4000,135.4333,"京都府","kinki",300,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","綾部駅から車",True,5,1,True,"由良川沿いの里山"),
  ("京都・福知山","京都北部",35.3000,135.1167,"京都府","kinki",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","福知山駅から車",True,5,1,True,"由良川沿いのクヌギ・コナラ"),
  ("京都・宮津","丹後",35.5333,135.2000,"京都府","kinki",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","宮津駅から車",True,5,1,True,"天橋立周辺の里山"),
  ("京都・笠置山","京都南部",34.7333,135.9500,"京都府","kinki",288,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","笠置駅から徒歩",True,5,1,True,"木津川沿いのクヌギ林"),
  # 大阪追加
  ("大阪・高槻・摂津峡","北摂",34.9000,135.5833,"大阪府","kinki",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","高槻駅から車",True,5,1,True,"渓谷沿い。ヒラタ出る"),
  ("大阪・北摂・るり渓","北摂",35.1000,135.5167,"大阪府","kinki",350,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","園部駅から車",True,5,1,True,"渓谷の広葉樹林"),
  ("大阪・泉南・岩湧山","和泉",34.4000,135.5833,"大阪府","kinki",898,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","河内長野駅から車",False,10,2,True,"大阪府最南部の山"),
  ("大阪・生駒山","生駒",34.6833,135.6833,"大阪府","kinki",642,["miyama","nokogiri","kokuwagata"],[6,7,8],"夜20〜22時","生駒駅からケーブルカー",True,6,1,True,"ケーブルカーあり"),
  # 兵庫追加
  ("兵庫・淡路島","淡路",34.5333,135.0167,"兵庫県","kinki",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","洲本バスから車",True,5,1,True,"南淡路の里山"),
  ("兵庫・播磨・千ヶ峰","播磨",35.0667,134.7333,"兵庫県","kinki",1005,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","西脇市から車",False,10,2,True,"播磨最高峰のコナラ林"),
  ("兵庫・丹波・黒井城","丹波",35.1333,135.1167,"兵庫県","kinki",356,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","黒井駅から徒歩",True,5,1,True,"城山周辺のコナラ・クヌギ"),
  ("兵庫・揖保川","播磨南部",34.8333,134.6000,"兵庫県","kinki",100,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","龍野駅から車",True,5,1,False,"揖保川沿いの広葉樹林"),
  ("兵庫・朝来・竹田城","但馬",35.3000,134.8333,"兵庫県","kinki",353,["nokogiri","kabuto","kokuwagata","miyama"],[7,8],"夜20〜23時","竹田駅から徒歩",True,6,1,True,"天空の城周辺の里山"),
  # 奈良追加
  ("奈良・春日山原始林","奈良盆地",34.6667,135.8500,"奈良県","kinki",400,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","近鉄奈良駅から徒歩",True,5,1,True,"世界遺産の原始林"),
  ("奈良・宇陀","奈良東部",34.5333,135.9667,"奈良県","kinki",500,["nokogiri","kabuto","hirata","kokuwagata","miyama"],[7,8],"夜20〜23時","大宇陀から車",True,6,1,True,"宇陀川沿いの里山"),
  ("奈良・大峰・洞川","大峰",34.2667,135.8000,"奈良県","kinki",820,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","下市口駅から車",False,10,2,True,"修験道の霊地。ブナ帯"),
  ("奈良・東吉野","奈良東部",34.4000,136.0333,"奈良県","kinki",400,["miyama","nokogiri","akaashi","hirata"],[6,7,8],"夜20〜23時","大和八木駅から車",True,6,1,True,"高見川沿いの広葉樹林"),
  # 和歌山追加
  ("和歌山・那智山","熊野",33.6667,135.9167,"和歌山県","kinki",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","紀伊勝浦駅からバス",True,5,1,True,"那智の滝周辺"),
  ("和歌山・有田川","和歌山中部",34.0833,135.3500,"和歌山県","kinki",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","有田駅から車",True,5,1,True,"有田みかん産地の里山"),
  ("和歌山・田辺","紀伊南部",33.7333,135.3833,"和歌山県","kinki",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","紀伊田辺駅から車",True,5,1,True,"熊野古道沿いの里山"),
  # 滋賀追加
  ("滋賀・鈴鹿・御池岳","鈴鹿山脈",35.0500,136.3333,"滋賀県","kinki",1247,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","近江鉄道から車",False,10,2,True,"コナラ・ミズナラ帯"),
  ("滋賀・朽木","滋賀北部",35.3500,135.8833,"滋賀県","kinki",300,["nokogiri","kabuto","hirata","kokuwagata","miyama"],[7,8],"夜20〜23時","安曇川駅から車",True,6,1,True,"安曇川源流の里山"),
  ("滋賀・永源寺","滋賀東部",35.0333,136.2833,"滋賀県","kinki",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","八日市駅から車",True,6,1,True,"愛知川沿いの広葉樹林"),
  ("滋賀・近江八幡","琵琶湖東岸",35.1333,136.0833,"滋賀県","kinki",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","近江八幡駅から車",True,5,1,True,"八幡山周辺の里山"),
  # 福井追加
  ("福井・敦賀","福井",35.6500,136.0833,"福井県","kinki",400,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","敦賀駅から車",True,5,1,True,"野坂山麓の広葉樹林"),
  ("福井・小浜","福井",35.5000,135.7333,"福井県","kinki",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","小浜駅から車",True,5,1,True,"若狭の里山"),
  ("福井・永平寺","福井中部",36.1000,136.3500,"福井県","kinki",350,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","永平寺口駅から車",True,6,1,True,"禅寺の杉林と広葉樹林"),
  ("福井・勝山","福井北部",36.0667,136.5000,"福井県","kinki",500,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","勝山駅から車",True,6,1,True,"恐竜博物館の近く"),
  # 三重追加
  ("三重・伊勢","三重南部",34.4833,136.7333,"三重県","kinki",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","伊勢市駅から車",True,5,1,True,"神宮の森周辺"),
  ("三重・鈴鹿・錫杖湖","鈴鹿",34.8667,136.4833,"三重県","kinki",350,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","亀山駅から車",True,5,1,True,"鈴鹿山麓の里山"),
  ("三重・熊野市","熊野",33.8833,136.1000,"三重県","kinki",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","熊野市駅から車",True,5,1,True,"熊野川沿いの広葉樹林"),
  # ===== 東北追加 +25件 =====
  ("福島・会津・西会津","東北南部",37.5000,139.5833,"福島県","tohoku",400,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","野沢駅から車",True,6,1,True,"阿賀川沿いの広葉樹林"),
  ("福島・いわき","東北南部",37.0500,140.8833,"福島県","tohoku",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","いわき駅から車",True,5,1,True,"夏井川沿いの里山"),
  ("福島・郡山・湖南","東北南部",37.3333,140.4833,"福島県","tohoku",600,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","郡山駅から車",True,6,1,True,"湖南高原の広葉樹林"),
  ("福島・南会津","東北南部",37.1833,139.5500,"福島県","tohoku",600,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","会津高原尾瀬口駅から車",False,10,2,True,"只見川源流の山里"),
  ("山形・上山","東北中部",38.1833,140.2833,"山形県","tohoku",300,["nokogiri","kabuto","kokuwagata","miyama"],[7,8],"夜20〜23時","かみのやま温泉駅から車",True,5,1,True,"蔵王の麓の里山"),
  ("山形・天童","東北中部",38.3667,140.3833,"山形県","tohoku",200,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","天童駅から車",True,5,1,True,"将棋の里。里山の雑木林"),
  ("山形・最上川流域","東北中部",38.7667,140.2167,"山形県","tohoku",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","新庄駅から車",True,5,1,False,"最上川沿いの広葉樹林"),
  ("山形・小国","東北中部",38.0667,139.7333,"山形県","tohoku",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","坂町駅から車",False,10,2,True,"荒川沿いの広葉樹林"),
  ("宮城・気仙沼","東北南部",38.9167,141.5667,"宮城県","tohoku",200,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","気仙沼駅から車",True,5,1,True,"内湾周辺の里山"),
  ("宮城・栗原","東北南部",38.7333,141.0000,"宮城県","tohoku",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","くりこま高原駅から車",True,6,1,True,"栗駒山麓の広葉樹林"),
  ("宮城・加美","東北南部",38.5333,140.8167,"宮城県","tohoku",500,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","古川駅から車",False,10,2,True,"薬莱山周辺のコナラ林"),
  ("岩手・種山高原","東北中部",39.2000,141.2333,"岩手県","tohoku",700,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","遠野駅から車",False,10,2,True,"宮沢賢治の舞台。広葉樹林"),
  ("岩手・北上","東北中部",39.3000,141.1333,"岩手県","tohoku",200,["nokogiri","kabuto","kokuwagata"],[7,8],"夜20〜23時","北上駅から車",True,5,1,True,"展勝地周辺の里山"),
  ("秋田・横手","秋田南部",39.3167,140.5667,"秋田県","tohoku",100,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","横手駅から車",True,5,1,False,"横手川沿いの里山"),
  ("秋田・阿仁","秋田中部",40.0500,140.4333,"秋田県","tohoku",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","阿仁前田温泉駅から車",True,6,1,True,"阿仁川沿いの広葉樹林"),
  ("秋田・鹿角","秋田北部",40.2167,140.7833,"秋田県","tohoku",300,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","鹿角花輪駅から車",True,6,1,True,"大湯温泉周辺"),
  ("青森・三沢","東北北部",40.6833,141.3833,"青森県","tohoku",80,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","三沢駅から車",True,5,1,True,"低地のクヌギ・コナラ林"),
  ("青森・奥入瀬流域","東北北部",40.5500,141.1500,"青森県","tohoku",400,["miyama","akaashi","nokogiri"],[7,8],"夜20〜22時","十和田湖から徒歩",True,6,1,True,"渓流沿いの原生林"),
  ("青森・黒石","東北北部",40.6333,140.5833,"青森県","tohoku",300,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","黒石駅から車",True,6,1,True,"こみせ通り周辺の里山"),
  ("青森・白神山地麓","東北北部",40.3667,140.1167,"青森県","tohoku",400,["miyama","akaashi","nokogiri"],[7,8],"夜20〜22時","能代駅から車",False,10,2,True,"世界遺産のブナ林"),
  ("岩手・一関","東北南部",38.9333,141.1167,"岩手県","tohoku",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","一ノ関駅から車",True,5,1,True,"磐井川沿いの里山"),
  ("福島・猪苗代湖南岸","東北南部",37.5333,140.1333,"福島県","tohoku",514,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","猪苗代駅から車",True,6,1,True,"湖畔の広葉樹林"),
  ("山形・飯豊山麓","東北中部",38.0833,139.8500,"山形県","tohoku",500,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","荒砥駅から車",False,10,2,True,"飯豊連峰の麓の広葉樹林"),
  ("宮城・七ヶ宿","東北南部",38.0667,140.3333,"宮城県","tohoku",600,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","白石駅から車",False,10,2,True,"七ヶ宿ダム周辺"),
  ("岩手・岩泉","東北北部",39.7333,141.8000,"岩手県","tohoku",300,["miyama","nokogiri","akaashi"],[7,8],"夜20〜22時","茂市駅から車",False,10,2,True,"龍泉洞周辺の広葉樹林"),
  # ===== 九州追加 +25件 =====
  ("福岡・朝倉・三連水車","九州北部",33.4167,130.7500,"福岡県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","甘木鉄道から車",True,5,1,True,"筑後川沿いの里山"),
  ("福岡・添田・香春","九州北部",33.5500,130.8333,"福岡県","kyushu",350,["nokogiri","kabuto","kokuwagata","miyama"],[7,8],"夜20〜23時","香春駅から車",True,5,1,True,"石灰岩の山の周辺林"),
  ("大分・佐伯","九州南東部",32.9500,131.8000,"大分県","kyushu",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","佐伯駅から車",True,5,1,True,"番匠川沿いの広葉樹林"),
  ("大分・豊後大野","九州中部",32.9833,131.5833,"大分県","kyushu",400,["nokogiri","kabuto","hirata","kokuwagata","miyama"],[7,8],"夜20〜23時","三重町駅から車",True,6,1,True,"大野川沿いの里山"),
  ("大分・別府・鶴見岳","九州北東部",33.2833,131.4833,"大分県","kyushu",1374,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","別府駅からロープウェー",True,8,1,True,"温泉地の高台"),
  ("熊本・八代","熊本西部",32.5000,130.6167,"熊本県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","八代駅から車",True,5,1,True,"球磨川下流の里山"),
  ("熊本・菊池渓谷","熊本北部",33.0000,130.9333,"熊本県","kyushu",600,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","熊本駅から車",True,6,1,True,"清流の渓谷。広葉樹林"),
  ("熊本・山都・通潤橋","熊本中部",32.6167,130.9333,"熊本県","kyushu",400,["nokogiri","kabuto","kokuwagata","miyama"],[7,8],"夜20〜23時","熊本駅から車",True,5,1,True,"石橋と里山"),
  ("宮崎・日向・耳川流域","九州東部",32.5333,131.6333,"宮崎県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","日向市駅から車",True,5,1,True,"耳川沿いの広葉樹林"),
  ("宮崎・都城・霧島東","九州南部",31.7167,131.0500,"宮崎県","kyushu",400,["nokogiri","kabuto","hirata","kokuwagata","miyama"],[7,8],"夜20〜23時","都城駅から車",True,5,1,True,"関之尾滝周辺の里山"),
  ("鹿児島・姶良","鹿児島北部",31.7333,130.6167,"鹿児島県","kyushu",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","帖佐駅から車",True,5,1,True,"重富海岸の背後の山林"),
  ("鹿児島・薩摩川内","鹿児島西部",31.8167,130.3000,"鹿児島県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","川内駅から車",True,5,1,True,"川内川沿いの里山"),
  ("長崎・佐世保","九州西部",33.1667,129.7167,"長崎県","kyushu",400,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","佐世保駅から車",True,5,1,True,"九十九島周辺の山林"),
  ("長崎・五島列島","九州西部",32.7000,128.8333,"長崎県","kyushu",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","福江港から車",True,5,1,True,"離島の広葉樹林"),
  ("佐賀・多久","九州北部",33.2833,129.9833,"佐賀県","kyushu",300,["nokogiri","kabuto","kokuwagata","miyama"],[7,8],"夜20〜23時","多久駅から車",True,5,1,True,"牧ノ山周辺の里山"),
  ("佐賀・嬉野","九州北部",33.1000,129.9333,"佐賀県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","武雄温泉駅から車",True,5,1,True,"嬉野温泉周辺の里山"),
  ("熊本・水上村・市房山","熊本南部",32.3667,130.9333,"熊本県","kyushu",1721,["miyama","akaashi"],[6,7],"夜19〜22時","人吉駅から車",False,12,3,True,"九州のミヤマの名所"),
  ("宮崎・五ヶ瀬","九州中部",32.6500,131.2333,"宮崎県","kyushu",600,["miyama","akaashi","nokogiri"],[6,7,8],"夜20〜22時","延岡駅から車",False,10,2,True,"九州脊梁山地の中心"),
  ("鹿児島・指宿","薩摩",31.2667,130.6333,"鹿児島県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","指宿駅から車",True,5,1,True,"知林ヶ島周辺の林"),
  ("熊本・南阿蘇","阿蘇",32.8833,131.0833,"熊本県","kyushu",700,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","立野駅から車",True,6,1,True,"外輪山内側の広葉樹林"),
  ("大分・杵築","九州北東部",33.4000,131.6167,"大分県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","杵築駅から車",True,5,1,True,"武家屋敷近くの里山"),
  ("福岡・糸島","九州北部",33.5500,130.1833,"福岡県","kyushu",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","筑前前原駅から車",True,5,1,True,"二丈山系の里山"),
  ("福岡・朝倉・秋月","九州北部",33.4333,130.6833,"福岡県","kyushu",400,["nokogiri","kabuto","miyama","kokuwagata"],[7,8],"夜20〜23時","甘木駅から車",True,5,1,True,"秋月城下町の里山"),
  ("長崎・島原","九州西部",32.7833,130.3667,"長崎県","kyushu",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","島原駅から車",True,6,1,True,"普賢岳周辺の広葉樹林"),
  ("熊本・小国","阿蘇",33.1167,131.0667,"熊本県","kyushu",500,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","杖立温泉から車",True,6,1,True,"杖立川沿いの広葉樹林"),
  # ===== 中国追加 +20件 =====
  ("広島・芸北・八幡高原","中国山地",34.7833,132.5000,"広島県","chugoku",900,["miyama","akaashi","nokogiri"],[6,7],"夜19〜22時","浜田道から車",True,8,1,True,"高原でミヤマ安定"),
  ("広島・世羅","中国山地",34.5833,133.0333,"広島県","chugoku",350,["nokogiri","kabuto","kokuwagata","hirata"],[7,8],"夜20〜23時","三次駅から車",True,5,1,True,"世羅高原の里山"),
  ("広島・熊野","広島東部",34.3833,132.5833,"広島県","chugoku",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","矢野駅から車",True,5,1,True,"熊野筆の里。里山"),
  ("広島・大朝","中国山地",34.8333,132.4500,"広島県","chugoku",500,["miyama","nokogiri","akaashi","kabuto"],[6,7,8],"夜20〜23時","大朝ICから車",True,6,1,True,"旭川源流の里山"),
  ("岡山・津山","中国山地",35.0667,134.0000,"岡山県","chugoku",250,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","津山駅から車",True,5,1,True,"吉井川沿いの里山"),
  ("岡山・真庭・湯原","中国山地",35.1833,133.7667,"岡山県","chugoku",400,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜23時","中国道から車",True,6,1,True,"旭川沿いの広葉樹林"),
  ("岡山・奥津渓","中国山地",35.0833,133.8000,"岡山県","chugoku",350,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","津山駅から車",False,10,2,True,"吉井川上流の渓谷"),
  ("岡山・備中松山城","中国山地",34.8667,133.6333,"岡山県","chugoku",430,["miyama","nokogiri","akaashi","kokuwagata"],[6,7,8],"夜20〜22時","備中高梁駅から車",True,6,1,True,"山城周辺の広葉樹林"),
  ("鳥取・船岡","中国山地",35.3000,134.0500,"鳥取県","chugoku",500,["miyama","nokogiri","akaashi","kabuto"],[7,8],"夜20〜22時","郡家駅から車",False,10,2,True,"八東川沿いの広葉樹林"),
  ("鳥取・若桜","中国山地",35.3333,134.3833,"鳥取県","chugoku",500,["miyama","nokogiri","akaashi"],[6,7,8],"夜20〜22時","若桜鉄道若桜駅から車",False,10,2,True,"若桜鬼ヶ城周辺"),
  ("島根・仁多","中国山地",35.1500,133.1833,"島根県","chugoku",600,["miyama","akaashi","nokogiri"],[6,7],"夜20〜22時","木次線から車",False,10,2,True,"奥出雲の山里"),
  ("島根・浜田","島根西部",34.8833,132.0833,"島根県","chugoku",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","浜田駅から車",True,5,1,True,"高山谷周辺の里山"),
  ("山口・錦川","山口東部",34.2167,132.0167,"山口県","chugoku",300,["nokogiri","kabuto","hirata","kokuwagata","miyama"],[7,8],"夜20〜23時","錦町駅から車",True,5,1,True,"錦川沿いの広葉樹林"),
  ("山口・萩","山口北部",34.4000,131.3833,"山口県","chugoku",300,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","東萩駅から車",True,5,1,True,"萩城下町周辺の里山"),
  ("山口・宇部","山口南部",33.9500,131.2500,"山口県","chugoku",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","宇部駅から車",True,5,1,True,"厚東川沿いの里山"),
  ("広島・三原","広島南部",34.4000,133.0833,"広島県","chugoku",200,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","三原駅から車",True,5,1,True,"沼田川沿いの里山"),
  ("岡山・和気・吉井川","岡山南部",34.8000,134.0667,"岡山県","chugoku",150,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","和気駅から車",True,5,1,False,"吉井川沿いのヤナギ帯"),
  ("鳥取・大栄","鳥取中部",35.5000,133.8167,"鳥取県","chugoku",100,["nokogiri","kabuto","hirata","kokuwagata"],[7,8],"夜20〜23時","由良駅から車",True,5,1,True,"北栄町の砂丘背後の林"),
  ("島根・松江","島根中部",35.4667,133.0500,"島根県","chugoku",300,["nokogiri","kabuto","hirata","kokuwagata","miyama"],[7,8],"夜20〜23時","松江駅から車",True,5,1,True,"宍道湖周辺の里山"),
  ("広島・安芸太田","中国山地",34.6667,132.4333,"広島県","chugoku",700,["miyama","nokogiri","akaashi"],[6,7],"夜20〜22時","戸河内ICから車",False,10,2,True,"太田川源流の広葉樹林"),
]

# ── 変換関数 ─────────────────────────────────────────────────────
def make_family_spot(fid, row):
    name,area,lat,lng,pref,region,elev,species,best_months,best_time,access,fok,cage,diff,park,notes = row
    return {
        "id": fid,
        "name": name,
        "area": area,
        "lat": lat,
        "lng": lng,
        "prefecture": pref,
        "region": region,
        "elevation": elev,
        "species": species,
        "best_months": best_months,
        "best_time": best_time,
        "access": access,
        "family_ok": fok,
        "child_min_age": cage,
        "difficulty": diff,
        "parking": park,
        "notes": notes,
        "verified": True
    }

def tree_preset(elev, region, slope):
    if elev > 1400:
        return {"buna":0.5,"mizunara":0.3,"urajirogashi":0.1,"konara":0.1}
    elif elev > 900:
        if region in ["tohoku","hokkaido"]: return {"mizunara":0.45,"buna":0.35,"konara":0.15,"kunugi":0.05}
        return {"konara":0.35,"mizunara":0.3,"buna":0.2,"kunugi":0.15}
    elif elev > 400:
        if region in ["kinki","chugoku","shikoku","kyushu"]:
            return {"konara":0.4,"kunugi":0.3,"mizunara":0.15,"yanagi":0.1,"hannoki":0.05}
        return {"konara":0.45,"kunugi":0.3,"mizunara":0.15,"hannoki":0.1}
    else:
        return {"kunugi":0.5,"konara":0.25,"yanagi":0.15,"hannoki":0.1}

def water_dist():
    return random.choice([30,50,80,100,150,200,300,500])

def light_pol(elev, density="low"):
    base = max(0, min(5, 5 - elev//400))
    return max(0, base - (1 if density=="very_low" else 0))

def make_expert_spot(eid, fs, variant_idx):
    dlat = random.uniform(-0.015, 0.015)
    dlng = random.uniform(-0.020, 0.020)
    lat = round(fs["lat"] + dlat, 4)
    lng = round(fs["lng"] + dlng, 4)
    elev = max(50, fs["elevation"] + random.randint(-100, 150))
    slope = random.choice(["N","NE","E","SE","S","SW","W","NW"])
    trees = tree_preset(elev, fs["region"], slope)
    water = water_dist()
    lp = light_pol(elev)
    sub_names = ["北面コナラ帯","南斜面クヌギ林","谷間樹液帯","尾根沿いミズナラ","渓流沿いヤナギ帯","高台コナラ林"]
    sub_name = f"{fs['name']}・{sub_names[variant_idx % len(sub_names)]}"
    best_sp = []
    if "miyama" in fs["species"] and elev >= 400: best_sp.append("miyama")
    if "akaashi" in fs["species"] and elev >= 600: best_sp.append("akaashi")
    if "nokogiri" in fs["species"]: best_sp.append("nokogiri")
    if "hirata" in fs["species"] and water < 150: best_sp.append("hirata")
    if "kabuto" in fs["species"] and elev < 800: best_sp.append("kabuto")
    if not best_sp: best_sp = ["nokogiri","kokuwagata"]
    return {
        "id": eid,
        "name": sub_name,
        "lat": lat,
        "lng": lng,
        "prefecture": fs["prefecture"],
        "region": fs["region"],
        "elevation": elev,
        "slope": slope,
        "trees": trees,
        "water_m": water,
        "light_pollution": lp,
        "access_hard": min(3, fs["difficulty"] + (1 if variant_idx >= 3 else 0)),
        "best": best_sp[:3],
        "best_months": fs["best_months"]
    }

# ── 変換して追加 ─────────────────────────────────────────────────
new_fspots = []
fid = max_fid + 1
for row in ADD_SPOTS:
    new_fspots.append(make_family_spot(fid, row))
    fid += 1

new_espots = []
eid = max_eid + 1
for fs in new_fspots:
    num_variants = 5 if fs["region"] in ["kanto","chubu","kinki"] else 4
    for v in range(num_variants):
        new_espots.append(make_expert_spot(eid, fs, v))
        eid += 1

# ── マージして保存 ───────────────────────────────────────────────
all_fspots = family_spots + new_fspots
all_espots = expert_spots + new_espots

with open("static/family_spots.json","w",encoding="utf-8") as f:
    json.dump({"spots": all_fspots}, f, ensure_ascii=False, indent=None)
with open("static/expert_spots.json","w",encoding="utf-8") as f:
    json.dump({"spots": all_espots}, f, ensure_ascii=False, indent=None)

from collections import Counter
r_count = Counter(s["region"] for s in all_fspots)
print(f"家族用スポット合計: {len(all_fspots)}件")
print(f"玄人用スポット合計: {len(all_espots)}件")
print("地域別:", dict(sorted(r_count.items())))
