from typing import Any
import httpx

from bot.config import FACEIT_BASE_URL, FACEIT_TIMEOUT_SEC
from bot.models import FaceitPlayer, FaceitMatch, LifetimeStats


class FaceitClient:
    def __init__(self, api_key: str, base_url: str = FACEIT_BASE_URL):
        self._api_key = api_key
        self._base_url = base_url
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }
        self._client = httpx.AsyncClient(timeout=FACEIT_TIMEOUT_SEC)

    async def close(self):
        await self._client.aclose()

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        resp = await self._client.get(
            f"{self._base_url}{path}",
            params=params,
            headers=self._headers,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def _parse_player(self, data: dict, fallback_nickname: str = "") -> FaceitPlayer | None:
        if data is None:
            return None
        cs2 = (data.get("games") or {}).get("cs2") or {}
        return FaceitPlayer(
            player_id=data.get("player_id", ""),
            nickname=data.get("nickname", fallback_nickname),
            country=data.get("country", ""),
            steam_id=cs2.get("game_player_id", ""),
            faceit_url=data.get("faceit_url", ""),
            elo=int(cs2.get("faceit_elo", 0)),
            skill_level=int(cs2.get("skill_level", 0)),
        )

    async def get_player_by_nickname(self, nickname: str) -> FaceitPlayer | None:
        data = await self._get("/players", params={"nickname": nickname, "game": "cs2"})
        return self._parse_player(data, nickname)

    async def get_player_by_id(self, player_id: str) -> FaceitPlayer | None:
        data = await self._get(f"/players/{player_id}")
        return self._parse_player(data)

    async def get_match(self, match_id: str) -> FaceitMatch | None:
        data = await self._get(f"/matches/{match_id}")
        if data is None:
            return None
        results = data.get("results") or {}
        score_raw = (results.get("score") or {})
        score: dict[str, int] = {}
        for k, v in score_raw.items():
            score[k] = int(v) if v is not None else 0
        voting = data.get("voting") or {}
        map_pick = (voting.get("map") or {}).get("pick") or []
        map_name = map_pick[0] if map_pick else (data.get("map") or {}).get("name", "")
        return FaceitMatch(
            match_id=data.get("match_id", ""),
            map=map_name,
            status=data.get("status", ""),
            score=score,
            region=data.get("region", ""),
            faceit_url=data.get("faceit_url", ""),
        )

    async def get_match_stats(self, match_id: str) -> dict[str, Any]:
        data = await self._get(f"/matches/{match_id}/stats")
        if data is None:
            return {"map": "", "score": "", "players": []}
        rounds = (data.get("rounds") or [])
        if not rounds:
            return {"map": "", "score": "", "players": []}
        round_data = rounds[0]
        round_stats = round_data.get("round_stats") or {}
        players_out = []
        for team in round_data.get("teams") or []:
            team_stats = team.get("team_stats") or {}
            team_id = team.get("team_id", "")
            for player in team.get("players") or []:
                players_out.append({
                    "player_id": player.get("player_id", ""),
                    "nickname": player.get("nickname", ""),
                    "team_id": team_id,
                    "team_name": team_stats.get("Team", ""),
                    "team_score": team_stats.get("Final Score", ""),
                    "won": team_stats.get("Win") == "1",
                    "stats": player.get("player_stats") or {},
                })
        return {
            "map": round_stats.get("Map", ""),
            "score": round_stats.get("Score", ""),
            "rounds": round_stats.get("Rounds", ""),
            "players": players_out,
        }

    async def get_lifetime_stats(self, player_id: str) -> LifetimeStats | None:
        data = await self._get(f"/players/{player_id}/stats/cs2")
        if data is None:
            return None
        life = data.get("lifetime") or {}
        matches = self._to_int(life.get("Matches"))
        wins = self._to_int(life.get("Wins"))
        losses = matches - wins if matches and wins is not None else 0

        mvps = self._to_int(
            life.get("MVPs")
            or life.get("MVP")
            or life.get("Total MVPs")
            or life.get("mvps")
        )
        if mvps is None:
            mvps = self._mvps_from_segments(data.get("segments") or [])

        kr = self._pick_float(life, ["Average K/R Ratio", "K/R Ratio", "Average K/R", "K/R", "KPR", "kr"], max_val=3.0)
        if kr is None:
            kr = self._kr_from_segments(data.get("segments") or [])

        kd = self._pick_float(life, ["Average K/D Ratio", "K/D Ratio"], max_val=5.0)
        adr = self._pick_float(life, ["Average Damage per Round", "ADR"], max_val=200.0)
        hs_pct = self._pick_float(life, ["Average Headshots %", "Headshots %"], max_val=100.0)

        return LifetimeStats(
            matches=matches or 0,
            wins=wins or 0,
            losses=losses,
            win_rate=self._to_float(life.get("Win Rate %")) or 0.0,
            kd=kd or 0.0,
            adr=adr or 0.0,
            hs_pct=hs_pct or 0.0,
            kills=self._to_int(life.get("Total Kills")) or 0,
            deaths=self._to_int(life.get("Total Deaths")) or 0,
            assists=self._to_int(life.get("Total Assists")) or 0,
            mvps=mvps or 0,
            kr=kr or 0.0,
            longest_win_streak=self._to_int(life.get("Longest Win Streak")) or 0,
            raw=life,
            segments=data.get("segments") or [],
        )

    async def get_match_history(self, player_id: str, limit: int = 20, offset: int = 0) -> list[dict[str, Any]]:
        data = await self._get(
            f"/players/{player_id}/games/cs2/stats",
            params={"limit": min(limit, 100), "offset": offset},
        )
        if data is None:
            return []
        items = data.get("items") or []
        return [it.get("stats") or {} for it in items if isinstance(it, dict)]

    def _mvps_from_segments(self, segments: list[dict[str, Any]]) -> int | None:
        total = 0
        found = False
        for seg in segments:
            s = seg.get("stats") or {}
            mvp = self._to_int(s.get("MVPs") or s.get("mvps"))
            if mvp is not None:
                total += mvp
                found = True
        return total if found else None

    def _kr_from_segments(self, segments: list[dict[str, Any]]) -> float | None:
        total_weight = 0
        weighted_sum = 0.0
        for seg in segments:
            s = seg.get("stats") or {}
            kr_val = self._pick_float(s, ["Average K/R Ratio", "K/R Ratio", "Average K/R", "K/R"], max_val=3.0)
            seg_matches = self._to_int(s.get("Matches"))
            if kr_val is not None and seg_matches and seg_matches > 0:
                weighted_sum += kr_val * seg_matches
                total_weight += seg_matches
        if total_weight > 0:
            return round(weighted_sum / total_weight, 2)
        return None

    def _to_int(self, val: Any) -> int | None:
        if val is None:
            return None
        try:
            return int(float(str(val).strip()))
        except (TypeError, ValueError):
            return None

    def _to_float(self, val: Any) -> float | None:
        if val is None:
            return None
        try:
            return float(str(val).replace("%", "").strip())
        except (TypeError, ValueError):
            return None

    def _pick_float(self, obj: dict, keys: list[str], max_val: float = 1000.0) -> float | None:
        for key in keys:
            val = self._to_float(obj.get(key))
            if val is not None and -max_val <= val <= max_val:
                return val
        return None
