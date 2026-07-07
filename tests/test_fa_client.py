import pytest
import respx

from bot.fa_client import FaceitAnalyserClient
from bot.config import FA_BASE_URL


@pytest.fixture
def client():
    return FaceitAnalyserClient(api_key="fa_test_key")


@pytest.mark.asyncio
async def test_get_player_extended_stats(client: FaceitAnalyserClient):
    with respx.mock:
        route = respx.get(f"{FA_BASE_URL}/stats/NiKo/cs2", params={"key": "fa_test_key"})
        route.respond(
            status_code=200,
            json={
                "nickname": "NiKo",
                "elo": 2450,
                "level": 10,
                "opening_duels": {
                    "entry_attempts": 120,
                    "entry_success_pct": 54.2,
                    "opening_kills": 65,
                    "opening_deaths": 55,
                },
                "trades": {
                    "trade_kills": 48,
                    "trade_deaths": 32,
                    "trade_ratio": 1.5,
                },
                "clutches": {
                    "1v1_wins": 12,
                    "1v1_losses": 8,
                    "1v2_wins": 4,
                    "1v2_losses": 10,
                    "1v3_wins": 1,
                    "1v3_losses": 8,
                },
                "utility": {
                    "utility_damage_per_round": 28.4,
                    "enemies_flashed": 85,
                    "flash_assists": 12,
                },
                "weapons": {
                    "ak47_kills": 320,
                    "m4_kills": 180,
                    "awp_kills": 90,
                    "pistol_kills": 120,
                    "knife_kills": 2,
                },
                "per_side": {
                    "t_win_rate": 55.0,
                    "ct_win_rate": 61.0,
                },
                "rws": 12.5,
                "hltv_rating": 1.18,
            },
        )

        stats = await client.get_player_extended_stats("NiKo")
        assert stats is not None
        assert stats["nickname"] == "NiKo"
        assert stats["opening_duels"]["entry_success_pct"] == 54.2
        assert stats["trades"]["trade_ratio"] == 1.5
        assert stats["clutches"]["1v1_wins"] == 12
        assert stats["utility"]["utility_damage_per_round"] == 28.4
        assert stats["rws"] == 12.5


@pytest.mark.asyncio
async def test_get_player_not_found(client: FaceitAnalyserClient):
    with respx.mock:
        route = respx.get(f"{FA_BASE_URL}/stats/NoOne/cs2", params={"key": "fa_test_key"})
        route.respond(status_code=404)

        stats = await client.get_player_extended_stats("NoOne")
        assert stats is None


@pytest.mark.asyncio
async def test_get_match_extended_stats(client: FaceitAnalyserClient):
    with respx.mock:
        route = respx.get(
            f"{FA_BASE_URL}/match/abc123/cs2",
            params={"key": "fa_test_key"},
        )
        route.respond(
            status_code=200,
            json={
                "match_id": "abc123",
                "map": "de_mirage",
                "players": [
                    {
                        "nickname": "NiKo",
                        "opening_kills": 3,
                        "opening_deaths": 2,
                        "entry_success_pct": 60.0,
                        "trade_kills": 4,
                        "trade_deaths": 2,
                        "utility_damage": 142,
                        "enemies_flashed": 8,
                        "flash_assists": 2,
                        "1v1_wins": 1,
                        "1v2_wins": 0,
                        "hltv_rating": 1.35,
                    },
                    {
                        "nickname": "Enemy",
                        "opening_kills": 1,
                        "opening_deaths": 3,
                        "entry_success_pct": 25.0,
                        "trade_kills": 1,
                        "trade_deaths": 3,
                        "utility_damage": 56,
                        "enemies_flashed": 3,
                        "flash_assists": 0,
                        "1v1_wins": 0,
                        "1v2_wins": 0,
                        "hltv_rating": 0.85,
                    },
                ],
            },
        )

        match_stats = await client.get_match_extended_stats("abc123")
        assert match_stats is not None
        assert match_stats["map"] == "de_mirage"
        assert len(match_stats["players"]) == 2
        assert match_stats["players"][0]["nickname"] == "NiKo"
        assert match_stats["players"][0]["entry_success_pct"] == 60.0
        assert match_stats["players"][0]["trade_kills"] == 4
