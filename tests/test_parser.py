import pytest
from bot.parser import parse_faceit_url


def test_valid_faceit_match_url():
    match_id = parse_faceit_url("https://www.faceit.com/en/cs2/room/abc123-def456")
    assert match_id == "abc123-def456"


def test_valid_faceit_match_url_no_lang():
    match_id = parse_faceit_url("https://www.faceit.com/cs2/room/abc123")
    assert match_id == "abc123"


def test_with_trailing_slash():
    match_id = parse_faceit_url("https://faceit.com/en/cs2/room/abc123/")
    assert match_id == "abc123"


def test_invalid_url():
    match_id = parse_faceit_url("https://youtube.com/watch?v=123")
    assert match_id is None


def test_empty_string():
    match_id = parse_faceit_url("")
    assert match_id is None


def test_just_match_id():
    match_id = parse_faceit_url("abc123-def456")
    assert match_id == "abc123-def456"
