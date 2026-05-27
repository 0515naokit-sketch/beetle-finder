"""
clean_urban_parks.py
──────────────────────────────────────────────────────────────
urban_park_spots.json を整理して urban_park_spots_clean.json を生成。
・非公園エリア（グラウンド・広場のみ等）を除外
・同名×同都道府県の重複を除去（最大面積を残す）
・1ha未満を除外
・採集に不向きな名前キーワードを除外
"""

import json
import re

IN_FILE  = "static/urban_park_spots.json"
OUT_FILE = "static/urban_park_spots_clean.json"

# ── 除外キーワード（公園名に含まれる場合は除外）────────────────────────
EXCLUDE_KEYWORDS = [
    "グラウンド", "運動場", "球場", "サッカー場", "テニスコート",
    "プール", "スタジアム", "競技場", "体育館", "ゴルフ",
    "駐車場", "ガーデン", "キャンプ場", "オートキャンプ",
    "農園", "菜園", "バーベキュー",
]

# ── 採集有望度スコア（名前に含まれると+ポイント）──────────────────────
POSITIVE_KEYWORDS = {
    "森": 3, "林": 3, "雑木": 5, "緑地": 2, "自然": 3,
    "里山": 5, "野":  1, "谷": 1, "丘": 1, "山": 1,
    "川": 1, "河": 1, "池": 1, "湿地": 2, "湖": 1,
    "ふれあい": 1, "どんぐり": 5, "クヌギ": 10, "コナラ": 10,
}

def exclude(name):
    """除外すべき名前かどうか"""
    for kw in EXCLUDE_KEYWORDS:
        if kw in name:
            return True
    # 名前が短すぎる広場系
    if re.match(r'^(第?\d+)?広場$', name):
        return True
    if re.match(r'^(多目的|芝生|ピクニック|子ども|子供|花|バラ|噴水|休憩)広場$', name):
        return True
    return False

def score(spot):
    """採集有望度スコアを計算"""
    s = 0
    name = spot["name"]
    for kw, pts in POSITIVE_KEYWORDS.items():
        if kw in name:
            s += pts
    s += min(spot["area_ha"] / 5, 10)  # 面積ボーナス（最大10点）
    return round(s, 1)

def main():
    with open(IN_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    spots = raw["spots"]
    print(f"入力: {len(spots)}件")

    # ── 除外フィルタ ──────────────────────────────────────────────────
    filtered = [s for s in spots if not exclude(s["name"])]
    print(f"除外後: {len(filtered)}件（{len(spots)-len(filtered)}件除外）")

    # ── 1ha未満を除外 ─────────────────────────────────────────────────
    filtered = [s for s in filtered if s["area_ha"] >= 1.0]
    print(f"1ha以上: {len(filtered)}件")

    # ── 同名×同都道府県の重複を除去（最大面積を優先）─────────────────────
    key_map = {}
    for s in filtered:
        key = (s["name"], s["prefecture"])
        if key not in key_map or s["area_ha"] > key_map[key]["area_ha"]:
            key_map[key] = s
    deduped = list(key_map.values())
    print(f"重複除去後: {len(deduped)}件（{len(filtered)-len(deduped)}件除去）")

    # ── 採集有望度スコアを付与 ────────────────────────────────────────
    for s in deduped:
        s["collection_score"] = score(s)

    # ── IDを振り直す ─────────────────────────────────────────────────
    # 既存family_spotsの最大ID取得
    try:
        with open("static/family_spots.json", encoding="utf-8") as f:
            fam = json.load(f)
        base_id = max(s["id"] for s in fam["spots"]) + 1
    except Exception:
        base_id = 5000

    for i, s in enumerate(deduped):
        s["id"] = base_id + i

    # ── スコア順にソート ──────────────────────────────────────────────
    deduped.sort(key=lambda s: (-s["collection_score"], -s["area_ha"]))

    # ── 保存 ─────────────────────────────────────────────────────────
    output = {
        "description": "主要都市の公園スポット（クリーニング済み）",
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "note": "verified=false は未確認スポット。採集可否は各公園に要確認。",
        "total": len(deduped),
        "spots": deduped,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n保存完了: {OUT_FILE}  ({len(deduped)}件)")

    # ── サマリー ─────────────────────────────────────────────────────
    print("\n── 有望スコアTOP30（採集おすすめ公園） ──")
    for s in deduped[:30]:
        print(f"  [{s['collection_score']:4.1f}] {s['name']:25s} {s['area_ha']:7.1f}ha  {s['prefecture']}")

    print("\n── 都市別件数 ──")
    from collections import Counter
    c = Counter(s["area"] for s in deduped)
    for label, count in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {label:15s}: {count:4d}件")

    print("\n── 面積分布 ──")
    sizes = [(1,5,"1〜5ha"), (5,20,"5〜20ha"), (20,50,"20〜50ha"), (50,9999,"50ha〜")]
    for lo, hi, label in sizes:
        n = sum(1 for s in deduped if lo <= s["area_ha"] < hi)
        print(f"  {label}: {n}件")

if __name__ == "__main__":
    main()
