from typing import Any
from bot.analyzer import describe_usefulness, describe_skill_level


def _fmt_pct(val: float) -> str:
    if val > 1:
        return f"{val:.1f}%"
    return f"{val * 100:.1f}%"


def format_stats(agg: dict[str, Any], score: float) -> str:
    team_emoji = "🟢" if agg["won"] else "🔴"
    lines = [
        f"<b>{agg['nickname']}</b> {team_emoji}",
        f"📍 {agg['map']}  |  {agg['score']}",
        "",
        f"<b>Боевые</b>",
        f"K/D: {agg['kd']}  |  ADR: {agg['adr']}  |  KPR: {agg['kpr']}",
        f"HS: {agg['hs']} ({_fmt_pct(agg['hs_pct'])})",
        f"MVPs: {agg['mvps']}  |  Триплы/Квадры/Пенты: {agg['triple_kills']}/{agg['quadro_kills']}/{agg['penta_kills']}",
    ]

    if agg["entry_success_pct"] > 0 or agg["trade_kills"] > 0:
        lines += [
            "",
            f"<b>⚔️ Вход/Трейд</b>",
            f"Entry успех: {_fmt_pct(agg['entry_success_pct'])}  |  ОПН kills: {agg['opening_kills']} / deaths: {agg['opening_deaths']}",
            f"Trade kills: {agg['trade_kills']}  |  Trade deaths: {agg['trade_deaths']}  |  Ratio: {agg['trade_ratio']}",
        ]

    if agg["utility_damage"] > 0 or agg["enemies_flashed"] > 0:
        lines += [
            "",
            f"<b>💣 Утилити</b>",
            f"Урон: {agg['utility_damage']}  |  Flash assists: {agg['flash_assists']}",
            f"Ослеплено врагов: {agg['enemies_flashed']}",
        ]

    if agg["clutch_1v1_wins"] > 0 or agg["clutch_1v2_wins"] > 0:
        lines += [
            "",
            f"<b>🔥 Клатчи</b>",
            f"1v1: {agg['clutch_1v1_wins']}  |  1v2: {agg['clutch_1v2_wins']}",
        ]

    if agg["hltv_rating"] > 0:
        lines += [
            "",
            f"<b>Рейтинг HLTV</b>",
            f"Rating: {agg['hltv_rating']}  |  RWS: {agg['rws']}",
        ]

    lines += [
        "",
        f"<b>📊 Карьерные (lifetime)</b>",
        f"Матчей: {agg['lifetime_matches']}  |  Побед: {agg['lifetime_wins']} ({_fmt_pct(agg['lifetime_win_rate'])})",
        f"Ср. K/D: {agg['lifetime_kd']}  |  HS%: {_fmt_pct(agg['lifetime_hs_pct'])}  |  ADR: {agg['lifetime_adr']}",
        f"Тимплейты (faceit): {describe_skill_level(agg['skill_level'], agg['elo'], agg['lifetime_win_rate'])}",
    ]

    lines += [
        "",
        f"<b>{describe_usefulness(score)}</b> ({score})",
    ]

    return "\n".join(lines)
