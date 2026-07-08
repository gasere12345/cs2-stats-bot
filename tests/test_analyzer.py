from bot.analyzer import compute_usefulness, describe_usefulness, describe_skill_level


def test_compute_usefulness_carry():
    data = {
        "kd": 2.0, "adr": 120.0, "kpr": 1.2, "hs_pct": 60.0,
        "mvps": 6, "triple_kills": 3, "quadro_kills": 1, "penta_kills": 0,
        "entry_success_pct": 85.0, "first_kills": 6, "first_deaths": 1,
        "kast": 95.0,
    }
    score = compute_usefulness(data)
    assert score >= 1.5


def test_compute_usefulness_avg():
    data = {
        "kd": 1.1, "adr": 70.0, "kpr": 0.6, "hs_pct": 35.0,
        "mvps": 1, "triple_kills": 0, "quadro_kills": 0, "penta_kills": 0,
        "entry_success_pct": 50.0, "first_kills": 3, "first_deaths": 3,
        "kast": 60.0,
    }
    score = compute_usefulness(data)
    assert -0.5 <= score <= 0.5


def test_compute_usefulness_weak():
    data = {
        "kd": 0.3, "adr": 30.0, "kpr": 0.3, "hs_pct": 15.0,
        "mvps": 0, "triple_kills": 0, "quadro_kills": 0, "penta_kills": 0,
        "entry_success_pct": 20.0, "first_kills": 1, "first_deaths": 4,
        "kast": 40.0,
    }
    score = compute_usefulness(data)
    assert score <= -0.5


def test_compute_usefulness_good():
    data = {
        "kd": 1.2, "adr": 80.0, "kpr": 0.75, "hs_pct": 50.0,
        "mvps": 2, "triple_kills": 1, "quadro_kills": 0, "penta_kills": 0,
        "entry_success_pct": 55.0, "first_kills": 6, "first_deaths": 4,
        "kast": 72.0,
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
