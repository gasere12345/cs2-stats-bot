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


def aggregate_player_data(
    target_nickname: str,
    match_stats: dict[str, Any] | None,
    extended: dict[str, Any] | None,
    lifetime: dict[str, Any] | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "nickname": target_nickname,
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
        "entry_success_pct": 0.0,
        "opening_kills": 0,
        "opening_deaths": 0,
        "trade_kills": 0,
        "trade_deaths": 0,
        "trade_ratio": 0.0,
        "utility_damage": 0.0,
        "enemies_flashed": 0,
        "flash_assists": 0,
        "clutch_1v1_wins": 0,
        "clutch_1v2_wins": 0,
        "clutch_1v3_wins": 0,
        "rws": 0.0,
        "hltv_rating": 0.0,
        "t_win_rate": 0.0,
        "ct_win_rate": 0.0,
        "ak47_kills": 0,
        "m4_kills": 0,
        "awp_kills": 0,
        "pistol_kills": 0,
        "lifetime_matches": 0,
        "lifetime_wins": 0,
        "lifetime_kd": 0.0,
        "lifetime_hs_pct": 0.0,
        "lifetime_adr": 0.0,
        "lifetime_win_rate": 0.0,
        "lifetime_mvps": 0,
        "lifetime_kr": 0.0,
        "lifetime_win_streak": 0,
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
                break
        for p in match_stats.get("players") or []:
            nick = p.get("nickname", "")
            if nick.lower() == nick_lower:
                continue
            if target_team_id and p.get("team_id") == target_team_id:
                result["teammates"].append(nick)
            else:
                result["opponents"].append(nick)

    if extended:
        for p in extended.get("players") or []:
            if p.get("nickname", "").lower() == target_nickname.lower():
                result["entry_success_pct"] = _safe_float(p.get("entry_success_pct"))
                result["opening_kills"] = _safe_int(p.get("opening_kills"))
                result["opening_deaths"] = _safe_int(p.get("opening_deaths"))
                result["trade_kills"] = _safe_int(p.get("trade_kills"))
                result["trade_deaths"] = _safe_int(p.get("trade_deaths"))
                result["utility_damage"] = _safe_float(p.get("utility_damage"))
                result["enemies_flashed"] = _safe_int(p.get("enemies_flashed"))
                result["flash_assists"] = _safe_int(p.get("flash_assists"))
                result["clutch_1v1_wins"] = _safe_int(p.get("1v1_wins"))
                result["clutch_1v2_wins"] = _safe_int(p.get("1v2_wins"))
                result["clutch_1v3_wins"] = _safe_int(p.get("1v3_wins"))
                result["hltv_rating"] = _safe_float(p.get("hltv_rating"))
        result["t_win_rate"] = _safe_float(extended.get("t_win_rate"))
        result["ct_win_rate"] = _safe_float(extended.get("ct_win_rate"))
        result["rws"] = _safe_float(extended.get("rws"))

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

    if result["trade_kills"] > 0 or result["trade_deaths"] > 0:
        td = result["trade_deaths"] if result["trade_deaths"] > 0 else 1
        result["trade_ratio"] = round(result["trade_kills"] / td, 2)

    return result
