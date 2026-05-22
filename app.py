import sys
sys.setrecursionlimit(10000)   # gevent + SSL ハンドシェイクの深い再帰に対応

from flask import Flask, render_template, Response, jsonify, request, stream_with_context, abort
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
    data = SPOT_DATA.get(pref)
    if not data:
        from flask import abort
        abort(404)
    return render_template("guide_spot.html", pref=pref, **data)


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


@app.route("/sitemap.xml")
def sitemap():
    from datetime import date
    today = date.today().isoformat()
    urls = [
        ("https://beetle-finder.onrender.com/",                "weekly",  "1.0", today),
        ("https://beetle-finder.onrender.com/app",             "weekly",  "0.9", today),
        ("https://beetle-finder.onrender.com/guide",           "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/beginners", "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/miyama",    "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/nokogiri",  "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/hirata",    "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/ookuwa",    "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/kabuto",       "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/kokuwagata", "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/akaashi",    "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/suji",       "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/kids",      "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/light",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/night",     "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/tools",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/aftercare", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/may",       "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/june",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/july",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/august",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/september","monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/october",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/hokkaido",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/aomori",    "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/iwate",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/miyagi",    "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/akita",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/yamagata",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/fukushima", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/ibaraki",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/tochigi",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/gunma",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/saitama",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/chiba",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/tokyo",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/kanagawa",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/niigata",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/toyama",    "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/ishikawa",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/fukui",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/yamanashi", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/nagano",    "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/gifu",      "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/shizuoka",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/aichi",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/mie",       "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/shiga",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/kyoto",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/osaka",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/hyogo",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/nara",      "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/wakayama",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/tottori",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/shimane",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/okayama",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/hiroshima", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/yamaguchi", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/tokushima", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/kagawa",    "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/ehime",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/kochi",     "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/fukuoka",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/saga",      "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/nagasaki",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/kumamoto",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/oita",      "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/miyazaki",  "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/kagoshima", "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/pref/okinawa",   "monthly", "0.7", today),
        ("https://beetle-finder.onrender.com/guide/trap",      "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/calendar",  "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/breeding",  "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/case",      "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/jiyukenkyu",        "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/jiyukenkyu-kabuto", "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/tree",    "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/morning", "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/guide/rain",    "monthly", "0.8", today),
        ("https://beetle-finder.onrender.com/about",           "monthly", "0.5", today),
        ("https://beetle-finder.onrender.com/privacy",         "yearly",  "0.3", today),
        ("https://beetle-finder.onrender.com/terms",           "yearly",  "0.3", today),
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

        if mode == "family":
            db = _FAMILY_SPOTS
            results = []
            for spot in db:
                dist = haversine(lat, lng, spot["lat"], spot["lng"])
                if dist > radius:
                    continue
                if not _in_direction(lat, lng, spot["lat"], spot["lng"], direction):
                    continue
                sc = _family_score(spot, species, method, moon_age, month, lat, lng)
                results.append({**spot, "dist_km": round(dist, 1), "score": sc})
            results.sort(key=lambda x: -x["score"])
            return jsonify({"mode":"family","spots": results[:60], "moon_age": round(moon_age,1)})

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


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug, port=port)
