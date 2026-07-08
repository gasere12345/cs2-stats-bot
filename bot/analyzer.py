from typing import Any


_THRESHOLDS_COMBAT = {
    "kd": {"excellent": 1.5, "good": 1.2, "average": 0.9, "bad": 0.6},
    "adr": {"excellent": 100, "good": 80, "average": 60, "bad": 40},
    "kpr": {"excellent": 0.85, "good": 0.70, "average": 0.55, "bad": 0.40},
    "hs_pct": {"excellent": 55, "good": 45, "average": 35, "bad": 25},
}

_THRESHOLDS_IMPACT = {
    "mvps": {"excellent": 4, "good": 2, "average": 0, "bad": -1},
    "multi_kills": {"excellent": 4, "good": 2, "average": 0, "bad": -1},
}

_THRESHOLDS_ENTRY = {
    "entry_pct": {"excellent": 75, "good": 60, "average": 40, "bad": 20},
}

_THRESHOLDS_KAST = {
    "kast": {"excellent": 80, "good": 70, "average": 55, "bad": 40},
}

_WEIGHTS = {
    "combat": 0.35,
    "impact": 0.20,
    "entry": 0.25,
    "kast": 0.20,
}


def _score_metric(value: float, thresholds: dict) -> float:
    if value >= thresholds["excellent"]:
        return 2.0
    if value >= thresholds["good"]:
        t = (value - thresholds["good"]) / (thresholds["excellent"] - thresholds["good"])
        return 1.0 + t
    if value >= thresholds["average"]:
        t = (value - thresholds["average"]) / (thresholds["good"] - thresholds["average"])
        return 0.0 + t
    if value >= thresholds["bad"]:
        t = (value - thresholds["bad"]) / (thresholds["average"] - thresholds["bad"])
        return -1.0 + t
    if thresholds["bad"] > 0:
        t = value / thresholds["bad"]
        return -2.0 + t
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

    fk = data.get("first_kills", 0)
    fd = data.get("first_deaths", 0)
    if fk + fd > 0:
        entry = _score_metric(data.get("entry_success_pct", 0), _THRESHOLDS_ENTRY["entry_pct"])
    else:
        entry = 0.0

    if data.get("kast", 0) > 0:
        kast = _score_metric(data["kast"], _THRESHOLDS_KAST["kast"])
    else:
        kast = 0.0

    total = (
        combat * _WEIGHTS["combat"]
        + impact * _WEIGHTS["impact"]
        + entry * _WEIGHTS["entry"]
        + kast * _WEIGHTS["kast"]
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
