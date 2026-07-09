from bot.rating import (
    compute_rating,
    estimate_rating,
    win_probability,
    team_win_probability,
    required_rating_to_win,
    required_kd_to_win,
)


def test_compute_rating_base():
    agg = {"elo": 1500}
    assert compute_rating(agg, 0.0) == 1500.0


def test_compute_rating_positive():
    agg = {"elo": 1500}
    assert compute_rating(agg, 1.5) == 1650.0


def test_compute_rating_negative():
    agg = {"elo": 1500}
    assert compute_rating(agg, -1.0) == 1400.0


def test_compute_rating_no_elo():
    agg = {"elo": 0}
    r = compute_rating(agg, 0.5)
    assert r == 1050.0


def test_estimate_rating():
    r = estimate_rating(0.0, 1.0, 70)
    assert r == 1000.0


def test_estimate_rating_good():
    r = estimate_rating(1.0, 1.2, 85)
    assert r > 1000


def test_win_probability_equal():
    assert win_probability(1500, 1500) == 50.0


def test_win_probability_higher():
    wp = win_probability(1700, 1500)
    assert wp > 50.0


def test_win_probability_lower():
    wp = win_probability(1500, 1700)
    assert wp < 50.0


def test_team_win_probability():
    assert team_win_probability(1600, 1500) == 64.0


def test_team_win_probability_equal():
    assert team_win_probability(1500, 1500) == 50.0


def test_required_rating_to_win():
    assert required_rating_to_win(1500, 1550) == 1551.0


def test_required_kd_to_win():
    kd = required_kd_to_win(1500, 1600, 80)
    assert kd > 0


def test_required_kd_below_target():
    # If target <= base, return 0
    kd = required_kd_to_win(1500, 1400, 80)
    assert kd == 0.0
