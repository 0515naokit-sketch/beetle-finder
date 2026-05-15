from flask import Flask, render_template, Response, jsonify, request, stream_with_context
import requests
import math
import json
import hashlib
import datetime

app = Flask(__name__)

DEFAULT_LAT  = 35.7447
DEFAULT_LNG  = 139.8487
KM_PER_HOUR  = 55   # 実道路換算（高速+一般道混合）
MAX_RADIUS   = 500  # km
HEADERS      = {"User-Agent": "KuwagataSpotFinder/1.0 (beetle collecting research)"}

SPECIES_JA = {
    "quercus acutissima":   "クヌギ",
    "quercus serrata":      "コナラ",
    "quercus crispula":     "ミズナラ",
    "fagus crenata":        "ブナ",
    "castanea crenata":     "クリ",
    "alnus japonica":       "ハンノキ",
    "zelkova serrata":      "ケヤキ",
    "cryptomeria japonica": "スギ（針葉樹）",
    "chamaecyparis obtusa": "ヒノキ（針葉樹）",
    "pinus densiflora":     "アカマツ（針葉樹）",
}


# ── ユーティリティ ────────────────────────────────────────────────────────

def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat, dlng = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def bearing(lat1, lng1, lat2, lng2):
    """出発地から対象への方位角（0=北、時計回り）"""
    dlng = math.radians(lng2 - lng1)
    lat1r, lat2r = math.radians(lat1), math.radians(lat2)
    x = math.sin(dlng) * math.cos(lat2r)
    y = math.cos(lat1r) * math.sin(lat2r) - math.sin(lat1r) * math.cos(lat2r) * math.cos(dlng)
    return (math.degrees(math.atan2(x, y)) + 360) % 360

DIRECTION_ANGLES = {
    "N": 0, "NE": 45, "E": 90, "SE": 135,
    "S": 180, "SW": 225, "W": 270, "NW": 315,
}

def in_sector(lat1, lng1, lat2, lng2, center_deg, half_deg=45):
    b = bearing(lat1, lng1, lat2, lng2)
    diff = abs((b - center_deg + 180) % 360 - 180)
    return diff <= half_deg

def get_sector_bbox(lat, lng, radius_km, center_deg, half_deg=45):
    """方向セクターを包含する最小外接bbox（全円bboxより大幅に小さい）"""
    R = 6371
    lats, lngs = [lat], [lng]
    for angle_deg in range(int(center_deg - half_deg), int(center_deg + half_deg) + 1, 5):
        b = math.radians(angle_deg % 360)
        d = radius_km / R
        lat1r = math.radians(lat)
        lat2r = math.asin(math.sin(lat1r)*math.cos(d) + math.cos(lat1r)*math.sin(d)*math.cos(b))
        lng2r = math.radians(lng) + math.atan2(
            math.sin(b)*math.sin(d)*math.cos(lat1r),
            math.cos(d) - math.sin(lat1r)*math.sin(lat2r)
        )
        lats.append(math.degrees(lat2r))
        lngs.append(math.degrees(lng2r))
    pad = 0.15
    return min(lats) - pad, min(lngs) - pad, max(lats) + pad, max(lngs) + pad

def make_grid_candidates(lat, lng, radius_km, dir_angle, step_km=20):
    """セクター内グリッド候補点。決定論的ジッターで等間隔外観を解消。"""
    step_lat = step_km / 111.0
    step_lng = step_km / (111.0 * math.cos(math.radians(lat)))
    n = math.ceil(radius_km / step_km)
    out = []
    for di in range(-n, n + 1):
        for dj in range(-n, n + 1):
            # 座標ハッシュで決定論的ジッター（±32% of step）
            h = int(hashlib.md5(f"{di},{dj}".encode()).hexdigest(), 16)
            jlat = ((h & 0xFFFF) / 65536.0 - 0.5) * 2 * 0.32 * step_lat
            jlng = ((h >> 16 & 0xFFFF) / 65536.0 - 0.5) * 2 * 0.32 * step_lng
            glat = round(lat + di * step_lat + jlat, 4)
            glng = round(lng + dj * step_lng + jlng, 4)
            dist = haversine(lat, lng, glat, glng)
            if dist < 20 or dist > radius_km:
                continue
            if dir_angle is not None and not in_sector(lat, lng, glat, glng, dir_angle):
                continue
            out.append({
                "lat": glat, "lng": glng,
                "dist_km": round(dist, 1),
                "name": "", "is_grid": True,
                "broadleaf": True, "bl_confirmed": False, "species": "",
            })
    return out

def get_bbox(lat, lng, radius_km):
    dlat = radius_km / 111.0
    dlng = radius_km / (111.0 * math.cos(math.radians(lat)))
    return lat - dlat, lng - dlng, lat + dlat, lng + dlng

def parse_species(tags):
    sp = (tags.get("species") or tags.get("species:ja") or "").strip()
    if sp:
        for key, val in SPECIES_JA.items():
            if key in sp.lower():
                return val
        return sp
    lt = tags.get("leaf_type", "")
    if lt == "broadleaved":  return "広葉樹林"
    if lt == "needleleaved": return "針葉樹林"
    if lt == "mixed":        return "混合林"
    return ""

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
]

def overpass(query, timeout=120):
    last_err = None
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            r = requests.post(endpoint, data={"data": query}, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json().get("elements", [])
        except Exception as e:
            last_err = e
            continue
    raise last_err

def get_elevation(lat, lng):
    """単点標高（Open-Topo-Data → GSI フォールバック）"""
    try:
        r = requests.get(
            "https://api.opentopodata.org/v1/srtm30m",
            params={"locations": f"{lat},{lng}"},
            timeout=10,
        )
        v = r.json().get("results", [{}])[0].get("elevation")
        return float(v) if v is not None else -1.0
    except Exception:
        pass
    try:
        url = f"https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php?lon={lng}&lat={lat}&outtype=JSON"
        r = requests.get(url, timeout=8)
        v = r.json().get("elevation")
        return float(v) if v is not None and v != "-----" else -1.0
    except Exception:
        return -1.0

def get_elevations_batch(spots):
    """バッチ標高取得（Open-Topo-Data 最大100点/リクエスト）。失敗時は単点フォールバック。"""
    out = {}
    chunks = [spots[i:i+100] for i in range(0, len(spots), 100)]
    for chunk in chunks:
        locs = "|".join(f"{s['lat']},{s['lng']}" for s in chunk)
        try:
            r = requests.get(
                "https://api.opentopodata.org/v1/srtm30m",
                params={"locations": locs},
                timeout=20,
            )
            for s, res in zip(chunk, r.json().get("results", [])):
                v = res.get("elevation")
                out[(s["lat"], s["lng"])] = float(v) if v is not None else -1.0
        except Exception:
            for s in chunk:
                out[(s["lat"], s["lng"])] = get_elevation(s["lat"], s["lng"])
    return out

def query_rivers(s, w, n, e):
    """bbox内の河川・水路の座標点リストを返す（Overpass）"""
    q = f"""
[out:json][timeout:55];
(
  way["waterway"~"^(river|stream|canal)$"]({s},{w},{n},{e});
)->.r;
.r out geom;
"""
    try:
        elements = overpass(q, timeout=65)
        pts = []
        for el in elements:
            for pt in (el.get("geometry") or []):
                if pt:
                    pts.append((float(pt["lat"]), float(pt["lon"])))
        return pts
    except Exception:
        return []

def fetch_zone_roads(lat, lng, radius_km=3.0):
    """道路・街灯データを取得してdictで返す（zone-roads APIと共用）"""
    s, w, n, e = get_bbox(lat, lng, radius_km)
    ROAD_Q = f"""
[out:json][timeout:22];
(
  way["highway"~"^(primary|secondary|tertiary|unclassified|residential)$"]({s},{w},{n},{e});
  node["highway"="street_lamp"]({s},{w},{n},{e});
)->.r;
.r out center tags;
"""
    try:
        els = overpass(ROAD_Q, 28)
    except Exception:
        return {"error": True, "road_count": 0, "lamp_count": 0, "road_summary": [], "actual_score": 0, "has_roads": False}

    road_counts = {}
    lamp_count = 0
    for el in els:
        tags = el.get("tags", {})
        hw = tags.get("highway", "")
        if hw == "street_lamp":
            lamp_count += 1
        elif hw in ("primary", "secondary", "tertiary", "unclassified", "residential"):
            road_counts[hw] = road_counts.get(hw, 0) + 1

    road_ja = {
        "primary": "国道", "secondary": "県道", "tertiary": "市町村道",
        "unclassified": "一般道", "residential": "生活道路",
    }
    road_summary = [f"{road_ja.get(k, k)}{v}本" for k, v in road_counts.items()]
    total_roads = sum(road_counts.values())
    actual_score = min(lamp_count * 5 + total_roads * 4, 100)
    return {
        "road_count": total_roads, "road_summary": road_summary,
        "lamp_count": lamp_count, "actual_score": actual_score,
        "has_roads": total_roads > 0, "road_counts": road_counts,
    }



def nearest_river_km(lat, lng, river_points):
    """最近接河川までの距離(km)。データなしの場合 None"""
    if not river_points:
        return None
    nearby = [(r, g) for r, g in river_points if abs(r - lat) < 0.2 and abs(g - lng) < 0.2]
    if not nearby:
        return None
    return min(haversine(lat, lng, r, g) for r, g in nearby)

# ── 気温乗数 ────────────────────────────────────────────────────────────────
# (最高温度閾値°C, 乗数)  →  temp <= 閾値の最初のエントリを採用
TEMP_FACTOR = {
    "miyama":    [(18, 1.15), (22, 1.10), (25, 1.00), (28, 0.80), (31, 0.60), (99, 0.50)],
    "akaashi":   [(18, 1.15), (22, 1.10), (25, 1.00), (28, 0.80), (31, 0.60), (99, 0.50)],
    "suji":      [(20, 1.08), (24, 1.05), (27, 1.00), (30, 0.85), (99, 0.70)],
    "okuwagata": [(22, 0.95), (25, 1.05), (28, 1.00), (31, 0.90), (99, 0.80)],
    "nokogiri":  [(23, 0.90), (26, 1.05), (29, 1.00), (32, 0.85), (99, 0.75)],
    "kokuwagata":[(22, 0.95), (25, 1.05), (28, 1.00), (31, 0.90), (99, 0.80)],
    "hirata":    [(24, 0.80), (27, 0.95), (30, 1.10), (33, 1.05), (99, 0.95)],
    "kabuto":    [(22, 0.75), (25, 0.90), (28, 1.05), (31, 1.12), (34, 1.00), (99, 0.85)],
}

def get_temp_factor(temp, species):
    if temp is None:
        return 1.0
    for threshold, factor in TEMP_FACTOR.get(species, []):
        if temp <= threshold:
            return factor
    return 1.0

# ── 河川近接ボーナス(0〜12pt) ─────────────────────────────────────────────
# (距離km閾値, ボーナス点)  →  river_dist <= 閾値の最初のエントリを採用
RIVER_BONUS = {
    "hirata":    [(0.5, 12), (1.0,  9), (2.0, 6), (5.0, 3), (99, 0)],
    "nokogiri":  [(1.0,  8), (2.0,  5), (5.0, 2), (99, 0)],
    "kokuwagata":[(1.0,  6), (2.0,  4), (5.0, 2), (99, 0)],
    "miyama":    [(1.0,  5), (3.0,  3), (6.0, 1), (99, 0)],
    "akaashi":   [(1.0,  5), (3.0,  3), (99, 0)],
    "okuwagata": [(2.0,  4), (5.0,  2), (99, 0)],
    "suji":      [(2.0,  3), (5.0,  1), (99, 0)],
    "kabuto":    [(1.0,  6), (3.0,  3), (5.0, 1), (99, 0)],
}

def get_river_bonus(river_dist_km, species):
    if river_dist_km is None:
        return 0
    for threshold, bonus in RIVER_BONUS.get(species, []):
        if river_dist_km <= threshold:
            return bonus
    return 0

# ── 種別スコア関数 ────────────────────────────────────────────────────────

def _obs_bonus(obs, key, tiers=(5, 2, 1)):
    # 上限を25→15に縮小。標高・植生の方が信頼性が高いため観察記録は補助的扱い。
    v = obs.get(key, 0)
    t = obs.get("total", 0)
    if v >= tiers[0]: return 15
    if v >= tiers[1]: return 10
    if v >= tiers[2]: return 6
    if t >= 5:        return 3
    if t >= 1:        return 1
    return 0

def score_miyama(elev, bl, obs):
    # 500〜1400m 冷涼山地広葉樹林 ★採集者視点で修正
    if   700 <= elev <= 1400: e = 58   # 最良帯：大型個体が期待できる
    elif 500 <= elev <   700: e = 42   # 好適帯：梅雨明け後〜7月に多い
    elif 1400 < elev <= 1800: e = 36   # 高標高：個体数は減るが超大型も
    elif 300 <= elev <   500: e = 24   # 可能帯：梅雨前線通過後の夜に出る
    elif 150 <= elev <   300: e = 10   # 低標高：稀に飛来
    else:                     e = 4    # 0-150m：ほぼ生息なし
    return min(e + (28 if bl else 10) + _obs_bonus(obs, "miyama"), 100)

def score_okuwagata(elev, bl, obs):
    # 100〜700m 低中山地 古木広葉樹林（希少）
    if   150 <= elev <=  700: e = 52
    elif  80 <= elev <   150 or 700 < elev <= 1000: e = 35
    elif   0 <  elev <    80: e = 20
    elif elev > 1000:         e = 12
    else:                     e = 10
    return min(e + (26 if bl else 10) + _obs_bonus(obs, "okuwagata", (3,2,1)), 100)

def score_nokogiri(elev, bl, obs):
    # 30〜800m 最もポピュラー ★里山〜低山が主戦場
    if    50 <= elev <=  700: e = 54
    elif   0 <  elev <    50: e = 44
    elif 700 < elev <= 1000:  e = 28
    elif elev > 1000:         e = 10
    else:                     e = 16
    return min(e + (24 if bl else 8) + _obs_bonus(obs, "nokogiri"), 100)

def score_kokuwagata(elev, bl, obs):
    # 0〜1000m 最も環境を選ばない ★全国どこでも
    if    0 <  elev <= 1000:  e = 50
    elif 1000 < elev <= 1500: e = 32
    elif elev > 1500:         e = 14
    else:                     e = 20
    return min(e + (24 if bl else 10) + _obs_bonus(obs, "kokuwagata"), 100)

def score_hirata(elev, bl, obs):
    # 0〜300m 平地・河川沿い ★河川ボーナスで真価発揮
    if    0 <  elev <=  200:  e = 54
    elif 200 <  elev <=  500: e = 34
    elif 500 <  elev <=  800: e = 16
    elif elev > 800:          e = 5
    else:                     e = 22
    return min(e + (22 if bl else 8) + _obs_bonus(obs, "hirata", (3,2,1)), 100)

def score_akaashi(elev, bl, obs):
    # 400〜1400m ミヤマ同様 冷涼山地
    if   600 <= elev <= 1400: e = 55
    elif 400 <= elev <   600: e = 38
    elif 1400 < elev <= 1800: e = 34
    elif 200 <= elev <   400: e = 18
    else:                     e = 5
    return min(e + (28 if bl else 10) + _obs_bonus(obs, "akaashi"), 100)

def score_suji(elev, bl, obs):
    # 300〜900m 中山地
    if   300 <= elev <=  900: e = 52
    elif 100 <= elev <   300 or 900 < elev <= 1300: e = 34
    elif   0 <  elev <   100: e = 16
    elif elev > 1300:         e = 10
    else:                     e = 12
    return min(e + (24 if bl else 10) + _obs_bonus(obs, "suji"), 100)

def score_kabuto(elev, bl, obs):
    # 30〜700m 低地〜中山地の広葉樹林（クヌギ・コナラの樹液）
    if    30 <= elev <=  700: e = 55
    elif   0 <  elev <    30: e = 42
    elif 700 < elev <= 1000:  e = 28
    elif elev > 1000:         e = 8
    else:                     e = 24
    return min(e + (24 if bl else 8) + _obs_bonus(obs, "kabuto"), 100)

# ── 季節補正 ─────────────────────────────────────────────────────────────────
def season_multiplier(month, species):
    """月別の採集活性補正。7-8月ピークを1.0基準とし、オフシーズンは大きく下げる。"""
    TABLE = {
        "miyama":    {1:.05,2:.05,3:.05,4:.15,5:.50,6:.85,7:1.25,8:1.10,9:.50,10:.15,11:.05,12:.05},
        "akaashi":   {1:.05,2:.05,3:.05,4:.15,5:.50,6:.85,7:1.25,8:1.10,9:.50,10:.15,11:.05,12:.05},
        "suji":      {1:.05,2:.05,3:.05,4:.15,5:.50,6:.85,7:1.20,8:1.05,9:.50,10:.15,11:.05,12:.05},
        "okuwagata": {1:.05,2:.05,3:.05,4:.20,5:.60,6:.90,7:1.20,8:1.15,9:.80,10:.30,11:.05,12:.05},
        "nokogiri":  {1:.05,2:.05,3:.05,4:.20,5:.55,6:.85,7:1.20,8:1.25,9:1.00,10:.40,11:.05,12:.05},
        "kokuwagata":{1:.05,2:.05,3:.05,4:.20,5:.55,6:.85,7:1.10,8:1.15,9:1.00,10:.50,11:.05,12:.05},
        "hirata":    {1:.05,2:.05,3:.05,4:.15,5:.45,6:.75,7:1.05,8:1.20,9:1.00,10:.60,11:.10,12:.05},
        "kabuto":    {1:.05,2:.05,3:.05,4:.10,5:.40,6:.75,7:1.15,8:1.20,9:.80,10:.25,11:.05,12:.05},
    }
    default = {1:.05,2:.05,3:.05,4:.2,5:.5,6:.8,7:1.0,8:1.0,9:.7,10:.3,11:.05,12:.05}
    return TABLE.get(species, default).get(month, default.get(month, 0.1))

SCORERS = {
    "miyama":     score_miyama,
    "okuwagata":  score_okuwagata,
    "nokogiri":   score_nokogiri,
    "kokuwagata": score_kokuwagata,
    "hirata":     score_hirata,
    "akaashi":    score_akaashi,
    "suji":       score_suji,
    "kabuto":     score_kabuto,
}

def all_final_scores(elev, bl, obs, temp, river_dist_km, month=None):
    """季節補正・気温乗数・河川ボーナス込みの最終スコアを全種分計算"""
    scores = {}
    for sp, fn in SCORERS.items():
        base = fn(elev, bl, obs)
        tf   = get_temp_factor(temp, sp)
        rb   = get_river_bonus(river_dist_km, sp)
        sm   = season_multiplier(month, sp) if month else 1.0
        scores[sp] = min(round(base * tf * sm) + rb, 100)
    return scores

def score_light_trap(elev, broadleaf, river_dist_km):
    """ライト採集ポテンシャル: 暗い山地・広葉樹林・水辺が理想"""
    if   700 <= elev <= 1500: e = 55
    elif 400 <= elev <  700 or 1500 < elev <= 2000: e = 38
    elif 200 <= elev <  400: e = 20
    elif   0 <  elev <  200: e = 8
    else:                     e = 18  # 不明
    bl = 25 if broadleaf else 8
    rv = 0
    if river_dist_km is not None:
        if   river_dist_km <= 1.0: rv = 12
        elif river_dist_km <= 3.0: rv = 8
        elif river_dist_km <= 6.0: rv = 3
    return min(e + bl + rv, 100)

def score_street_heuristic(elev, river_dist_km, dist_km):
    """街灯採集ポテンシャル(初期推定): 低標高・河川沿い道路が理想。選択後OSMで補正。"""
    if   150 <= elev <= 500: e = 52  # 農村部の国道・県道沿いが最適
    elif   0 <  elev <  150: e = 35  # 市街地に近すぎる
    elif 500 <  elev <= 800: e = 38
    elif 800 <  elev <= 1200: e = 18
    elif elev > 1200:         e = 5
    else:                     e = 30  # 不明
    rv = 0
    if river_dist_km is not None:
        if   river_dist_km <= 1.0: rv = 18  # 河川沿いに幹線道路が集まる
        elif river_dist_km <= 2.0: rv = 12
        elif river_dist_km <= 4.0: rv = 6
    dist_b = 8 if 25 <= dist_km <= 100 else 4 if dist_km <= 150 else 0
    return min(e + rv + dist_b, 100)

# ── 月齢・気象コンディション ─────────────────────────────────────────────

def moon_phase_age(date=None):
    """指定日（またはデフォルト今日）の月齢（0=新月、14.77=満月、29.53=周期）"""
    if date is None:
        date = datetime.date.today()
    elif isinstance(date, str):
        date = datetime.date.fromisoformat(date)
    known_new = datetime.date(2000, 1, 6)
    return (date - known_new).days % 29.53058867

def moon_emoji(age):
    return ["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"][int(age / 29.53 * 8) % 8]

def moon_phase_label(age):
    if age < 1.5 or age > 28: return "新月"
    if age < 6:                return "三日月"
    if age < 8.5:              return "上弦"
    if age < 13:               return "十三夜"
    if age < 16:               return "満月"
    if age < 21:               return "十六夜"
    if age < 23.5:             return "下弦"
    return "晦日月"

def moon_collecting_factor(age, method="light"):
    """月明かりによる採集補正。新月に近いほどライト採集向き。"""
    dist = min(age, 29.53 - age)  # 新月からの距離（日数）
    if method == "light":
        if dist <= 1.5: return 1.40
        if dist <= 3.5: return 1.25
        if dist <= 6.0: return 1.10
        if dist <= 9.0: return 0.88
        if dist <= 12:  return 0.68
        return 0.52  # 満月付近
    if method == "street":
        # 街灯は人工光が強く月明かりの影響が小さい
        if dist <= 3:  return 1.12
        if dist <= 8:  return 1.04
        if dist <= 12: return 0.92
        return 0.85
    return 1.0  # tree採集は月齢に依存しない

def get_forecast_weather(lat, lng, target_date=None):
    """Open-Meteo: 指定日22時の気温・湿度・雲量（14日以内の予報のみ取得可）"""
    if target_date is None:
        target_date = datetime.date.today()
    elif isinstance(target_date, str):
        target_date = datetime.date.fromisoformat(target_date)
    days_ahead = (target_date - datetime.date.today()).days
    if days_ahead < 0 or days_ahead > 14:
        return None  # 過去日または14日超は予報取得不可
    date_str = target_date.isoformat()
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat, "longitude": lng,
                "hourly": "temperature_2m,relative_humidity_2m,cloud_cover",
                "timezone": "Asia/Tokyo",
                "start_date": date_str, "end_date": date_str,
            },
            timeout=12,
        )
        data = r.json()
        times = data["hourly"]["time"]
        idx = next((i for i, t in enumerate(times) if t.endswith("T22:00")), 22)
        return {
            "temp":     round(data["hourly"]["temperature_2m"][idx], 1),
            "humidity": data["hourly"]["relative_humidity_2m"][idx],
            "cloud":    data["hourly"]["cloud_cover"][idx],
        }
    except Exception:
        return None

def build_conditions(lat, lng, weather=None, date=None):
    """月齢＋気象を統合したコンディション辞書を返す"""
    if date is None:
        date = datetime.date.today().isoformat()
    age = moon_phase_age(date)
    if weather is None:
        weather = get_forecast_weather(lat, lng, target_date=date)
    moon_f = moon_collecting_factor(age, "light")

    # 総合グレード（ライト採集基準）
    score = round(moon_f * 55)
    if weather:
        hum_b   = 12 if weather["humidity"] >= 75 else 6 if weather["humidity"] >= 60 else 0
        cloud_b = 8  if weather["cloud"]    <= 25 else -5 if weather["cloud"] >= 80 else 0
        score   = min(score + hum_b + cloud_b, 100)
    grade = "S" if score >= 80 else "A" if score >= 65 else "B" if score >= 50 else "C" if score >= 35 else "D"

    return {
        "moon_age":    round(age, 1),
        "moon_emoji":  moon_emoji(age),
        "moon_label":  moon_phase_label(age),
        "moon_factor": {
            "light":  round(moon_collecting_factor(age, "light"),  2),
            "street": round(moon_collecting_factor(age, "street"), 2),
            "tree":   1.0,
        },
        "weather": weather,
        "grade":   grade,
        "grade_score": score,
        "date": date if date else datetime.date.today().isoformat(),
    }

# ── SSE ──────────────────────────────────────────────────────────────────

def sse(data):
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

# ── ルート ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", default_lat=DEFAULT_LAT, default_lng=DEFAULT_LNG)


@app.route("/guide")
def guide():
    return render_template("guide.html")


@app.route("/guide/beginners")
def guide_beginners():
    return render_template("guide_beginners.html")


@app.route("/guide/miyama")
def guide_miyama():
    return render_template("guide_miyama.html")


@app.route("/guide/ookuwa")
def guide_ookuwa():
    return render_template("guide_ookuwa.html")


@app.route("/guide/tools")
def guide_tools():
    return render_template("guide_tools.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/sitemap.xml")
def sitemap():
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://beetle-finder.onrender.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/guide</loc>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/guide/beginners</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/guide/miyama</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/guide/ookuwa</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/guide/tools</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/about</loc>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
  <url>
    <loc>https://beetle-finder.onrender.com/privacy</loc>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
</urlset>'''
    return Response(xml, mimetype="application/xml")


@app.route("/api/geocode")
def geocode():
    addr = request.args.get("address", "").strip()
    if not addr:
        return jsonify({"error": "住所を入力してください"}), 400
    try:
        r = requests.get("https://nominatim.openstreetmap.org/search",
                         params={"q": addr, "format": "json", "limit": 1, "accept-language": "ja"},
                         headers=HEADERS, timeout=10)
        hits = r.json()
        if not hits:
            return jsonify({"error": f"「{addr}」が見つかりませんでした"}), 404
        h = hits[0]
        return jsonify({"lat": float(h["lat"]), "lng": float(h["lon"]), "display_name": h["display_name"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/spots")
def spots_stream():
    lat       = float(request.args.get("lat",   DEFAULT_LAT))
    lng       = float(request.args.get("lng",   DEFAULT_LNG))
    hours     = float(request.args.get("hours", 3))
    direction = request.args.get("direction", "all")
    plan_date = request.args.get("date", None)   # YYYY-MM-DD、省略時は今日
    radius    = min(hours * KM_PER_HOUR, MAX_RADIUS)
    dir_angle = DIRECTION_ANGLES.get(direction)  # None = 全方向

    step_km   = 18 if dir_angle is not None else 20
    max_zones = 45 if dir_angle is not None else 40
    dedup_km  = 6.0 if dir_angle is not None else 7.0

    def generate():
        try:
            dir_label = {"N":"北","NE":"北東","E":"東","SE":"南東","S":"南","SW":"南西","W":"西","NW":"北西"}.get(direction, "全方向")
            yield sse({"status": "progress", "message": f"河川データ取得中（半径約{int(radius)}km・{dir_label}方向）...", "pct": 10})

            s, w, n, e = get_bbox(lat, lng, radius)
            if dir_angle is not None:
                qs, qw, qn, qe = get_sector_bbox(lat, lng, radius, dir_angle)
            else:
                qs, qw, qn, qe = s, w, n, e

            river_pts = query_rivers(qs, qw, qn, qe)

            yield sse({"status": "progress", "message": "探索推奨ゾーンスキャン中（標高ベース分析）...", "pct": 30})

            grid_pts = make_grid_candidates(lat, lng, radius, dir_angle, step_km=step_km)

            yield sse({"status": "progress", "message": f"グリッド候補 {len(grid_pts)} 点の標高取得・今夜の気象データ取得中...", "pct": 50})

            dummy = {"total": 0, **{sp: 0 for sp in SCORERS}}
            zones = []
            tonight_weather = None
            if grid_pts:
                grid_elev_map   = get_elevations_batch(grid_pts)
                tonight_weather = get_forecast_weather(lat, lng, plan_date)
                plan_month = None
                if plan_date:
                    try:
                        plan_month = datetime.date.fromisoformat(plan_date).month
                    except Exception:
                        plan_month = datetime.date.today().month
                else:
                    plan_month = datetime.date.today().month

                for gp in grid_pts:
                    gp["elevation"]     = grid_elev_map.get((gp["lat"], gp["lng"]), -1.0)
                    gp["river_dist_km"] = nearest_river_km(gp["lat"], gp["lng"], river_pts)
                    e_val = gp["elevation"]
                    # broadleaf: 標高80m以上は広葉樹林の可能性が高い（日本の里山）
                    gp["broadleaf"] = (80 < e_val < 1800) if e_val > 0 else True
                    gp["obs"]  = dummy
                    gp["temp"] = None
                    gp.update(all_final_scores(gp["elevation"], gp["broadleaf"], dummy, None, gp["river_dist_km"], month=plan_month))
                    gp["m_light"]  = score_light_trap(gp["elevation"], gp["broadleaf"], gp["river_dist_km"])
                    gp["m_street"] = score_street_heuristic(gp["elevation"], gp["river_dist_km"], gp["dist_km"])
                grid_sorted = sorted(grid_pts, key=lambda x: max(x[sp] for sp in SCORERS), reverse=True)
                for gp in grid_sorted:
                    if all(haversine(gp["lat"], gp["lng"], z["lat"], z["lng"]) >= dedup_km for z in zones):
                        zones.append(gp)
                    if len(zones) >= max_zones:
                        break

            yield sse({"status": "progress", "message": "完了間近...", "pct": 95})

            zone_result = [{
                "lat":           z["lat"], "lng": z["lng"],
                "dist_km":       z["dist_km"],
                "elevation":     round(z["elevation"]) if z["elevation"] > 0 else None,
                "broadleaf":     z["broadleaf"],
                "river_dist_km": round(z["river_dist_km"], 1) if z.get("river_dist_km") is not None else None,
                "m_light":       z["m_light"],
                "m_street":      z["m_street"],
                **{sp: z[sp] for sp in SCORERS},
            } for z in zones]

            conditions = build_conditions(lat, lng, weather=tonight_weather, date=plan_date)
            yield sse({"status": "done", "spots": [], "zones": zone_result,
                       "direction": direction, "conditions": conditions, "pct": 100})
        except Exception as exc:
            yield sse({"status": "error", "message": str(exc)})

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/light-spots")
def light_spots():
    lat    = float(request.args.get("lat",   DEFAULT_LAT))
    lng    = float(request.args.get("lng",   DEFAULT_LNG))
    hours  = float(request.args.get("hours", 3))
    radius = min(hours * KM_PER_HOUR, MAX_RADIUS)
    s, w, n, e = get_bbox(lat, lng, radius)

    # 名前付き駐車場・キャンプ場・ダム・水辺のみ取得（1クエリで完結）
    PARK_Q = f"""
[out:json][timeout:25];
(
  node["amenity"="parking"]["name"]["access"!="private"]({s},{w},{n},{e});
  way["amenity"="parking"]["name"]["access"!="private"]({s},{w},{n},{e});
  node["tourism"="camp_site"]({s},{w},{n},{e});
  way["tourism"="camp_site"]({s},{w},{n},{e});
  node["waterway"="dam"]({s},{w},{n},{e});
  way["waterway"="dam"]({s},{w},{n},{e});
  node["man_made"="dam"]({s},{w},{n},{e});
  way["man_made"="dam"]({s},{w},{n},{e});
  node["natural"="water"]["name"]({s},{w},{n},{e});
  way["natural"="water"]["name"]({s},{w},{n},{e});
)->.p;
.p out center tags;
"""
    TYPE = {
        "parking":   ("駐車場",    "P",  "#ffc107"),
        "camp_site": ("キャンプ場", "⛺", "#4caf50"),
        "dam":       ("ダム",      "🏞", "#1565c0"),
        "water":     ("水辺",     "💧", "#26c6da"),
    }

    try:
        parks = overpass(PARK_Q, 35)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    result = []
    for el in parks:
        c = el.get("center") or {}
        elat = float(c.get("lat") or el.get("lat") or 0)
        elng = float(c.get("lon") or el.get("lon") or 0)
        if not elat or not elng:
            continue
        dist = haversine(lat, lng, elat, elng)
        if dist > radius:
            continue
        tags = el.get("tags", {})
        t = tags.get("tourism", ""); w_ = tags.get("waterway", ""); m = tags.get("man_made", ""); n_ = tags.get("natural", "")
        if t == "camp_site":            stype = "camp_site"
        elif w_ == "dam" or m == "dam": stype = "dam"
        elif n_ == "water":             stype = "water"
        else:                           stype = "parking"

        label, icon, color = TYPE[stype]
        result.append({
            "lat": elat, "lng": elng, "name": tags.get("name", ""),
            "type": stype, "type_label": label, "icon": icon, "color": color,
            "dist_km": round(dist, 1),
            "capacity": tags.get("capacity", ""), "fee": tags.get("fee", ""),
        })

    # キャンプ場・ダム・水辺を優先、駐車場は後回し、各カテゴリ内で距離順、上位30件
    priority = {"camp_site": 0, "dam": 1, "water": 2, "parking": 3}
    result.sort(key=lambda x: (priority[x["type"]], x["dist_km"]))
    result = result[:30]
    return jsonify({"spots": result, "total": len(result)})




@app.route("/api/conditions")
def conditions_api():
    """指定日のコンディション（月齢＋気象）を返す。dateはYYYY-MM-DD形式。"""
    lat  = float(request.args.get("lat",  DEFAULT_LAT))
    lng  = float(request.args.get("lng",  DEFAULT_LNG))
    date = request.args.get("date", None)  # YYYY-MM-DD、省略時は今日
    return jsonify(build_conditions(lat, lng, date=date))


@app.route("/api/zone-roads")
def zone_roads():
    """街灯採集用: ゾーン選択時に3km圏の道路・街灯を取得（遅延ロード）"""
    lat = float(request.args.get("lat"))
    lng = float(request.args.get("lng"))
    try:
        data = fetch_zone_roads(lat, lng, radius_km=3.0)
        if data.get("error"):
            return jsonify({"error": "Overpass取得失敗"}), 500
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500




if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=port)
