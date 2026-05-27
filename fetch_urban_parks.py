"""
fetch_urban_parks.py
──────────────────────────────────────────────────────────────────────
OpenStreetMap Overpass API を使って主要都市の公園を取得し、
クワガタ採集スポット候補として urban_park_spots.json に保存する。

対象：東京・横浜・埼玉・千葉・大阪・名古屋・福岡・札幌・京都・神戸・仙台・広島
条件：leisure=park または landuse=park で名前のある公園
後処理：面積推定・標高推定・species推定を自動付与
"""

import json
import math
import time
import requests

# ── 設定 ─────────────────────────────────────────────────────────────

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "beetle-finder-urban/1.0 (clam research)"}
OUT_FILE = "static/urban_park_spots.json"

# 取得する都市・地域の定義 (name, region, prefecture, bbox=[s,w,n,e])
CITIES = [
    # ── 関東 ──────────────────────────────────────────
    {"label": "東京23区",    "region": "kanto", "pref": "東京都",   "bbox": [35.53, 139.60, 35.82, 139.92]},
    {"label": "東京多摩",    "region": "kanto", "pref": "東京都",   "bbox": [35.60, 139.00, 35.90, 139.62]},
    {"label": "横浜市",      "region": "kanto", "pref": "神奈川県", "bbox": [35.30, 139.40, 35.60, 139.78]},
    {"label": "川崎市",      "region": "kanto", "pref": "神奈川県", "bbox": [35.50, 139.55, 35.65, 139.78]},
    {"label": "埼玉南部",    "region": "kanto", "pref": "埼玉県",   "bbox": [35.76, 139.42, 36.05, 139.78]},
    {"label": "千葉北西部",  "region": "kanto", "pref": "千葉県",   "bbox": [35.55, 139.88, 35.82, 140.20]},
    {"label": "相模原・厚木", "region": "kanto", "pref": "神奈川県", "bbox": [35.38, 139.20, 35.65, 139.55]},
    # ── 近畿 ──────────────────────────────────────────
    {"label": "大阪市",      "region": "kinki", "pref": "大阪府",   "bbox": [34.55, 135.38, 34.75, 135.60]},
    {"label": "大阪北部",    "region": "kinki", "pref": "大阪府",   "bbox": [34.72, 135.40, 34.92, 135.65]},
    {"label": "京都市",      "region": "kinki", "pref": "京都府",   "bbox": [34.92, 135.62, 35.10, 135.83]},
    {"label": "神戸市",      "region": "kinki", "pref": "兵庫県",   "bbox": [34.62, 135.00, 34.80, 135.32]},
    # ── 中部 ──────────────────────────────────────────
    {"label": "名古屋市",    "region": "chubu", "pref": "愛知県",   "bbox": [35.05, 136.78, 35.28, 137.05]},
    {"label": "浜松・静岡",  "region": "chubu", "pref": "静岡県",   "bbox": [34.60, 137.55, 35.00, 138.40]},
    # ── 九州 ──────────────────────────────────────────
    {"label": "福岡市",      "region": "kyushu", "pref": "福岡県",  "bbox": [33.50, 130.25, 33.70, 130.55]},
    {"label": "北九州市",    "region": "kyushu", "pref": "福岡県",  "bbox": [33.80, 130.65, 33.98, 131.00]},
    {"label": "熊本市",      "region": "kyushu", "pref": "熊本県",  "bbox": [32.65, 130.55, 32.90, 130.88]},
    # ── 北海道・東北 ──────────────────────────────────
    {"label": "札幌市",      "region": "tohoku", "pref": "北海道",  "bbox": [43.00, 141.13, 43.28, 141.50]},
    {"label": "仙台市",      "region": "tohoku", "pref": "宮城県",  "bbox": [38.18, 140.78, 38.42, 141.05]},
    # ── 中国・四国 ─────────────────────────────────────
    {"label": "広島市",      "region": "chugoku", "pref": "広島県", "bbox": [34.30, 132.32, 34.50, 132.58]},
    {"label": "岡山市",      "region": "chugoku", "pref": "岡山県", "bbox": [34.58, 133.82, 34.75, 133.98]},
]

# 地域ごとのデフォルト種（公園・低地）
REGION_SPECIES = {
    "kanto":   ["nokogiri", "kabuto", "kokuwagata", "hirata"],
    "kinki":   ["nokogiri", "kabuto", "kokuwagata", "hirata"],
    "chubu":   ["nokogiri", "kabuto", "kokuwagata", "hirata"],
    "kyushu":  ["nokogiri", "kabuto", "kokuwagata", "hirata"],
    "tohoku":  ["nokogiri", "kabuto", "kokuwagata"],
    "chugoku": ["nokogiri", "kabuto", "kokuwagata", "hirata"],
}

# ── ユーティリティ ────────────────────────────────────────────────────

def haversine(lat1, lng1, lat2, lng2):
    R = 6371000  # メートル
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlng / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def estimate_area_m2(nodes_latlon):
    """ノード列から概算面積(m²)を計算（Shoelace公式近似）"""
    if len(nodes_latlon) < 3:
        return 0
    lats = [n[0] for n in nodes_latlon]
    lngs = [n[1] for n in nodes_latlon]
    # 近似スケール（東京付近）
    lat_m = 111000
    lng_m = 111000 * math.cos(math.radians(sum(lats) / len(lats)))
    n = len(lats)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += (lats[i] * lat_m) * (lngs[j] * lng_m)
        area -= (lats[j] * lat_m) * (lngs[i] * lng_m)
    return abs(area) / 2


def classify_difficulty(area_ha, tags):
    """面積と属性から難易度(1〜3)を推定"""
    if area_ha >= 20:
        return 1  # 大きい公園は設備整備済み
    if area_ha >= 5:
        return 1
    return 1  # 公園はほぼ難易度1


def estimate_child_age(area_ha, tags):
    """面積からファミリー向け最低年齢を推定"""
    if area_ha >= 5:
        return 4
    return 5


def build_access_note(tags):
    """OSMタグからアクセス情報を組み立て"""
    parts = []
    if "website" in tags:
        pass  # URLは入れない
    if "operator" in tags:
        parts.append(tags["operator"] + "管理")
    note = "。".join(parts)
    return note if note else "公共交通機関またはお車でのアクセス"


def get_notes(tags, area_ha, region):
    """採集メモを生成"""
    notes = []
    if area_ha >= 30:
        notes.append("広大な樹林帯あり")
    elif area_ha >= 10:
        notes.append("クヌギ・コナラ林を確認要")
    else:
        notes.append("雑木林エリアを事前に確認")

    park_name = tags.get("name", "")
    if "森" in park_name or "林" in park_name:
        notes.append("森林系公園")
    if "川" in park_name or "河" in park_name:
        notes.append("河川沿い・ヤナギ帯の可能性")
    if "緑地" in park_name:
        notes.append("緑地保全区域")

    notes.append("※採集前に公園管理事務所で採集可否を確認")
    return "。".join(notes)


# ── Overpass クエリ ───────────────────────────────────────────────────

def build_query(bbox, timeout=60):
    s, w, n, e = bbox
    bbox_str = f"{s},{w},{n},{e}"
    return f"""
[out:json][timeout:{timeout}];
(
  way[leisure=park][name]({bbox_str});
  way[landuse=recreation_ground][name]({bbox_str});
  relation[leisure=park][name]({bbox_str});
);
out body;
>;
out skel qt;
"""


def fetch_parks(city):
    """1都市分の公園データを取得"""
    query = build_query(city["bbox"])
    for attempt in range(3):
        try:
            resp = requests.post(
                OVERPASS_URL,
                data={"data": query},
                headers=HEADERS,
                timeout=90,
            )
            if resp.status_code == 200:
                return resp.json()
            print(f"  HTTP {resp.status_code} → リトライ {attempt + 1}/3")
        except requests.exceptions.Timeout:
            print(f"  タイムアウト → リトライ {attempt + 1}/3")
        except Exception as ex:
            print(f"  エラー: {ex} → リトライ {attempt + 1}/3")
        time.sleep(5 * (attempt + 1))
    return None


# ── メイン処理 ────────────────────────────────────────────────────────

def process_city(city, raw_data, next_id):
    """都市のOSMデータをスポットリストに変換"""
    spots = []
    if not raw_data:
        return spots, next_id

    # nodeをIDでマッピング
    node_map = {}
    for el in raw_data.get("elements", []):
        if el["type"] == "node":
            node_map[el["id"]] = (el["lat"], el["lon"])

    seen_names = set()

    for el in raw_data.get("elements", []):
        if el["type"] not in ("way", "relation"):
            continue

        tags = el.get("tags", {})
        name = tags.get("name", "").strip()
        if not name or name in seen_names:
            continue

        # センター座標を取得
        if "center" in el:
            lat, lng = el["center"]["lat"], el["center"]["lon"]
        elif el["type"] == "way" and "nodes" in el:
            node_latlngs = [node_map[nid] for nid in el["nodes"] if nid in node_map]
            if not node_latlngs:
                continue
            lat = sum(p[0] for p in node_latlngs) / len(node_latlngs)
            lng = sum(p[1] for p in node_latlngs) / len(node_latlngs)
        else:
            continue

        # バウンディングボックス外ならスキップ
        s, w, n, e = city["bbox"]
        if not (s <= lat <= n and w <= lng <= e):
            continue

        # 面積推定（wayのノード数を代理指標に使う）
        if el["type"] == "way" and "nodes" in el:
            node_latlngs = [node_map[nid] for nid in el["nodes"] if nid in node_map]
            area_m2 = estimate_area_m2(node_latlngs)
            area_ha = area_m2 / 10000
        else:
            # relationの場合は名前から推定
            area_ha = 5.0

        # 小さすぎる公園（0.3ha未満 ≈ 30m×100m）は除外
        if area_ha < 0.3:
            continue

        # 採集規模感でフィルタ（都市部は1ha未満は除外）
        is_urban_23ku = city["label"] in ("東京23区", "大阪市", "名古屋市", "福岡市", "札幌市")
        if is_urban_23ku and area_ha < 1.0:
            continue

        seen_names.add(name)

        # 種・シーズン推定
        species = REGION_SPECIES.get(city["region"], ["nokogiri", "kabuto", "kokuwagata"])
        best_months = [7, 8]
        if city["region"] == "tohoku":
            best_months = [7, 8]
        if city["region"] in ("kanto", "kinki", "chubu", "kyushu", "chugoku"):
            best_months = [7, 8]

        spot = {
            "id": next_id,
            "name": name,
            "area": city["label"],
            "lat": round(lat, 6),
            "lng": round(lng, 6),
            "prefecture": city["pref"],
            "region": city["region"],
            "elevation": 10,          # 公園は低地とみなす（後で国土地理院APIで補完可）
            "species": species,
            "best_months": best_months,
            "best_time": "夜20〜23時（早朝4〜7時も可）",
            "access": build_access_note(tags),
            "family_ok": True,
            "child_min_age": estimate_child_age(area_ha, tags),
            "difficulty": classify_difficulty(area_ha, tags),
            "parking": tags.get("parking") == "yes" or area_ha >= 5,
            "notes": get_notes(tags, area_ha, city["region"]),
            "spot_type": "urban_park",
            "area_ha": round(area_ha, 1),
            "osm_id": el["id"],
            "verified": False,
        }
        spots.append(spot)
        next_id += 1

    return spots, next_id


def main():
    all_spots = []
    # 既存family_spotsの最大IDを取得して続番にする
    try:
        with open("static/family_spots.json", encoding="utf-8") as f:
            fam = json.load(f)
        next_id = max(s["id"] for s in fam["spots"]) + 1
    except Exception:
        next_id = 5000

    print(f"開始ID: {next_id}")
    print(f"対象都市: {len(CITIES)}都市\n")

    for i, city in enumerate(CITIES, 1):
        print(f"[{i:02d}/{len(CITIES)}] {city['label']} を取得中...", end=" ", flush=True)
        raw = fetch_parks(city)
        new_spots, next_id = process_city(city, raw, next_id)
        all_spots.extend(new_spots)
        print(f"{len(new_spots)}件取得")
        time.sleep(3)  # Overpass API 負荷対策

    print(f"\n合計: {len(all_spots)}件")

    # 保存
    output = {
        "description": "主要都市の公園スポット（OpenStreetMapから自動取得）",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "note": "verified=false は未確認スポット。採集可否は各公園に要確認。",
        "total": len(all_spots),
        "spots": all_spots,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"保存完了: {OUT_FILE}")

    # 都市別件数サマリー
    print("\n── 都市別取得件数 ──")
    from collections import Counter
    c = Counter(s["area"] for s in all_spots)
    for label, count in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {label:12s}: {count:4d}件")

    # 面積分布
    print("\n── 面積分布 ──")
    tiny  = sum(1 for s in all_spots if s["area_ha"] <  1)
    small = sum(1 for s in all_spots if  1 <= s["area_ha"] <  5)
    mid   = sum(1 for s in all_spots if  5 <= s["area_ha"] < 20)
    large = sum(1 for s in all_spots if 20 <= s["area_ha"])
    print(f"  <1ha   : {tiny}件")
    print(f"  1〜5ha : {small}件")
    print(f"  5〜20ha: {mid}件")
    print(f"  20ha〜 : {large}件")

    # クワガタ採集に向いていそうな大型公園TOP10
    print("\n── 面積TOP10（有望候補） ──")
    top10 = sorted(all_spots, key=lambda s: -s["area_ha"])[:10]
    for s in top10:
        print(f"  {s['name']:20s}  {s['area_ha']:6.1f}ha  {s['prefecture']}")


if __name__ == "__main__":
    main()
