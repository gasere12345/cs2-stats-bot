import math
from typing import Any


def compute_rating(agg: dict[str, Any], usefulness_score: float) -> float:
    base = agg.get("elo", 1000) or 1000
    return round(base + usefulness_score * 100, 1)


def estimate_rating(usefulness_score: float, kd: float, adr: float) -> float:
    base = 1000.0
    kd_bonus = (kd - 1.0) * 200
    adr_bonus = (adr - 70) * 3
    perf_bonus = usefulness_score * 150
    return round(base + kd_bonus + adr_bonus + perf_bonus, 1)


def win_probability(player_rating: float, opponent_avg_rating: float) -> float:
    diff = player_rating - opponent_avg_rating
    p = 1.0 / (1.0 + math.pow(10, -diff / 400.0))
    return round(p * 100, 1)


def team_win_probability(team_avg: float, opponent_avg: float) -> float:
    diff = team_avg - opponent_avg
    p = 1.0 / (1.0 + math.pow(10, -diff / 400.0))
    return round(p * 100, 1)


def required_rating_to_win(current_rating: float, opponent_avg_rating: float) -> float:
    return round(opponent_avg_rating + 1, 1)


def required_kd_to_win(base_elo: float, target_rating: float, current_adr: float) -> float:
    rating_gap = target_rating - base_elo
    if rating_gap <= 0:
        return 0.0
    kd_needed = 1.0 + (rating_gap - (current_adr - 70) * 3) / 200
    return round(max(kd_needed, 0.0), 2)
