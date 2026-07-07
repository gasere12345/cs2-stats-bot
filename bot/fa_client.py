from typing import Any
import httpx

from bot.config import FA_BASE_URL, FACEIT_TIMEOUT_SEC


class FaceitAnalyserClient:
    def __init__(self, api_key: str, base_url: str = FA_BASE_URL):
        self._api_key = api_key
        self._base_url = base_url

    async def _get(self, path: str) -> dict[str, Any] | None:
        if not self._api_key:
            return None
        async with httpx.AsyncClient(timeout=FACEIT_TIMEOUT_SEC) as c:
            resp = await c.get(
                f"{self._base_url}{path}",
                params={"key": self._api_key},
                headers={"Accept": "application/json"},
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    async def get_player_extended_stats(self, nickname: str) -> dict[str, Any] | None:
        return await self._get(f"/stats/{nickname}/cs2")

    async def get_match_extended_stats(self, match_id: str) -> dict[str, Any] | None:
        return await self._get(f"/match/{match_id}/cs2")
