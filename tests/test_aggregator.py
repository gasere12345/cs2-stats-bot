import pytest
from bot.aggregator import aggregate_player_data


def test_aggregate_basic():
    match_stats = {
        "map": "de_mirage",
        "score": "16-12",
        "rounds": "28",
        "players": [
            {
                "player_id": "p1",
                "nickname": "NiKo",
                "team_name": "TeamA",
                "team_score": "16",
                "won": True,
                "stats": {
                    "Kills": "26",
                    "Assists": "5",
                    "Deaths": "16",
                    "K/D Ratio": "1.62",
                    "K/R Ratio": "0.93",
                    "Headshots": "14",
                    "Headshots %": "53.8",
                    "ADR": "108.3",
                    "MVPs": "4",
                    "Triple Kills": "2",
                    "Quadro Kills": "1",
                    "Penta Kills": "0",
                    "Result": "1",
                },
            }
        ],
    }
    extended = {
        "players": [
            {
                "nickname": "NiKo",
                "entry_success_pct": 60.0,
                "trade_kills": 4,
                "trade_deaths": 2,
                "utility_damage": 142,
                "enemies_flashed": 8,
                "flash_assists": 2,
                "1v1_wins": 1,
                "1v2_wins": 0,
                "hltv_rating": 1.35,
            }
        ]
    }
    lifetime = {
        "matches": 500,
        "wins": 290,
        "kd": 1.35,
        "hs_pct": 51.0,
        "mvps": 150,
        "win_rate": 58.0,
    }

    result = aggregate_player_data(
        "NiKo",
        match_stats=match_stats,
        extended=extended,
        lifetime=lifetime,
    )

    assert result["nickname"] == "NiKo"
    assert result["map"] == "de_mirage"
    assert result["score"] == "16-12"
    assert result["kills"] == 26
    assert result["assists"] == 5
    assert result["deaths"] == 16
    assert result["kd"] == 1.62
    assert result["adr"] == 108.3
    assert result["hs_pct"] == 53.8
    assert result["mvps"] == 4
    assert result["triple_kills"] == 2
    assert result["quadro_kills"] == 1
    assert result["won"] is True
    assert result["entry_success_pct"] == 60.0
    assert result["trade_kills"] == 4
    assert result["utility_damage"] == 142
    assert result["enemies_flashed"] == 8
    assert result["clutch_1v1_wins"] == 1
    assert result["hltv_rating"] == 1.35
    assert result["lifetime_kd"] == 1.35
    assert result["lifetime_hs_pct"] == 51.0
    assert result["lifetime_win_rate"] == 58.0
    assert result["lifetime_matches"] == 500


def test_aggregate_no_extended():
    match_stats = {
        "map": "de_mirage",
        "score": "16-12",
        "players": [
            {
                "player_id": "p1",
                "nickname": "NiKo",
                "team_name": "TeamA",
                "team_score": "16",
                "won": True,
                "stats": {"Kills": "20", "Assists": "5", "Deaths": "15"},
            }
        ],
    }

    result = aggregate_player_data("NiKo", match_stats=match_stats, extended=None, lifetime=None)
    assert result["kills"] == 20
    assert result["entry_success_pct"] == 0.0
    assert result["hltv_rating"] == 0.0
    assert result["lifetime_matches"] == 0
