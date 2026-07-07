import pytest
from bot.parser import parse_faceit_url


def test_bot_command_parse():
    text = "/faceit https://www.faceit.com/en/cs2/room/abc123 NiKo"
    parts = text.split(maxsplit=2)
    assert len(parts) == 3
    assert parts[0] == "/faceit"
    match_id = parse_faceit_url(parts[1])
    assert match_id == "abc123"
    assert parts[2] == "NiKo"


def test_bot_command_parse_no_lang():
    text = "/faceit https://faceit.com/cs2/room/def456 s1mple"
    parts = text.split(maxsplit=2)
    match_id = parse_faceit_url(parts[1])
    assert match_id == "def456"
    assert parts[2] == "s1mple"


def test_format_aggregated_output():
    from bot.formatter import format_stats
    from bot.analyzer import compute_usefulness

    data = {
        "nickname": "NiKo",
        "skill_level": 10,
        "elo": 2500,
        "map": "de_mirage",
        "score": "13-16",
        "won": False,
        "kills": 22,
        "assists": 3,
        "deaths": 18,
        "kd": 1.22,
        "kpr": 0.76,
        "adr": 92.4,
        "hs": 10,
        "hs_pct": 45.5,
        "mvps": 3,
        "triple_kills": 1,
        "quadro_kills": 0,
        "penta_kills": 0,
        "entry_success_pct": 55.0,
        "opening_kills": 3,
        "opening_deaths": 2,
        "trade_kills": 4,
        "trade_deaths": 3,
        "trade_ratio": 1.33,
        "utility_damage": 120.0,
        "enemies_flashed": 7,
        "flash_assists": 1,
        "clutch_1v1_wins": 1,
        "clutch_1v2_wins": 0,
        "hltv_rating": 1.25,
        "rws": 11.5,
        "lifetime_matches": 350,
        "lifetime_wins": 185,
        "lifetime_kd": 1.28,
        "lifetime_hs_pct": 48.0,
        "lifetime_adr": 88.0,
        "lifetime_win_rate": 52.9,
        "lifetime_mvps": 120,
    }
    score = compute_usefulness(data)
    result = format_stats(data, score)
    assert "NiKo" in result
    assert "de_mirage" in result
    assert "13-16" in result
    assert "1.22" in result
    assert "Carry" in result or "Good" in result or "Average" in result
