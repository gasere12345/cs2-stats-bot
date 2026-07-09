from typing import Any


def _safe_int(val: Any) -> int:
    if val is None:
        return 0
    try:
        return int(float(str(val)))
    except (TypeError, ValueError):
        return 0


def _safe_float(val: Any) -> float:
    if val is None:
        return 0.0
    try:
        return float(str(val).replace("%", "").strip())
    except (TypeError, ValueError):
        return 0.0


def _pick_float(stats: dict, keys: list[str], max_val: float = 1000.0) -> float:
    for key in keys:
        val = stats.get(key)
        if val is not None:
            try:
                f = float(str(val).replace("%", "").strip())
                if -max_val <= f <= max_val:
                    return f
            except (TypeError, ValueError):
                pass
    return 0.0


def aggregate_player_data(
    target_nickname: str,
    match_stats: dict[str, Any] | None,
    extended: dict[str, Any] | None,
    lifetime: dict[str, Any] | None,
    player_info: dict[str, Any] | None = None,
    leetify: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "nickname": target_nickname,
        "skill_level": (player_info or {}).get("skill_level", 0),
        "elo": (player_info or {}).get("elo", 0),
        "map": "",
        "score": "",
        "won": False,
        "kills": 0,
        "assists": 0,
        "deaths": 0,
        "kd": 0.0,
        "kpr": 0.0,
        "adr": 0.0,
        "hs": 0,
        "hs_pct": 0.0,
        "mvps": 0,
        "triple_kills": 0,
        "quadro_kills": 0,
        "penta_kills": 0,
        "result": "",
        "first_kills": 0,
        "first_deaths": 0,
        "kast": 0.0,
        "utility_kills": 0,
        "flash_assists": 0,
        "smoke_kills": 0,
        "flash_kills": 0,
        "lifetime_matches": 0,
        "lifetime_wins": 0,
        "lifetime_kd": 0.0,
        "lifetime_hs_pct": 0.0,
        "lifetime_adr": 0.0,
        "lifetime_win_rate": 0.0,
        "lifetime_mvps": 0,
        "lifetime_kr": 0.0,
        "lifetime_win_streak": 0,
        "leetify_ratings": (leetify or {}).get("recentGameRatings"),
        "all_stats_raw": {},
        "teammates": [],
        "opponents": [],
    }

    target_team_id = None
    if match_stats:
        result["map"] = match_stats.get("map", "")
        result["score"] = match_stats.get("score", "")
        nick_lower = target_nickname.lower()
        for p in match_stats.get("players") or []:
            if p.get("nickname", "").lower() == nick_lower:
                target_team_id = p.get("team_id", "")
                s = p.get("stats") or {}
                result["all_stats_raw"] = s
                result["won"] = p.get("won", False)
                result["kills"] = _safe_int(s.get("Kills"))
                result["assists"] = _safe_int(s.get("Assists"))
                result["deaths"] = _safe_int(s.get("Deaths"))
                result["kd"] = _safe_float(s.get("K/D Ratio"))
                result["kpr"] = _safe_float(s.get("K/R Ratio"))
                result["adr"] = _safe_float(s.get("ADR"))
                result["hs"] = _safe_int(s.get("Headshots"))
                result["hs_pct"] = _safe_float(s.get("Headshots %"))
                result["mvps"] = _safe_int(s.get("MVPs"))
                result["triple_kills"] = _safe_int(s.get("Triple Kills"))
                result["quadro_kills"] = _safe_int(s.get("Quadro Kills"))
                result["penta_kills"] = _safe_int(s.get("Penta Kills"))
                result["result"] = s.get("Result", "")
                result["first_kills"] = _safe_int(s.get("First Kills"))
                result["first_deaths"] = _safe_int(s.get("First Deaths"))
                fk = result["first_kills"]
                fd = result["first_deaths"]
                if fk + fd > 0:
                    result["entry_success_pct"] = round(fk / (fk + fd) * 100, 1)
                result["kast"] = _safe_float(s.get("KAST"))
                result["utility_kills"] = _safe_int(s.get("Utility Kills"))
                result["flash_assists"] = _safe_int(s.get("Flash Assists"))
                result["smoke_kills"] = _safe_int(s.get("Smoke Kills"))
                result["flash_kills"] = _safe_int(s.get("Flash Kills"))
                break
        for p in match_stats.get("players") or []:
            nick = p.get("nickname", "")
            if nick.lower() == nick_lower:
                continue
            if target_team_id and p.get("team_id") == target_team_id:
                result["teammates"].append(nick)
            else:
                result["opponents"].append(nick)

    if lifetime:
        result["lifetime_matches"] = _safe_int(lifetime.get("matches"))
        result["lifetime_wins"] = _safe_int(lifetime.get("wins"))
        result["lifetime_kd"] = _safe_float(lifetime.get("kd"))
        result["lifetime_hs_pct"] = _safe_float(lifetime.get("hs_pct"))
        result["lifetime_adr"] = _safe_float(lifetime.get("adr"))
        result["lifetime_win_rate"] = _safe_float(lifetime.get("win_rate"))
        result["lifetime_mvps"] = _safe_int(lifetime.get("mvps"))
        result["lifetime_kr"] = _safe_float(lifetime.get("kr"))
        result["lifetime_win_streak"] = _safe_int(lifetime.get("longest_win_streak"))
        segments = lifetime.get("segments") or []
        map_stats = []
        for seg in segments:
            if seg.get("type") == "Map":
                stats = seg.get("stats") or {}
                map_stats.append({
                    "name": seg.get("label", ""),
                    "matches": _safe_int(stats.get("Matches")),
                    "wins": _safe_int(stats.get("Wins")),
                    "kd": _pick_float(stats, ["Average K/D Ratio", "K/D Ratio"], 5.0),
                    "adr": _pick_float(stats, ["Average Damage per Round", "ADR"], 200.0),
                    "hs_pct": _pick_float(stats, ["Average Headshots %", "Headshots %"], 100.0),
                    "kpr": _pick_float(stats, ["Average K/R Ratio", "K/R Ratio", "Average K/R", "K/R"], 3.0),
                })
        map_stats.sort(key=lambda x: x["matches"], reverse=True)
        result["map_stats"] = map_stats

    return result
