import math
from typing import Any


def compute_rating(agg: dict[str, Any], usefulness_score: float) -> float:
    return round(1000 + usefulness_score * 250, 1)


def estimate_rating(usefulness_score: float, kd: float, adr: float) -> float:
    return round(1000 + usefulness_score * 250, 1)


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


def required_score_to_win(current_usefulness: float, opponent_avg_rating: float, player_rating: float) -> float:
    needed_rating = opponent_avg_rating + 1
    needed_usefulness = (needed_rating - 1000) / 250
    return round(max(needed_usefulness, -2.0), 2)
