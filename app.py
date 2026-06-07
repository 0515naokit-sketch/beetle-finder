import sys
sys.setrecursionlimit(10000)   # gevent + SSL ハンドシェイクの深い再帰に対応

from flask import Flask, render_template, Response, jsonify, request, stream_with_context, abort, redirect
from pref_data import PREF_DATA as PREF_GUIDE_DATA
import requests
from requests.adapters import HTTPAdapter
import math
import json
import hashlib
import datetime

app = Flask(__name__)

# gevent 環境での requests セッション（接続プールを無効化してSSL再帰を回避）
_session = requests.Session()
_adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1, max_retries=0)
_session.mount("https://", _adapter)
_session.mount("http://",  _adapter)

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
            r = _session.post(endpoint, data={"data": query}, headers=HEADERS, timeout=timeout)
            r.raise_for_status()
            return r.json().get("elements", [])
        except Exception as e:
            last_err = e
            continue
    raise last_err

def get_elevation(lat, lng):
    """単点標高（Open-Topo-Data → GSI フォールバック）"""
    try:
        r = _session.get(
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
        r = _session.get(url, timeout=8)
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
            r = _session.get(
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
        r = _session.get(
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
def landing():
    return render_template("landing.html")

@app.route("/app")
def index():
    return render_template("index.html", default_lat=DEFAULT_LAT, default_lng=DEFAULT_LNG)


@app.route("/guide")
def guide():
    return render_template("guide.html")


@app.route("/guide/reports")
def guide_reports():
    return render_template("guide_reports.html")


@app.route("/guide/experiences")
def guide_experiences():
    return render_template("guide_experiences.html")


@app.route("/guide/manner")
def guide_manner():
    return render_template("guide_manner.html")


@app.route("/guide/report/okutama")
def report_okutama():
    return render_template("report_okutama.html")


@app.route("/guide/report/chichibu")
def report_chichibu():
    return render_template("report_chichibu.html")


@app.route("/guide/report/takao")
def report_takao():
    return render_template("report_takao.html")


@app.route("/guide/report/tsukuba")
def report_tsukuba():
    return render_template("report_tsukuba.html")


@app.route("/guide/scoring")
def guide_scoring():
    return render_template("guide_scoring.html")


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


@app.route("/guide/beginner-kit")
def guide_beginner_kit():
    return render_template("guide_beginner_kit.html")


@app.route("/guide/nokogiri")
def guide_nokogiri():
    return render_template("guide_nokogiri.html")


@app.route("/guide/hirata")
def guide_hirata():
    return render_template("guide_hirata.html")


@app.route("/guide/kabuto")
def guide_kabuto():
    return render_template("guide_kabuto.html")


@app.route("/guide/kids")
def guide_kids():
    return render_template("guide_kids.html")


@app.route("/guide/light")
def guide_light():
    return render_template("guide_light.html")


@app.route("/guide/night")
def guide_night():
    return render_template("guide_night.html")


@app.route("/guide/trap")
def guide_trap():
    return render_template("guide_trap.html")


@app.route("/guide/calendar")
def guide_calendar():
    return render_template("guide_calendar.html")


@app.route("/guide/breeding")
def guide_breeding():
    return render_template("guide_breeding.html")


@app.route("/guide/larva")
def guide_larva():
    return render_template("guide_larva.html")


@app.route("/guide/jelly")
def guide_jelly():
    return render_template("guide_jelly.html")


@app.route("/guide/zaiwari")
def guide_zaiwari():
    return render_template("guide_zaiwari.html")


@app.route("/guide/iku/<species>")
def guide_iku(species):
    valid = ["kokuwagata", "nokogiri", "miyama", "hirata", "ookuwa", "akaashi"]
    if species not in valid:
        from flask import abort
        abort(404)
    return render_template(f"guide_iku_{species}.html")


@app.route("/guide/case")
def guide_case():
    return render_template("guide_case.html")


@app.route("/guide/aftercare")
def guide_aftercare():
    return render_template("guide_aftercare.html")


@app.route("/guide/may")
def guide_may():
    return render_template("guide_may.html")


@app.route("/guide/june")
def guide_june():
    return render_template("guide_june.html")


@app.route("/guide/july")
def guide_july():
    return render_template("guide_july.html")


@app.route("/guide/august")
def guide_august():
    return render_template("guide_august.html")


@app.route("/guide/september")
def guide_september():
    return render_template("guide_september.html")


@app.route("/guide/october")
def guide_october():
    return render_template("guide_october.html")


@app.route("/guide/overwinter")
def guide_overwinter():
    return render_template("guide_overwinter.html")


@app.route("/guide/november")
def guide_november():
    return render_template("guide_november.html")


@app.route("/guide/spring")
def guide_spring():
    return render_template("guide_spring.html")


SPOT_DATA = {
    # 北海道・東北
    "hokkaido":  {"name": "北海道",   "alt": "道内各山地",             "elev": "0〜800m",    "species": "ミヤマ・ノコギリ・コクワ",         "spots": "道南・道央の雑木林",               "best_month": "7〜8月"},
    "aomori":    {"name": "青森県",   "alt": "八甲田山・白神山地",     "elev": "200〜1200m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "八甲田・白神・下北半島周辺",       "best_month": "7月"},
    "iwate":     {"name": "岩手県",   "alt": "早池峰山・奥羽山脈",     "elev": "200〜1200m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "花巻・遠野・八幡平周辺",           "best_month": "7月"},
    "miyagi":    {"name": "宮城県",   "alt": "蔵王山・船形山",         "elev": "200〜1000m", "species": "ミヤマ・ノコギリ・コクワ",         "spots": "蔵王・七ヶ宿・気仙沼周辺",         "best_month": "7〜8月"},
    "akita":     {"name": "秋田県",   "alt": "奥羽山脈・白神山地",     "elev": "200〜1500m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "田沢湖・角館・男鹿周辺",           "best_month": "7月"},
    "yamagata":  {"name": "山形県",   "alt": "月山・蔵王・飯豊連峰",   "elev": "200〜1400m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "月山麓・米沢・上山周辺",           "best_month": "7月"},
    "fukushima": {"name": "福島県",   "alt": "奥羽山脈・阿武隈山地",   "elev": "200〜1500m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "裏磐梯・南会津・那須周辺",         "best_month": "7〜8月"},
    # 関東
    "ibaraki":   {"name": "茨城県",   "alt": "筑波山・八溝山地",       "elev": "0〜800m",    "species": "ノコギリ・コクワ・ヒラタ",         "spots": "筑波山・奥久慈・大子周辺",         "best_month": "7〜8月"},
    "tochigi":   {"name": "栃木県",   "alt": "日光・那須・足尾山地",   "elev": "200〜1500m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "日光・那須・矢板周辺",             "best_month": "7月"},
    "gunma":     {"name": "群馬県",   "alt": "赤城山・榛名山・上信越", "elev": "200〜1500m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "赤城山・榛名山・みなかみ周辺",     "best_month": "7月"},
    "saitama":   {"name": "埼玉県",   "alt": "奥武蔵・秩父",           "elev": "100〜1000m", "species": "ノコギリ・コクワ・ミヤマ",         "spots": "秩父・飯能・越生",                 "best_month": "7〜8月"},
    "chiba":     {"name": "千葉県",   "alt": "房総丘陵",               "elev": "0〜300m",    "species": "ノコギリ・コクワ・カブトムシ",     "spots": "君津・鴨川・市原",                 "best_month": "7〜8月"},
    "tokyo":     {"name": "東京都",   "alt": "奥多摩・高尾山",         "elev": "200〜1000m", "species": "ノコギリ・コクワ・ヒラタ",         "spots": "奥多摩・高尾山・青梅",             "best_month": "7〜8月"},
    "kanagawa":  {"name": "神奈川県", "alt": "丹沢山地",               "elev": "200〜1500m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "丹沢・相模川沿い・宮ヶ瀬",         "best_month": "7月"},
    # 中部
    "niigata":   {"name": "新潟県",   "alt": "越後山脈・妙高山",       "elev": "200〜1500m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "妙高・糸魚川・魚沼周辺",           "best_month": "7月"},
    "toyama":    {"name": "富山県",   "alt": "立山・北アルプス",       "elev": "300〜1800m", "species": "ミヤマ・アカアシ・ノコギリ",       "spots": "立山山麓・朝日・魚津周辺",         "best_month": "7月"},
    "ishikawa":  {"name": "石川県",   "alt": "白山・能登半島",         "elev": "200〜1200m", "species": "ノコギリ・コクワ・ミヤマ",         "spots": "白山麓・加賀・能登周辺",           "best_month": "7〜8月"},
    "fukui":     {"name": "福井県",   "alt": "越前山地・若狭",         "elev": "200〜900m",  "species": "ノコギリ・ヒラタ・コクワ",         "spots": "越前・若狭・大野周辺",             "best_month": "7〜8月"},
    "yamanashi": {"name": "山梨県",   "alt": "富士山麓・南アルプス",   "elev": "400〜1800m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "富士五湖周辺・昇仙峡・甲府盆地縁", "best_month": "7月"},
    "nagano":    {"name": "長野県",   "alt": "日本アルプス周辺",       "elev": "500〜1800m", "species": "ミヤマ・アカアシ・ノコギリ",       "spots": "伊那谷・安曇野・上高地周辺",       "best_month": "7月"},
    "gifu":      {"name": "岐阜県",   "alt": "飛騨山脈・木曽山脈",     "elev": "300〜1800m", "species": "ミヤマ・アカアシ・ノコギリ",       "spots": "飛騨高山・郡上・下呂周辺",         "best_month": "7月"},
    "shizuoka":  {"name": "静岡県",   "alt": "南アルプス・天城山",     "elev": "200〜1800m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "天城山・寸又峡・井川周辺",         "best_month": "7〜8月"},
    "aichi":     {"name": "愛知県",   "alt": "三河山地・設楽",         "elev": "100〜1000m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "設楽・豊田・新城",                 "best_month": "7〜8月"},
    "mie":       {"name": "三重県",   "alt": "大台ケ原・紀伊山地",     "elev": "200〜1500m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "大台ケ原・熊野・宮川周辺",         "best_month": "7〜8月"},
    # 近畿
    "shiga":     {"name": "滋賀県",   "alt": "比良山系・鈴鹿山脈",     "elev": "200〜1200m", "species": "ノコギリ・ミヤマ・コクワ",         "spots": "比良山・伊吹山・朽木周辺",         "best_month": "7〜8月"},
    "kyoto":     {"name": "京都府",   "alt": "丹波高地・北山",         "elev": "200〜900m",  "species": "ノコギリ・コクワ・ヒラタ",         "spots": "美山・京都北山・綾部周辺",         "best_month": "7〜8月"},
    "osaka":     {"name": "大阪府",   "alt": "金剛山・北摂",           "elev": "100〜1100m", "species": "ノコギリ・ヒラタ・コクワ",         "spots": "金剛山・能勢・箕面",               "best_month": "7〜8月"},
    "hyogo":     {"name": "兵庫県",   "alt": "六甲山・氷ノ山",         "elev": "200〜1500m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "氷ノ山・丹波・篠山周辺",           "best_month": "7〜8月"},
    "nara":      {"name": "奈良県",   "alt": "大台ケ原・吉野山地",     "elev": "300〜1700m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "吉野・大台ケ原・天川周辺",         "best_month": "7月"},
    "wakayama":  {"name": "和歌山県", "alt": "紀伊山地",               "elev": "200〜1300m", "species": "ノコギリ・ヒラタ・コクワ",         "spots": "護摩壇山・龍神・熊野周辺",         "best_month": "7〜8月"},
    # 中国
    "tottori":   {"name": "鳥取県",   "alt": "大山・中国山地",         "elev": "200〜1700m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "大山・智頭・日野周辺",             "best_month": "7月"},
    "shimane":   {"name": "島根県",   "alt": "中国山地・三瓶山",       "elev": "200〜1200m", "species": "ノコギリ・ミヤマ・コクワ",         "spots": "三瓶山・奥出雲・益田周辺",         "best_month": "7〜8月"},
    "okayama":   {"name": "岡山県",   "alt": "中国山地・蒜山",         "elev": "200〜1200m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "蒜山・津山・新見周辺",             "best_month": "7〜8月"},
    "hiroshima": {"name": "広島県",   "alt": "中国山地・冠山",         "elev": "200〜1300m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "三段峡・庄原・三次周辺",           "best_month": "7〜8月"},
    "yamaguchi": {"name": "山口県",   "alt": "西中国山地",             "elev": "200〜1000m", "species": "ノコギリ・ヒラタ・コクワ",         "spots": "秋吉台・山口・岩国周辺",           "best_month": "7〜8月"},
    # 四国
    "tokushima": {"name": "徳島県",   "alt": "剣山・四国山地",         "elev": "300〜1900m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "剣山・祖谷・那賀周辺",             "best_month": "7月"},
    "kagawa":    {"name": "香川県",   "alt": "讃岐山脈",               "elev": "200〜800m",  "species": "ノコギリ・コクワ・ヒラタ",         "spots": "五色台・琴平・小豆島周辺",         "best_month": "7〜8月"},
    "ehime":     {"name": "愛媛県",   "alt": "石鎚山・四国山地",       "elev": "300〜1900m", "species": "ミヤマ・ノコギリ・アカアシ",       "spots": "石鎚山・久万高原・宇和島周辺",     "best_month": "7月"},
    "kochi":     {"name": "高知県",   "alt": "四国山地・剣山地",       "elev": "300〜1900m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "四万十・嶺北・土佐山周辺",         "best_month": "7〜8月"},
    # 九州
    "fukuoka":   {"name": "福岡県",   "alt": "英彦山・脊振山地",       "elev": "200〜1200m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "英彦山・脊振山・宝満山",           "best_month": "7月"},
    "saga":      {"name": "佐賀県",   "alt": "脊振山地・天山",         "elev": "200〜1000m", "species": "ノコギリ・ヒラタ・コクワ",         "spots": "脊振山・天山・唐津周辺",           "best_month": "7〜8月"},
    "nagasaki":  {"name": "長崎県",   "alt": "多良山系・雲仙",         "elev": "200〜1400m", "species": "ノコギリ・ヒラタ・コクワ",         "spots": "雲仙・対馬・五島周辺",             "best_month": "7〜8月"},
    "kumamoto":  {"name": "熊本県",   "alt": "阿蘇山・九州山地",       "elev": "200〜1500m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "阿蘇・五木・球磨周辺",             "best_month": "7〜8月"},
    "oita":      {"name": "大分県",   "alt": "くじゅう連山・九州山地", "elev": "300〜1700m", "species": "ミヤマ・ノコギリ・ヒラタ",         "spots": "くじゅう・由布院・日田周辺",       "best_month": "7月"},
    "miyazaki":  {"name": "宮崎県",   "alt": "九州山地・霧島",         "elev": "200〜1700m", "species": "ノコギリ・ヒラタ・ミヤマ",         "spots": "椎葉・綾・高千穂周辺",             "best_month": "7〜8月"},
    "kagoshima": {"name": "鹿児島県", "alt": "霧島山・大隅山地",       "elev": "200〜1700m", "species": "ノコギリ・ヒラタ・コクワ",         "spots": "霧島・屋久島・大隅周辺",           "best_month": "7〜8月"},
    "okinawa":   {"name": "沖縄県",   "alt": "沖縄本島北部・やんばる", "elev": "0〜500m",    "species": "ノコギリ・コクワ（琉球亜種）",     "spots": "やんばる・名護・国頭周辺",         "best_month": "6〜9月"},
}


@app.route("/guide/kokuwagata")
def guide_kokuwagata():
    return render_template("guide_kokuwagata.html")


@app.route("/guide/akaashi")
def guide_akaashi():
    return render_template("guide_akaashi.html")


@app.route("/guide/suji")
def guide_suji():
    return render_template("guide_suji.html")


@app.route("/guide/jiyukenkyu")
def guide_jiyukenkyu():
    return render_template("guide_jiyukenkyu.html")


@app.route("/guide/jiyukenkyu-kabuto")
def guide_jiyukenkyu_kabuto():
    return render_template("guide_jiyukenkyu_kabuto.html")


@app.route("/guide/tree")
def guide_tree():
    return render_template("guide_tree.html")


@app.route("/guide/morning")
def guide_morning():
    return render_template("guide_morning.html")


@app.route("/guide/rain")
def guide_rain():
    return render_template("guide_rain.html")


@app.route("/guide/spot/<pref>")
def guide_spot(pref):
    # /guide/pref/<pref> に統一（重複コンテンツ解消）
    if pref in SPOT_DATA:
        return redirect(f"/guide/pref/{pref}", 301)
    abort(404)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ── 都道府県別ガイド ──────────────────────────────────────────
@app.route("/guide/pref")
def guide_pref_index():
    return render_template("guide_pref_index.html")


@app.route("/guide/pref/tokyo")
def guide_pref_tokyo():
    return render_template("guide_pref_tokyo.html")

@app.route("/guide/pref/kanagawa")
def guide_pref_kanagawa():
    return render_template("guide_pref_kanagawa.html")

@app.route("/guide/pref/saitama")
def guide_pref_saitama():
    return render_template("guide_pref_saitama.html")

@app.route("/guide/pref/chiba")
def guide_pref_chiba():
    return render_template("guide_pref_chiba.html")

@app.route("/guide/pref/osaka")
def guide_pref_osaka():
    return render_template("guide_pref_osaka.html")

@app.route("/guide/pref/aichi")
def guide_pref_aichi():
    return render_template("guide_pref_aichi.html")

@app.route("/guide/pref/hyogo")
def guide_pref_hyogo():
    return render_template("guide_pref_hyogo.html")

@app.route("/guide/pref/fukuoka")
def guide_pref_fukuoka():
    return render_template("guide_pref_fukuoka.html")

@app.route("/guide/pref/hokkaido")
def guide_pref_hokkaido():
    return render_template("guide_pref_hokkaido.html")

@app.route("/guide/pref/shizuoka")
def guide_pref_shizuoka():
    return render_template("guide_pref_shizuoka.html")

@app.route("/guide/pref/nagano")
def guide_pref_nagano():
    return render_template("guide_pref_nagano.html")

@app.route("/guide/pref/hiroshima")
def guide_pref_hiroshima():
    return render_template("guide_pref_hiroshima.html")

@app.route("/guide/pref/miyagi")
def guide_pref_miyagi():
    return render_template("guide_pref_miyagi.html")

@app.route("/guide/pref/tochigi")
def guide_pref_tochigi():
    return render_template("guide_pref_tochigi.html")

@app.route("/guide/pref/gunma")
def guide_pref_gunma():
    return render_template("guide_pref_gunma.html")

@app.route("/guide/pref/yamanashi")
def guide_pref_yamanashi():
    return render_template("guide_pref_yamanashi.html")

@app.route("/guide/pref/gifu")
def guide_pref_gifu():
    return render_template("guide_pref_gifu.html")

@app.route("/guide/pref/kyoto")
def guide_pref_kyoto():
    return render_template("guide_pref_kyoto.html")

@app.route("/guide/pref/shiga")
def guide_pref_shiga():
    return render_template("guide_pref_shiga.html")

@app.route("/guide/pref/nara")
def guide_pref_nara():
    return render_template("guide_pref_nara.html")

@app.route("/guide/pref/mie")
def guide_pref_mie():
    return render_template("guide_pref_mie.html")

@app.route("/guide/pref/wakayama")
def guide_pref_wakayama():
    return render_template("guide_pref_wakayama.html")

@app.route("/guide/pref/aomori")
def guide_pref_aomori():
    return render_template("guide_pref_aomori.html")

@app.route("/guide/pref/iwate")
def guide_pref_iwate():
    return render_template("guide_pref_iwate.html")

@app.route("/guide/pref/akita")
def guide_pref_akita():
    return render_template("guide_pref_akita.html")

@app.route("/guide/pref/yamagata")
def guide_pref_yamagata():
    return render_template("guide_pref_yamagata.html")

@app.route("/guide/pref/fukushima")
def guide_pref_fukushima():
    return render_template("guide_pref_fukushima.html")

@app.route("/guide/pref/ibaraki")
def guide_pref_ibaraki():
    return render_template("guide_pref_ibaraki.html")

@app.route("/guide/pref/niigata")
def guide_pref_niigata():
    return render_template("guide_pref_niigata.html")

@app.route("/guide/pref/toyama")
def guide_pref_toyama():
    return render_template("guide_pref_toyama.html")

@app.route("/guide/pref/ishikawa")
def guide_pref_ishikawa():
    return render_template("guide_pref_ishikawa.html")

@app.route("/guide/pref/fukui")
def guide_pref_fukui():
    return render_template("guide_pref_fukui.html")

@app.route("/guide/pref/tottori")
def guide_pref_tottori():
    return render_template("guide_pref_tottori.html")

@app.route("/guide/pref/shimane")
def guide_pref_shimane():
    return render_template("guide_pref_shimane.html")

@app.route("/guide/pref/okayama")
def guide_pref_okayama():
    return render_template("guide_pref_okayama.html")

@app.route("/guide/pref/yamaguchi")
def guide_pref_yamaguchi():
    return render_template("guide_pref_yamaguchi.html")

@app.route("/guide/pref/tokushima")
def guide_pref_tokushima():
    return render_template("guide_pref_tokushima.html")

@app.route("/guide/pref/kagawa")
def guide_pref_kagawa():
    return render_template("guide_pref_kagawa.html")

@app.route("/guide/pref/ehime")
def guide_pref_ehime():
    return render_template("guide_pref_ehime.html")

@app.route("/guide/pref/kochi")
def guide_pref_kochi():
    return render_template("guide_pref_kochi.html")

@app.route("/guide/pref/saga")
def guide_pref_saga():
    return render_template("guide_pref_saga.html")

@app.route("/guide/pref/nagasaki")
def guide_pref_nagasaki():
    return render_template("guide_pref_nagasaki.html")

@app.route("/guide/pref/kumamoto")
def guide_pref_kumamoto():
    return render_template("guide_pref_kumamoto.html")

@app.route("/guide/pref/oita")
def guide_pref_oita():
    return render_template("guide_pref_oita.html")

@app.route("/guide/pref/miyazaki")
def guide_pref_miyazaki():
    return render_template("guide_pref_miyazaki.html")

@app.route("/guide/pref/kagoshima")
def guide_pref_kagoshima():
    return render_template("guide_pref_kagoshima.html")

@app.route("/guide/pref/okinawa")
def guide_pref_okinawa():
    return render_template("guide_pref_okinawa.html")

@app.route("/guide/pref/<slug>")
def guide_pref_dynamic(slug):
    pref = PREF_GUIDE_DATA.get(slug)
    if not pref or pref.get("static"):
        abort(404)
    # 同地域の都道府県（現在のページを除く、最大4件）
    same_region = [
        p for s, p in PREF_GUIDE_DATA.items()
        if p.get("region") == pref.get("region") and s != slug and not p.get("static")
    ][:4]
    return render_template("guide_pref.html", pref=pref, same_region=same_region)


@app.route("/feed.xml")
@app.route("/rss")
def rss_feed():
    """RSS 2.0フィード（ブログ村・RSSリーダー・Google News連携用）"""
    BASE = "https://beetle-finder.onrender.com"
    AUTHOR = "森山春樹（クワガタ採集スポット検索）"

    # ── 記事リスト（新しい順）──
    # カテゴリ: 採集ガイド / 飼育ガイド / 種類ガイド / 採集レポート / 都道府県
    items = [
        # ── 2026-05-31 新規公開 ──
        {"title": "春（3〜5月）のクワガタ採集ガイド｜越冬個体・材割り・シーズン開幕準備",
         "link": f"{BASE}/guide/spring",
         "desc": "春3〜5月のクワガタ採集ガイド。越冬から目覚めたコクワガタ・ヒラタクワガタが狙えます。月別の採集方法・種別活動時期一覧・シーズン開幕前チェックリスト・材割り採集のコツまで完全解説。",
         "date": "Sat, 31 May 2026 12:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "11月のクワガタ採集ガイド｜材割り採集・越冬個体探し・来シーズン準備",
         "link": f"{BASE}/guide/november",
         "desc": "11月のクワガタ採集ガイド。シーズンオフでも材割り採集でコクワガタ・オオクワガタが狙えます。越冬管理チェックリスト・幼虫飼育・来シーズンの準備まで完全解説。",
         "date": "Sat, 31 May 2026 11:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "クワガタの越冬方法【完全ガイド2026年版】冬の管理・春の起こし方まで",
         "link": f"{BASE}/guide/overwinter",
         "desc": "クワガタの越冬方法を完全解説。越冬できる種・できない種の一覧、越冬セットの作り方（マット・温度・湿度管理）、10月〜4月の月別管理カレンダー、よくある失敗と対策、春の起こし方まで採集歴20年のプロが詳しく解説。",
         "date": "Sat, 31 May 2026 10:00:00 +0900",
         "cat": "飼育ガイド"},
        # ── 2026-05-30 新規公開 ──
        {"title": "クワガタ幼虫の育て方2026年完全版｜1〜3齢の見分け方・菌糸ビン・マット比較",
         "link": f"{BASE}/guide/larva",
         "desc": "クワガタ幼虫の育て方を採集歴20年の筆者が徹底解説。1齢・2齢・3齢の見分け方、菌糸ビンvsマットの比較、温度管理、蛹化・羽化の見守り方まで。初心者でも失敗しない幼虫飼育の完全ガイド。",
         "date": "Fri, 30 May 2026 10:00:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "昆虫ゼリーおすすめ2026年版｜4タイプ比較・種別選び方・交換頻度ガイド",
         "link": f"{BASE}/guide/jelly",
         "desc": "クワガタ・カブトムシ向け昆虫ゼリーのおすすめ5選を徹底比較。高タンパク・フルーツ・プロゼリー・ワイドの4タイプ特徴と選び方、種別最適ゼリー、交換頻度・保管方法のNG例まで完全解説。",
         "date": "Fri, 30 May 2026 09:00:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "材割り採集ガイド2026年版｜冬〜春のクワガタ採集を完全マスター",
         "link": f"{BASE}/guide/zaiwari",
         "desc": "材割り採集（冬〜春シーズン）の完全ガイド。樹液採集との違い・朽ち木の見分け方・道具・STEP別手順・採集できる種一覧・採集後の幼虫の扱い方・マナーまで。オオクワガタ幼虫の採集を目指す方必見。",
         "date": "Fri, 30 May 2026 08:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "コクワガタの飼育方法【自由研究向け】観察シート付き｜成虫・産卵・幼虫",
         "link": f"{BASE}/guide/iku/kokuwagata",
         "desc": "コクワガタの飼育・繁殖を小学生でもわかるように解説。成虫飼育のSTEP・産卵セットの作り方・幼虫の育て方・観察ポイント5項目・印刷用観察シートつき。夏休みの自由研究にも最適。",
         "date": "Fri, 30 May 2026 07:00:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "ノコギリクワガタの飼育方法【自由研究向け】観察シート付き",
         "link": f"{BASE}/guide/iku/nokogiri",
         "desc": "ノコギリクワガタの飼育・繁殖を解説。大歯型・中歯型・小歯型の見分け方、産卵マットの選び方、幼虫飼育まで。観察シート付きで自由研究にも使えます。",
         "date": "Fri, 30 May 2026 06:30:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "ミヤマクワガタの飼育方法【自由研究向け】低温管理が重要",
         "link": f"{BASE}/guide/iku/miyama",
         "desc": "ミヤマクワガタの飼育は低温管理がカギ。成虫の温度管理・寿命・産卵の難しさ・幼虫の長期飼育まで詳しく解説。自由研究向け観察シート付き。",
         "date": "Fri, 30 May 2026 06:00:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "ヒラタクワガタの飼育方法【自由研究向け】挟む力が最強クラス",
         "link": f"{BASE}/guide/iku/hirata",
         "desc": "ヒラタクワガタの飼育・繁殖ガイド。ペアリング・産卵セット・幼虫飼育・大型個体の羽化まで。噛む力が強いので取り扱い注意点も解説。",
         "date": "Fri, 30 May 2026 05:30:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "オオクワガタの飼育方法【自由研究向け】菌糸ビンで大型個体を育てる",
         "link": f"{BASE}/guide/iku/ookuwa",
         "desc": "オオクワガタの飼育・大型個体の羽化を目指すガイド。菌糸ビン選択・交換タイミング・温度管理・蛹化管理まで徹底解説。日本最大クワガタを育てる達成感を。",
         "date": "Fri, 30 May 2026 05:00:00 +0900",
         "cat": "飼育ガイド"},
        {"title": "アカアシクワガタの飼育方法【自由研究向け】高山種の低温飼育",
         "link": f"{BASE}/guide/iku/akaashi",
         "desc": "アカアシクワガタの飼育ガイド。ブナ帯の高山種で飼育には低温環境が必要。成虫飼育・産卵セット・幼虫飼育の注意点を解説。",
         "date": "Fri, 30 May 2026 04:30:00 +0900",
         "cat": "飼育ガイド"},

        # ── 2026-05-30 公開 ──
        {"title": "筑波山麓 ヒラタクワガタ採集レポート2025年8月｜65mmオス含む7匹",
         "link": f"{BASE}/guide/report/tsukuba",
         "desc": "筑波山麓での夜間採集レポート。ヒラタクワガタ♂65mm含む7匹（ヒラタ2・コクワ5）を採集。低標高里山のヤナギ狙いで好成果。時間別グラフ・タイムライン・ギアリスト掲載。",
         "date": "Sat, 30 May 2026 10:00:00 +0900",
         "cat": "採集レポート"},

        # ── 2026-05-28 公開 ──
        {"title": "奥多摩 ミヤマクワガタ夜間採集レポート2025年7月｜ミヤマ5匹・最大63mm",
         "link": f"{BASE}/guide/report/okutama",
         "desc": "奥多摩での夜間採集レポート。ミヤマクワガタ5匹（最大63mm）を採集した夜の詳細記録。採集条件（気温・月齢・時刻）・場所タイプ・時間別成果グラフを掲載。",
         "date": "Wed, 28 May 2026 10:00:00 +0900",
         "cat": "採集レポート"},
        {"title": "秩父 雨上がり翌夜採集レポート2025年8月｜ノコギリ7・ヒラタ3・カブト多数",
         "link": f"{BASE}/guide/report/chichibu",
         "desc": "秩父での雨後採集レポート。ノコギリクワガタ7匹・ヒラタクワガタ3匹・カブトムシ多数を採集。雨後に採集が爆発的に増える理由と最適タイミングを解説。",
         "date": "Wed, 28 May 2026 09:00:00 +0900",
         "cat": "採集レポート"},
        {"title": "高尾山 子供と一緒ファミリー採集レポート2025年7月｜コクワ4・ノコギリ2",
         "link": f"{BASE}/guide/report/takao",
         "desc": "高尾山での子連れ採集レポート。コクワガタ4匹・ノコギリクワガタ2匹を採集。子連れ採集のコツ・安全対策・子供が喜んだポイントをまとめました。",
         "date": "Wed, 28 May 2026 08:00:00 +0900",
         "cat": "採集レポート"},

        # ── 2026-05-25 公開 ──
        {"title": "クワガタ採集スポットの選び方2026年版｜樹種・地形・水辺・標高の判断法",
         "link": f"{BASE}/guide/spot/tokyo",
         "desc": "採集スポット選びの完全ガイド。クヌギ・コナラの見つけ方、樹液の確認法、標高別種分布、水辺ボーナスの活用法、Google Mapsでのスポット下調べ方法まで。",
         "date": "Sun, 25 May 2026 10:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "ライトトラップ・ブラックライト採集完全ガイド｜設置方法・最適条件",
         "link": f"{BASE}/guide/trap",
         "desc": "ライトトラップを使ったクワガタ・カブトムシ採集の完全ガイド。ブラックライト・水銀灯の選び方、設置方法、最適な気温・月齢・場所条件、採集できる種を解説。",
         "date": "Sun, 25 May 2026 09:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "クワガタ採集に必要な道具一覧2026年版｜ヘッドライト・虫かご・安全装備",
         "link": f"{BASE}/guide/tools",
         "desc": "クワガタ採集に必要な道具を完全リスト化。ヘッドライトの選び方、虫かご・ケースの種類、安全装備（熊鈴・長袖・スパッツ）まで初心者でもすぐ揃えられる道具ガイド。",
         "date": "Sun, 25 May 2026 08:00:00 +0900",
         "cat": "採集ガイド"},

        # ── 2026-05-22 公開 ──
        {"title": "8月のクワガタ採集【2026年版】｜真夏の採集攻略・おすすめスポット",
         "link": f"{BASE}/guide/august",
         "desc": "8月のクワガタ採集攻略ガイド。真夏の高温対策・採集ピーク時間・おすすめスポット・種類別の出やすい条件を解説。ミヤマは高標高へ、ノコギリ・ヒラタは里山へ。",
         "date": "Sat, 22 May 2026 10:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "7月のクワガタ採集【2026年版】｜梅雨明け直後が採集シーズン開幕",
         "link": f"{BASE}/guide/july",
         "desc": "7月のクワガタ採集は梅雨明け直後が最大チャンス。気温上昇・雨上がり・新月を組み合わせた最強採集条件と、7月に採れる種類・おすすめスポットを解説。",
         "date": "Sat, 22 May 2026 08:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "ミヤマクワガタ完全ガイド2026年版｜生態・採集場所・採集時期・飼育法",
         "link": f"{BASE}/guide/miyama",
         "desc": "ミヤマクワガタの生態・採集場所・採集時期・飼育方法を採集歴20年の筆者が完全解説。標高800m以上の高山地帯での採集ポイント、大型個体の狙い方まで。",
         "date": "Sat, 22 May 2026 07:00:00 +0900",
         "cat": "種類ガイド"},
        {"title": "ノコギリクワガタ完全ガイド2026年版｜生態・採集場所・採集時期・飼育法",
         "link": f"{BASE}/guide/nokogiri",
         "desc": "ノコギリクワガタの生態・採集法・飼育方法を完全解説。里山の樹液ポイントで採れる日本で最もポピュラーなクワガタ。大歯型の狙い方も解説。",
         "date": "Sat, 22 May 2026 06:00:00 +0900",
         "cat": "種類ガイド"},

        # ── 2026-05-20 公開 ──
        {"title": "雨の日のクワガタ採集｜雨後が爆採チャンス！条件・タイミング・注意点",
         "link": f"{BASE}/guide/rain",
         "desc": "雨の日・雨後のクワガタ採集を徹底解説。なぜ雨後に虫が増えるのか、雨上がり後何時間が最適か、危険な条件（雷雨・増水）の見極め方まで。",
         "date": "Wed, 20 May 2026 10:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "クワガタ採集の木の種類｜クヌギ・コナラ・ヤナギの見つけ方・見分け方",
         "link": f"{BASE}/guide/tree",
         "desc": "クワガタが集まる木の種類（クヌギ・コナラ・ヤナギ・ハルニレ）の見分け方・樹液の確認法・季節ごとの樹液出やすい条件を写真解説。",
         "date": "Wed, 20 May 2026 09:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "ヒラタクワガタ完全ガイド2026年版｜生態・採集場所・採集時期・飼育法",
         "link": f"{BASE}/guide/hirata",
         "desc": "ヒラタクワガタの生態・採集ポイント・飼育方法を完全解説。低山帯の樹洞・朽木に潜む最強クワガタの採集法と、大型個体の育て方まで。",
         "date": "Wed, 20 May 2026 08:00:00 +0900",
         "cat": "種類ガイド"},

        # ── 都道府県別ガイド（主要）──
        {"title": "京都府クワガタ採集ガイド｜美山・京都北山・丹波のスポット完全解説",
         "link": f"{BASE}/guide/pref/kyoto",
         "desc": "京都府でクワガタを採るなら美山・京都北山・丹波高地・由良川ヒラタ。ノコギリ・コクワ・ヒラタ・ミヤマの採れる場所・時期・コツを徹底解説。",
         "date": "Fri, 22 May 2026 10:00:00 +0900",
         "cat": "都道府県ガイド"},
        {"title": "長野県クワガタ採集ガイド｜木曽谷・戸隠・八ヶ岳のスポット完全解説",
         "link": f"{BASE}/guide/pref/nagano",
         "desc": "長野県でクワガタを採るなら木曽谷・戸隠・伊那谷・八ヶ岳。信州ミヤマ天国の採集スポットを徹底解説。",
         "date": "Thu, 21 May 2026 08:00:00 +0900",
         "cat": "都道府県ガイド"},
        {"title": "北海道クワガタ採集ガイド｜日高山脈・渡島半島・道央のスポット完全解説",
         "link": f"{BASE}/guide/pref/hokkaido",
         "desc": "北海道でクワガタを採るなら日高山脈・渡島半島・道央（支笏湖）。エゾミヤマクワガタ固有亜種やヒグマ対策も解説。",
         "date": "Wed, 20 May 2026 12:00:00 +0900",
         "cat": "都道府県ガイド"},
        {"title": "東京都クワガタ採集ガイド｜奥多摩・高尾山・檜原村のスポット完全解説",
         "link": f"{BASE}/guide/pref/tokyo",
         "desc": "東京都でクワガタを採るなら奥多摩・高尾山・檜原村。ミヤマ・ノコギリ・ヒラタの採れる場所・時期を解説。都内で本格採集が楽しめるスポットガイド。",
         "date": "Sun, 17 May 2026 12:00:00 +0900",
         "cat": "都道府県ガイド"},
        {"title": "神奈川県クワガタ採集ガイド｜丹沢・箱根・相模川のスポット完全解説",
         "link": f"{BASE}/guide/pref/kanagawa",
         "desc": "神奈川県でクワガタを採るなら丹沢・箱根・相模川ヒラタ。横浜・川崎から日帰り可能なスポットを解説。",
         "date": "Mon, 18 May 2026 08:00:00 +0900",
         "cat": "都道府県ガイド"},
        {"title": "大阪府クワガタ採集ガイド｜金剛山・能勢・生駒山のスポット完全解説",
         "link": f"{BASE}/guide/pref/osaka",
         "desc": "大阪府でクワガタを採るなら金剛山・能勢・生駒山・石川ヒラタ。能勢オオクワガタの産地としても有名。",
         "date": "Tue, 19 May 2026 10:00:00 +0900",
         "cat": "都道府県ガイド"},

        # ── 総合ガイド ──
        {"title": "クワガタ採集 初心者完全ガイド2026年版｜道具・場所・時期・コツ",
         "link": f"{BASE}/guide/beginners",
         "desc": "クワガタ採集を始める初心者向けの完全ガイド。必要な道具・採集場所の探し方・最適な時期・時間帯・安全対策まで。これ1本でクワガタ採集デビューできます。",
         "date": "Sat, 16 May 2026 10:00:00 +0900",
         "cat": "採集ガイド"},
        {"title": "クワガタ採集完全ガイド2026年版｜初心者から上級者まで",
         "link": f"{BASE}/guide",
         "desc": "クワガタ採集の基本から上級テクニックまで解説。採集時期・場所・道具・種類別ポイント・安全対策を完全網羅。採集歴20年の筆者が執筆。",
         "date": "Sat, 01 May 2026 09:00:00 +0900",
         "cat": "採集ガイド"},
    ]

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    item_xml = ""
    for it in items:
        cat = it.get("cat", "採集ガイド")
        item_xml += f"""
    <item>
      <title>{esc(it['title'])}</title>
      <link>{it['link']}</link>
      <guid isPermaLink="true">{it['link']}</guid>
      <description>{esc(it['desc'])}</description>
      <pubDate>{it['date']}</pubDate>
      <author>info@beetle-finder.example.com ({esc(AUTHOR)})</author>
      <category>{esc(cat)}</category>
    </item>"""

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
  xmlns:atom="http://www.w3.org/2005/Atom"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>クワガタ採集スポット検索｜beetle-finder</title>
    <link>{BASE}</link>
    <description>採集歴20年・全国47都道府県フィールド経験の運営者が執筆するクワガタ採集・飼育ガイドと、月齢・気象・標高データで採集スポットを絞り込む無料サービスです。</description>
    <language>ja</language>
    <managingEditor>info@beetle-finder.example.com ({esc(AUTHOR)})</managingEditor>
    <webMaster>info@beetle-finder.example.com ({esc(AUTHOR)})</webMaster>
    <copyright>2026 クワガタ採集スポット検索 / 森山春樹</copyright>
    <ttl>1440</ttl>
    <atom:link href="{BASE}/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{items[0]['date']}</lastBuildDate>
    <image>
      <url>{BASE}/static/ogp_main.png</url>
      <title>クワガタ採集スポット検索</title>
      <link>{BASE}</link>
      <width>144</width>
      <height>144</height>
    </image>{item_xml}
  </channel>
</rss>"""

    return Response(rss, mimetype="application/rss+xml; charset=utf-8")


@app.route("/health")
def health():
    """ヘルスチェック用エンドポイント（UptimeRobotなどの死活監視から定期ping）"""
    return "OK", 200


@app.route("/robots.txt")
def robots():
    from flask import send_from_directory
    return send_from_directory("static", "robots.txt", mimetype="text/plain")


@app.route("/ads.txt")
def ads_txt():
    from flask import send_from_directory
    return send_from_directory("static", "ads.txt", mimetype="text/plain")


@app.route("/ogp.png")
def ogp_png():
    """OGP画像を /ogp.png でも配信（SNSクローラー向け短縮URL）"""
    from flask import send_from_directory
    return send_from_directory("static", "ogp.png", mimetype="image/png")


@app.route("/manifest.json")
def manifest():
    """PWA Web App Manifest"""
    from flask import send_from_directory
    return send_from_directory("static", "manifest.json", mimetype="application/manifest+json")


@app.route("/sw.js")
def service_worker():
    """Service Worker（キャッシュ制御）"""
    from flask import send_from_directory, make_response
    resp = make_response(send_from_directory("static", "sw.js", mimetype="application/javascript"))
    resp.headers["Service-Worker-Allowed"] = "/"
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.route("/apple-touch-icon.png")
@app.route("/apple-touch-icon-precomposed.png")
def apple_touch_icon():
    """iOS ホーム画面アイコン"""
    from flask import send_from_directory
    return send_from_directory("static", "apple-touch-icon.png", mimetype="image/png")


@app.route("/sitemap.xml")
def sitemap():
    # lastmod は各ページの実際の最終更新日を固定値で設定する（動的 date.today() は使わない）
    # ※ コンテンツ更新時は該当URLの日付を修正してpushすること
    # 最終一括更新: 2026-06-07（msmaflink全ページ展開・container崩れ修正・WebP化）
    D_TODAY   = "2026-06-07"  # 本日一括更新したページ
    D_STABLE  = "2026-05-30"  # 公開時から安定しているページ（初回公開日）

    BASE = "https://beetle-finder.onrender.com"
    urls = [
        # ── コアページ（weekly: 機能更新の可能性あり） ──
        (f"{BASE}/",    "weekly",  "1.0", D_TODAY),
        (f"{BASE}/app", "weekly",  "0.9", D_TODAY),

        # ── ガイドトップ ──
        (f"{BASE}/guide", "monthly", "0.8", D_TODAY),

        # ── 採集技術・初心者向けガイド（年数回更新想定 → monthly） ──
        (f"{BASE}/guide/beginners",    "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/beginner-kit", "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/scoring",   "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/trap",      "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/light",     "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/night",     "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/morning",   "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/rain",      "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/tree",      "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/tools",     "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/kids",      "monthly", "0.7", D_TODAY),
        (f"{BASE}/guide/zaiwari",   "monthly", "0.8", D_TODAY),

        # ── 種別ガイド（年1回更新想定 → yearly） ──
        (f"{BASE}/guide/miyama",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/nokogiri",   "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/hirata",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/ookuwa",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/kabuto",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/kokuwagata", "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/akaashi",    "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/suji",       "yearly", "0.7", D_TODAY),

        # ── 飼育・育て方ガイド（yearly） ──
        (f"{BASE}/guide/larva",             "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/breeding",          "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/case",              "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/aftercare",         "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/overwinter",        "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/jelly",             "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/jiyukenkyu",        "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/jiyukenkyu-kabuto", "yearly", "0.7", D_TODAY),

        # ── 種別飼育記事 (yearly) ──
        (f"{BASE}/guide/iku/kokuwagata", "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/iku/nokogiri",   "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/iku/miyama",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/iku/hirata",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/iku/ookuwa",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/iku/akaashi",    "yearly", "0.7", D_TODAY),

        # ── 月別採集カレンダー（シーズンコンテンツ → yearly） ──
        (f"{BASE}/guide/calendar",   "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/spring",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/may",        "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/june",       "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/july",       "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/august",     "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/september",  "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/october",    "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/november",   "yearly", "0.8", D_TODAY),

        # ── 採集レポート（yearly） ──
        (f"{BASE}/guide/reports",           "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/experiences",       "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/manner",            "yearly",  "0.7", D_TODAY),
        (f"{BASE}/guide/report/okutama",    "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/report/chichibu",   "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/report/takao",      "yearly", "0.7", D_TODAY),
        (f"{BASE}/guide/report/tsukuba",    "yearly", "0.7", D_TODAY),

        # ── 都道府県別採集ガイド（/guide/pref/<pref> / 47ページ）
        # ※ /guide/spot/<pref> は /guide/pref/<pref> へ301リダイレクト済み・サイトマップから除外 ──
        (f"{BASE}/guide/pref/hokkaido",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/aomori",    "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/iwate",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/miyagi",    "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/akita",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/yamagata",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/fukushima", "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/ibaraki",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/tochigi",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/gunma",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref",           "yearly", "0.8", D_TODAY),
        (f"{BASE}/guide/pref/saitama",   "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/pref/chiba",     "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/pref/tokyo",     "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/pref/kanagawa",  "monthly", "0.8", D_TODAY),
        (f"{BASE}/guide/pref/niigata",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/toyama",    "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/ishikawa",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/fukui",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/yamanashi", "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/nagano",    "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/gifu",      "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/shizuoka",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/aichi",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/mie",       "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/shiga",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/kyoto",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/osaka",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/hyogo",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/nara",      "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/wakayama",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/tottori",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/shimane",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/okayama",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/hiroshima", "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/yamaguchi", "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/tokushima", "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/kagawa",    "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/ehime",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/kochi",     "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/fukuoka",   "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/saga",      "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/nagasaki",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/kumamoto",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/oita",      "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/miyazaki",  "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/kagoshima", "yearly", "0.7", D_STABLE),
        (f"{BASE}/guide/pref/okinawa",   "yearly", "0.7", D_STABLE),

        # ── サービス情報ページ ──
        (f"{BASE}/about",   "monthly", "0.6", D_TODAY),
        (f"{BASE}/contact", "yearly",  "0.4", D_STABLE),
        (f"{BASE}/privacy", "yearly",  "0.3", D_STABLE),
        (f"{BASE}/terms",   "yearly",  "0.3", D_STABLE),
    ]
    entries = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{lmod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{pri}</priority>\n  </url>"
        for loc, freq, pri, lmod in urls
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>'
    return Response(xml, mimetype="application/xml")


@app.route("/api/geocode")
def geocode():
    addr = request.args.get("address", "").strip()
    if not addr:
        return jsonify({"error": "住所を入力してください"}), 400
    # Nominatim にフォールバックするシンプルな実装
    endpoints = [
        ("https://nominatim.openstreetmap.org/search",
         {"q": addr, "format": "json", "limit": 1, "accept-language": "ja"}),
        ("https://nominatim.openstreetmap.org/search",
         {"q": addr + " 日本", "format": "json", "limit": 1, "accept-language": "ja"}),
    ]
    last_err = "住所が見つかりませんでした"
    for url, params in endpoints:
        try:
            r = _session.get(url, params=params, headers=HEADERS, timeout=15)
            hits = r.json()
            if hits:
                h = hits[0]
                return jsonify({"lat": float(h["lat"]), "lng": float(h["lon"]),
                                "display_name": h["display_name"]})
            last_err = f"「{addr}」が見つかりませんでした"
        except RecursionError:
            # gevent + SSL 深い再帰 → サーバーを再試行
            return jsonify({"error": "サーバー内部エラーが発生しました。もう一度「設定」を押してください。"}), 500
        except Exception as e:
            last_err = str(e)
    return jsonify({"error": last_err}), 404


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




# ── スポットDB読み込み ────────────────────────────────────────────────────
import os as _os

def _load_spots_db(filename):
    path = _os.path.join(_os.path.dirname(__file__), "static", filename)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("spots", [])
    except Exception:
        return []

_FAMILY_SPOTS = _load_spots_db("family_spots.json")
_EXPERT_SPOTS = _load_spots_db("expert_spots.json")
_URBAN_PARK_SPOTS = _load_spots_db("urban_park_spots_clean.json")

# 樹種スコア重み（種別×樹種）
_TREE_WEIGHT = {
    "miyama":     {"konara":0.45,"kunugi":0.25,"mizunara":0.20,"buna":0.05,"other":0.05},
    "akaashi":    {"buna":0.50,"mizunara":0.30,"konara":0.15,"other":0.05},
    "okuwagata":  {"kunugi":0.50,"konara":0.30,"other":0.20},
    "nokogiri":   {"kunugi":0.40,"konara":0.30,"yanagi":0.15,"hannoki":0.10,"other":0.05},
    "hirata":     {"kunugi":0.35,"yanagi":0.35,"hannoki":0.15,"konara":0.10,"other":0.05},
    "kokuwagata": {"kunugi":0.40,"konara":0.35,"other":0.25},
    "kabuto":     {"kunugi":0.50,"konara":0.35,"other":0.15},
    "suji":       {"buna":0.60,"mizunara":0.30,"other":0.10},
}
# 最適標高（種別）
_ELEV_OPT = {
    "miyama":700,"akaashi":900,"okuwagata":300,"nokogiri":250,
    "hirata":150,"kokuwagata":300,"kabuto":200,"suji":800,
}
# 最適月（種別）
_BEST_MONTHS = {
    "miyama":[6,7],"akaashi":[6,7],"okuwagata":[7,8],
    "nokogiri":[6,7,8],"hirata":[7,8],"kokuwagata":[6,7,8],
    "kabuto":[7],"suji":[6,7],
}

def _expert_score(spot, species, method, moon_age, month):
    """研究ベースの9軸スコアリング（0〜100点）"""
    s = 0
    trees = spot.get("trees", {})
    tw = _TREE_WEIGHT.get(species, _TREE_WEIGHT["nokogiri"])

    # A. 樹種マッチ（最大18点）
    tree_match = sum(trees.get(t, 0) * w for t, w in tw.items()) / 100.0
    s += tree_match * 18

    # B. 標高適性（最大10点）
    elev_opt = _ELEV_OPT.get(species, 400)
    elev = spot.get("elevation", 400)
    elev_diff = abs(elev - elev_opt)
    s += max(0, 10 - elev_diff / 60)

    # C. 水場スコア（最大7点）
    water_m = spot.get("water_m", 500)
    if species == "hirata":
        s += 7 if water_m < 50 else (5 if water_m < 150 else (3 if water_m < 300 else 0))
    else:
        s += 4 if water_m < 100 else (2 if water_m < 300 else 0)

    # D. 採集方法別（最大25点）
    if method == "light":
        lp = spot.get("light_pollution", 3)
        s += (5 - lp) * 5  # 光害なし=25点、最悪=0点
    elif method == "street":
        lp = spot.get("light_pollution", 3)
        s += lp * 4  # 街灯が多い=高点
    else:  # tree
        tree_score = min(25, tree_match * 28)
        s += tree_score

    # E. 気温スコア（今月の気温は取得困難なので月×標高で推定）
    # 夏(7-8月)の平地気温27℃ - (標高/150)℃ が夜間気温の目安
    est_night_temp = 27 - (elev / 150) + (1 if month == 7 else 0)
    if est_night_temp >= 25:
        s += 10
    elif est_night_temp >= 22:
        s += 6
    elif est_night_temp >= 19:
        s += 3
    else:
        s += 0

    # F. 月齢スコア（ライト採集のみ2倍効果, 最大8点通常・15点ライト）
    if moon_age < 2 or moon_age > 27.5:
        moon_s = 8
    elif moon_age < 5 or moon_age > 25:
        moon_s = 6
    elif moon_age < 8 or moon_age > 22:
        moon_s = 4
    elif moon_age < 12 or moon_age > 18:
        moon_s = 2
    else:
        moon_s = 0
    s += moon_s * (1.9 if method == "light" else 1.0)

    # G. 季節スコア（最大7点）
    best_m = _BEST_MONTHS.get(species, [7])
    s += 7 if month in best_m else (3 if abs(month - best_m[0]) <= 1 else 0)

    # H. 採集圧補正（access_hardが高い=穴場=+5点）
    ah = spot.get("access_hard", 2)
    s += (ah - 1) * 2.5  # 難易度1=0点、3=+5点

    return max(0, min(100, round(s)))


def _family_score(spot, species, method, moon_age, month, origin_lat, origin_lng):
    """家族用スコア（距離・難易度・ファミリー適性を重視）"""
    dist = haversine(origin_lat, origin_lng, spot["lat"], spot["lng"])
    dist_s = max(0, 30 - dist * 0.5)  # 0km=30点、60km=0点

    # 種マッチ
    sp_match = 15 if species in spot.get("species", []) else 0

    # 季節
    best_m = spot.get("best_months", [7])
    month_s = 8 if month in best_m else (3 if any(abs(month - m) <= 1 for m in best_m) else 0)

    # ファミリー適性
    fam_s = 10 if spot.get("family_ok") else 0

    # 難易度（低いほど高得点、家族向け）
    diff = spot.get("difficulty", 2)
    diff_s = (3 - diff) * 5  # 難易度1=10点、2=5点、3=0点

    # 駐車場
    park_s = 5 if spot.get("parking") else 0

    # 月齢（ライト採集のみ考慮）
    moon_s = 0
    if method == "light":
        moon_s = 8 if (moon_age < 3 or moon_age > 27) else 4 if (moon_age < 6 or moon_age > 24) else 0

    total = dist_s + sp_match + month_s + fam_s + diff_s + park_s + moon_s
    return max(0, min(100, round(total)))


def _calc_moon_age(date_str):
    known_new = datetime.date(2000, 1, 6)
    try:
        target = datetime.date.fromisoformat(date_str)
    except Exception:
        target = datetime.date.today()
    days = (target - known_new).days
    return ((days % 29.53058867) + 29.53058867) % 29.53058867


_DIR_ANGLES = {"N":0,"NE":45,"E":90,"SE":135,"S":180,"SW":225,"W":270,"NW":315}

def _in_direction(lat1, lng1, lat2, lng2, direction, half_deg=67.5):
    """指定方向 ±half_deg 以内かどうか判定 (direction='all' は常に True)"""
    if direction not in _DIR_ANGLES:
        return True
    b = bearing(lat1, lng1, lat2, lng2)
    diff = abs((b - _DIR_ANGLES[direction] + 180) % 360 - 180)
    return diff <= half_deg


@app.route("/api/nearby-spots")
def nearby_spots():
    """家族用・玄人用 スポット検索API"""
    try:
        lat    = float(request.args.get("lat", DEFAULT_LAT))
        lng    = float(request.args.get("lng", DEFAULT_LNG))
        mode   = request.args.get("mode", "family")       # family / expert
        radius = float(request.args.get("radius", 50))    # km
        species = request.args.get("species", "nokogiri")
        method  = request.args.get("method", "tree")
        month   = int(request.args.get("month", datetime.date.today().month))
        date_str = request.args.get("date", datetime.date.today().isoformat())
        direction = request.args.get("direction", "all")   # N/NE/E/SE/S/SW/W/NW/all
        moon_age = _calc_moon_age(date_str)

        if mode == "park":
            # 都市公園モード：駅・公園近郊の採集候補
            results = []
            for spot in _URBAN_PARK_SPOTS:
                dist = haversine(lat, lng, spot["lat"], spot["lng"])
                if dist > radius:
                    continue
                if not _in_direction(lat, lng, spot["lat"], spot["lng"], direction):
                    continue
                sc = _family_score(spot, species, method, moon_age, month, lat, lng)
                # 公園スコアは採集有望度を加算
                sc = min(100, sc + int(spot.get("collection_score", 0)))
                results.append({**spot, "dist_km": round(dist, 1), "score": sc})
            results.sort(key=lambda x: -x["score"])
            return jsonify({"mode":"park","spots": results[:80], "moon_age": round(moon_age,1)})

        elif mode == "family":
            # 山地スポット＋都市公園を合算して返す
            results = []
            seen_keys = set()
            for spot in _FAMILY_SPOTS + _URBAN_PARK_SPOTS:
                dist = haversine(lat, lng, spot["lat"], spot["lng"])
                if dist > radius:
                    continue
                if not _in_direction(lat, lng, spot["lat"], spot["lng"], direction):
                    continue
                # 同名 or 同座標（小数2桁）の重複を除去
                dedup_key = (spot["name"], round(spot["lat"], 2), round(spot["lng"], 2))
                if dedup_key in seen_keys:
                    continue
                seen_keys.add(dedup_key)
                sc = _family_score(spot, species, method, moon_age, month, lat, lng)
                if spot.get("spot_type") == "urban_park":
                    sc = min(100, sc + int(spot.get("collection_score", 0)))
                results.append({**spot, "dist_km": round(dist, 1), "score": sc})
            results.sort(key=lambda x: -x["score"])
            return jsonify({"mode":"family","spots": results[:80], "moon_age": round(moon_age,1)})

        else:  # expert
            db = _EXPERT_SPOTS
            results = []
            for spot in db:
                dist = haversine(lat, lng, spot["lat"], spot["lng"])
                if dist > radius:
                    continue
                if not _in_direction(lat, lng, spot["lat"], spot["lng"], direction):
                    continue
                sc = _expert_score(spot, species, method, moon_age, month)
                results.append({**spot, "dist_km": round(dist, 1), "score": sc})
            results.sort(key=lambda x: -x["score"])
            return jsonify({"mode":"expert","spots": results[:120], "moon_age": round(moon_age,1)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/urban-parks")
def urban_parks_api():
    """都市公園スポット検索API（フロントエンド用）"""
    try:
        lat      = float(request.args.get("lat", DEFAULT_LAT))
        lng      = float(request.args.get("lng", DEFAULT_LNG))
        radius   = float(request.args.get("radius", 30))   # デフォルト30km
        pref     = request.args.get("pref", "")            # 都道府県フィルタ
        min_ha   = float(request.args.get("min_ha", 0))    # 最小面積(ha)
        sort_by  = request.args.get("sort", "dist")        # dist / score / area

        results = []
        for spot in _URBAN_PARK_SPOTS:
            dist = haversine(lat, lng, spot["lat"], spot["lng"])
            if dist > radius:
                continue
            if pref and spot.get("prefecture") != pref:
                continue
            if spot.get("area_ha", 0) < min_ha:
                continue
            results.append({
                **spot,
                "dist_km": round(dist, 1),
            })

        if sort_by == "area":
            results.sort(key=lambda x: -x.get("area_ha", 0))
        elif sort_by == "score":
            results.sort(key=lambda x: -x.get("collection_score", 0))
        else:
            results.sort(key=lambda x: x["dist_km"])

        return jsonify({
            "total": len(results),
            "spots": results[:100],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/urban-parks/stats")
def urban_parks_stats():
    """都市公園データの統計情報"""
    from collections import Counter
    pref_count = Counter(s.get("prefecture") for s in _URBAN_PARK_SPOTS)
    return jsonify({
        "total": len(_URBAN_PARK_SPOTS),
        "by_prefecture": dict(pref_count.most_common()),
    })


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("404.html"), 500


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=port)
