from typing import Any
import httpx

from bot.config import CS2_SPACE_BASE_URL, FACEIT_TIMEOUT_SEC


class Cs2SpaceClient:
    def __init__(self, api_key: str, base_url: str = CS2_SPACE_BASE_URL):
        self._api_key = api_key
        self._base_url = base_url
        self._headers = {
            "x-api-key": api_key,
            "Accept": "application/json",
        }
        self._client = httpx.AsyncClient(timeout=FACEIT_TIMEOUT_SEC)

    async def close(self):
        await self._client.aclose()

    async def _get(self, path: str) -> dict[str, Any] | None:
        if not self._api_key:
            return None
        resp = await self._client.get(
            f"{self._base_url}{path}",
            headers=self._headers,
        )
        if resp.status_code in (401, 403, 404):
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_profile(self, steam_id: str) -> dict[str, Any] | None:
        return await self._get(f"/profile/{steam_id}")
