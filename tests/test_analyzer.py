from bot.analyzer import compute_usefulness, describe_usefulness, describe_skill_level


def test_compute_usefulness_carry():
    data = {
        "kd": 2.0,
        "adr": 120.0,
        "kpr": 1.2,
        "hs_pct": 60.0,
        "mvps": 6,
        "triple_kills": 3,
        "quadro_kills": 1,
        "penta_kills": 0,
        "entry_success_pct": 65.0,
        "trade_kills": 5,
        "trade_deaths": 1,
        "utility_damage": 180.0,
        "enemies_flashed": 12,
        "clutch_1v1_wins": 2,
        "clutch_1v2_wins": 1,
        "hltv_rating": 1.5,
        "has_extended_data": True,
    }
    score = compute_usefulness(data)
    assert score >= 1.5


def test_compute_usefulness_avg():
    data = {
        "kd": 1.0,
        "adr": 75.0,
        "kpr": 0.7,
        "hs_pct": 40.0,
        "mvps": 1,
        "triple_kills": 0,
        "quadro_kills": 0,
        "penta_kills": 0,
        "entry_success_pct": 45.0,
        "trade_kills": 2,
        "trade_deaths": 2,
        "utility_damage": 80.0,
        "enemies_flashed": 5,
        "clutch_1v1_wins": 0,
        "clutch_1v2_wins": 0,
        "hltv_rating": 1.0,
        "has_extended_data": True,
    }
    score = compute_usefulness(data)
    assert -0.5 <= score <= 0.5


def test_compute_usefulness_weak():
    data = {
        "kd": 0.3,
        "adr": 30.0,
        "kpr": 0.3,
        "hs_pct": 15.0,
        "mvps": 0,
        "triple_kills": 0,
        "quadro_kills": 0,
        "penta_kills": 0,
        "entry_success_pct": 20.0,
        "trade_kills": 0,
        "trade_deaths": 5,
        "utility_damage": 10.0,
        "enemies_flashed": 0,
        "clutch_1v1_wins": 0,
        "clutch_1v2_wins": 0,
        "hltv_rating": 0.5,
        "has_extended_data": True,
    }
    score = compute_usefulness(data)
    assert score <= -0.5


def test_compute_usefulness_no_extended():
    data = {
        "kd": 1.2,
        "adr": 80.0,
        "kpr": 0.75,
        "hs_pct": 50.0,
        "mvps": 2,
        "triple_kills": 1,
        "quadro_kills": 0,
        "penta_kills": 0,
    }
    score = compute_usefulness(data)
    assert score >= 0.0


def test_describe_usefulness():
    assert "Carry" in describe_usefulness(1.8)
    assert "Good" in describe_usefulness(0.8)
    assert "Average" in describe_usefulness(0.0)
    assert "Weak" in describe_usefulness(-0.8)
    assert "Throw" in describe_usefulness(-1.8)


def test_describe_skill_level():
    desc = describe_skill_level(10, 2500, 60.0)
    assert "Elite" in desc or "Pro" in desc

    desc = describe_skill_level(3, 700, 40.0)
    assert "Beginner" in desc or "Average" in desc
