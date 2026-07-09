from bot.rating import (
    compute_rating,
    estimate_rating,
    win_probability,
    team_win_probability,
    required_score_to_win,
)


def test_compute_rating_negative():
    assert compute_rating({}, -2.0) == 500.0


def test_compute_rating_zero():
    assert compute_rating({}, 0.0) == 1000.0


def test_compute_rating_positive():
    assert compute_rating({}, 1.0) == 1250.0


def test_compute_rating_max():
    assert compute_rating({}, 2.0) == 1500.0


def test_estimate_rating_equal():
    assert estimate_rating(0.0, 1.0, 70) == 1000.0


def test_estimate_rating_good():
    assert estimate_rating(1.0, 1.2, 85) == 1250.0


def test_win_probability_equal():
    assert win_probability(1000, 1000) == 50.0


def test_win_probability_higher():
    wp = win_probability(1200, 1000)
    assert wp > 50.0
    assert wp < 80.0


def test_win_probability_lower():
    wp = win_probability(1000, 1200)
    assert wp < 50.0


def test_team_win_probability():
    assert team_win_probability(1100, 1000) > 50.0


def test_team_win_probability_equal():
    assert team_win_probability(1000, 1000) == 50.0


def test_required_score_to_win_below():
    need = required_score_to_win(0.0, 1200, 1000)
    assert need > 0.0


def test_required_score_to_win_already_above():
    need = required_score_to_win(1.0, 1000, 1250)
    assert need >= 0.0
