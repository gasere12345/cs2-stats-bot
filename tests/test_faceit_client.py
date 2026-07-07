import httpx
import pytest
import respx

from bot.faceit_client import FaceitClient
from bot.config import FACEIT_BASE_URL


@pytest.fixture
def client():
    return FaceitClient(api_key="test_key")


@pytest.mark.asyncio
async def test_get_player_by_nickname_success(client: FaceitClient):
    with respx.mock:
        route = respx.get(f"{FACEIT_BASE_URL}/players", params={"nickname": "NiKo", "game": "cs2"})
        route.respond(
            status_code=200,
            json={
                "player_id": "abc123",
                "nickname": "NiKo",
                "country": "BA",
                "faceit_url": "https://faceit.com/en/players/NiKo",
                "games": {
                    "cs2": {
                        "faceit_elo": 2450,
                        "skill_level": 10,
                        "game_player_id": "steam_123",
                        "region": "EU",
                    }
                },
            },
        )

        player = await client.get_player_by_nickname("NiKo")

        assert player.player_id == "abc123"
        assert player.nickname == "NiKo"
        assert player.country == "BA"
        assert player.elo == 2450
        assert player.skill_level == 10
        assert player.steam_id == "steam_123"


@pytest.mark.asyncio
async def test_get_player_not_found(client: FaceitClient):
    with respx.mock:
        route = respx.get(f"{FACEIT_BASE_URL}/players", params={"nickname": "NoOne", "game": "cs2"})
        route.respond(status_code=404)

        player = await client.get_player_by_nickname("NoOne")
        assert player is None


@pytest.mark.asyncio
async def test_get_match_stats_dynamic_fields(client: FaceitClient):
    with respx.mock:
        route = respx.get(f"{FACEIT_BASE_URL}/matches/abc123/stats")
        route.respond(
            status_code=200,
            json={
                "rounds": [
                    {
                        "round_stats": {"Map": "de_mirage", "Score": "16-12", "Rounds": "28"},
                        "teams": [
                            {
                                "team_id": "team_a",
                                "team_stats": {"Team": "TeamA", "Win": "1", "Final Score": "16"},
                                "players": [
                                    {
                                        "player_id": "p1",
                                        "nickname": "NiKo",
                                        "player_stats": {
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
                            },
                            {
                                "team_id": "team_b",
                                "team_stats": {"Team": "TeamB", "Win": "0", "Final Score": "12"},
                                "players": [
                                    {
                                        "player_id": "p2",
                                        "nickname": "Enemy",
                                        "player_stats": {
                                            "Kills": "18",
                                            "Assists": "4",
                                            "Deaths": "20",
                                            "K/D Ratio": "0.90",
                                            "Result": "0",
                                        },
                                    }
                                ],
                            },
                        ],
                    }
                ]
            },
        )

        match_stats = await client.get_match_stats("abc123")
        assert match_stats["map"] == "de_mirage"
        assert match_stats["score"] == "16-12"
        assert len(match_stats["players"]) == 2

        niko = match_stats["players"][0]
        assert niko["nickname"] == "NiKo"
        assert niko["stats"]["Kills"] == "26"
        assert niko["stats"]["ADR"] == "108.3"
        assert niko["stats"]["Triple Kills"] == "2"
        assert niko["team_id"] == "team_a"


@pytest.mark.asyncio
async def test_get_lifetime_stats(client: FaceitClient):
    with respx.mock:
        route = respx.get(f"{FACEIT_BASE_URL}/players/abc123/stats/cs2")
        route.respond(
            status_code=200,
            json={
                "player_id": "abc123",
                "game_id": "cs2",
                "lifetime": {
                    "K/D Ratio": "1.35",
                    "Win Rate %": "58",
                    "Matches": "500",
                    "Wins": "290",
                    "Average Headshots %": "51",
                    "Longest Win Streak": "8",
                    "Total Kills": "12500",
                    "Total Deaths": "9259",
                    "Total Assists": "2500",
                    "Average K/D Ratio": "1.35",
                    "Average Headshots": "51",
                    "MVPs": "150",
                },
                "segments": [],
            },
        )

        stats = await client.get_lifetime_stats("abc123")
        assert stats.matches == 500
        assert stats.wins == 290
        assert stats.losses == 210
        assert stats.kd == 1.35
        assert stats.hs_pct == 51.0
        assert stats.mvps == 150
        assert stats.longest_win_streak == 8


@pytest.mark.asyncio
async def test_get_match_history(client: FaceitClient):
    with respx.mock:
        route = respx.get(
            f"{FACEIT_BASE_URL}/players/abc123/games/cs2/stats",
            params={"limit": 5, "offset": 0},
        )
        route.respond(
            status_code=200,
            json={
                "items": [
                    {
                        "stats": {
                            "Kills": "26",
                            "Deaths": "16",
                            "K/D Ratio": "1.62",
                            "Map": "de_mirage",
                            "Result": "1",
                        }
                    },
                    {
                        "stats": {
                            "Kills": "15",
                            "Deaths": "18",
                            "K/D Ratio": "0.83",
                            "Map": "de_inferno",
                            "Result": "0",
                        }
                    },
                ]
            },
        )

        history = await client.get_match_history("abc123", limit=5)
        assert len(history) == 2
        assert history[0]["Map"] == "de_mirage"
        assert history[1]["Kills"] == "15"


@pytest.mark.asyncio
async def test_get_match_details(client: FaceitClient):
    with respx.mock:
        route = respx.get(f"{FACEIT_BASE_URL}/matches/abc123")
        route.respond(
            status_code=200,
            json={
                "match_id": "abc123",
                "status": "finished",
                "region": "EU",
                "faceit_url": "https://faceit.com/en/cs2/room/abc123",
                "voting": {"map": {"pick": ["de_mirage"]}},
                "results": {"score": {"team_a": 16, "team_b": 12}, "winner": "team_a"},
            },
        )

        match = await client.get_match("abc123")
        assert match.match_id == "abc123"
        assert match.status == "finished"
        assert match.map == "de_mirage"
