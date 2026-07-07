from typing import Any


_THRESHOLDS_COMBAT = {
    "kd": {"excellent": 1.5, "good": 1.2, "average": 0.9, "bad": 0.6},
    "adr": {"excellent": 100, "good": 80, "average": 60, "bad": 40},
    "kpr": {"excellent": 0.85, "good": 0.70, "average": 0.55, "bad": 0.40},
    "hs_pct": {"excellent": 55, "good": 45, "average": 35, "bad": 25},
}

_THRESHOLDS_IMPACT = {
    "mvps": {"excellent": 5, "good": 3, "average": 1, "bad": 0},
    "multi_kills": {"excellent": 4, "good": 2, "average": 1, "bad": 0},
}

_THRESHOLDS_ENTRY = {
    "entry_pct": {"excellent": 60, "good": 50, "average": 40, "bad": 30},
    "trade_ratio": {"excellent": 1.5, "good": 1.2, "average": 0.8, "bad": 0.5},
}

_THRESHOLDS_UTILITY = {
    "util_dmg": {"excellent": 150, "good": 100, "average": 60, "bad": 30},
    "flashes": {"excellent": 10, "good": 6, "average": 3, "bad": 1},
}

_THRESHOLDS_CLUTCH = {
    "clutch_wins": {"excellent": 2, "good": 1, "average": 0, "bad": 0},
}

_WEIGHTS = {
    "combat": 0.35,
    "impact": 0.25,
    "entry": 0.15,
    "utility": 0.10,
    "clutch": 0.10,
    "hltv": 0.05,
}


def _score_metric(value: float, thresholds: dict) -> float:
    if value >= thresholds["excellent"]:
        return 2.0
    if value >= thresholds["good"]:
        return 1.0
    if value >= thresholds["average"]:
        return 0.0
    if value >= thresholds["bad"]:
        return -1.0
    return -2.0


def compute_usefulness(data: dict[str, Any]) -> float:
    combat_scores = [
        _score_metric(data.get("kd", 0), _THRESHOLDS_COMBAT["kd"]),
        _score_metric(data.get("adr", 0), _THRESHOLDS_COMBAT["adr"]),
        _score_metric(data.get("kpr", 0), _THRESHOLDS_COMBAT["kpr"]),
        _score_metric(data.get("hs_pct", 0), _THRESHOLDS_COMBAT["hs_pct"]),
    ]
    combat = sum(combat_scores) / len(combat_scores)

    multi = data.get("triple_kills", 0) + data.get("quadro_kills", 0) * 2 + data.get("penta_kills", 0) * 3
    impact_scores = [
        _score_metric(float(data.get("mvps", 0)), _THRESHOLDS_IMPACT["mvps"]),
        _score_metric(float(multi), _THRESHOLDS_IMPACT["multi_kills"]),
    ]
    impact = sum(impact_scores) / len(impact_scores)

    entry_scores = [
        _score_metric(data.get("entry_success_pct", 0), _THRESHOLDS_ENTRY["entry_pct"]),
        _score_metric(data.get("trade_ratio", 0), _THRESHOLDS_ENTRY["trade_ratio"]),
    ]
    entry = sum(entry_scores) / len(entry_scores)

    util_scores = [
        _score_metric(data.get("utility_damage", 0), _THRESHOLDS_UTILITY["util_dmg"]),
        _score_metric(float(data.get("enemies_flashed", 0)), _THRESHOLDS_UTILITY["flashes"]),
    ]
    utility = sum(util_scores) / len(util_scores)

    clutch_val = data.get("clutch_1v1_wins", 0) + data.get("clutch_1v2_wins", 0) * 2
    clutch = _score_metric(float(clutch_val), _THRESHOLDS_CLUTCH["clutch_wins"])

    hltv_val = data.get("hltv_rating", 0)
    if hltv_val >= 1.5:
        hltv_score = 2.0
    elif hltv_val >= 1.2:
        hltv_score = 1.0
    elif hltv_val >= 1.0:
        hltv_score = 0.0
    elif hltv_val >= 0.8:
        hltv_score = -1.0
    else:
        hltv_score = -2.0

    total = (
        combat * _WEIGHTS["combat"]
        + impact * _WEIGHTS["impact"]
        + entry * _WEIGHTS["entry"]
        + utility * _WEIGHTS["utility"]
        + clutch * _WEIGHTS["clutch"]
        + hltv_score * _WEIGHTS["hltv"]
    )
    return round(total, 1)


def describe_usefulness(score: float) -> str:
    if score >= 1.5:
        return "🔥 Carry — доминировал в матче, вытащил команду"
    if score >= 0.5:
        return "✅ Good — уверенная игра, весомый вклад"
    if score >= -0.5:
        return "➖ Average — средняя игра, можно лучше"
    if score >= -1.5:
        return "⚠️ Weak — не твой день, провальные показатели"
    return "💀 Throw — полный провал, иди отдыхать"


def describe_skill_level(level: int, elo: int, win_rate: float) -> str:
    if level >= 10 and elo >= 2500:
        return "🏆 Pro Player (Top 0.1%)"
    if level >= 10:
        return "👑 Elite (Top 1-2%)"
    if level >= 9:
        return "⭐ Advanced (Top 5%)"
    if level >= 8:
        return "🔷 Strong (Top 15%)"
    if level >= 7:
        return "🔶 Above Average"
    if level >= 5:
        return "🟡 Average"
    return "🟢 Beginner"
