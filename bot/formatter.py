from typing import Any
from bot.analyzer import describe_usefulness, describe_skill_level


def _fmt_pct(val: float) -> str:
    if val > 1:
        return f"{val:.1f}%"
    return f"{val * 100:.1f}%"


def _bar(value: float, max_val: float, width: int = 8) -> str:
    filled = max(0, min(int(value / max_val * width), width))
    return "█" * filled + "░" * (width - filled)


def _diff(val: float, lifetime_val: float) -> str:
    if lifetime_val == 0:
        return ""
    d = val - lifetime_val
    if d > 0:
        return f" (+{d:.1f})"
    if d < 0:
        return f" ({d:.1f})"
    return ""


def format_summary(agg: dict[str, Any], score: float) -> str:
    team_emoji = "🟢" if agg["won"] else "🔴"
    lines = [
        f"<b>{agg['nickname']}</b> {team_emoji}  {agg['map']}",
        f"📋 {agg['score']}",
        "",
        f"<b>🎯 Боевые</b>",
        f"K/D    {_bar(agg['kd'], 2.0)} {agg['kd']:.2f}{_diff(agg['kd'], agg['lifetime_kd'])}",
        f"ADR   {_bar(agg['adr'], 120)} {agg['adr']}{_diff(agg['adr'], agg['lifetime_adr'])}",
        f"KPR   {agg['kpr']:.2f}  |  HS%  {_fmt_pct(agg['hs_pct'])}",
        f"MVPs  {agg['mvps']}  |  Триплы/Квадры/Пенты  {agg['triple_kills']}/{agg['quadro_kills']}/{agg['penta_kills']}",
    ]

    if agg["first_kills"] > 0 or agg["kast"] > 0:
        lines += [
            "",
            f"<b>📊 Дополнительно</b>",
        ]
        if agg.get("kast"):
            lines.append(f"KAST  {_bar(agg['kast'], 100)} {_fmt_pct(agg['kast'])}")
        if agg["first_kills"] or agg["first_deaths"]:
            lines.append(f"Первые киллы: {agg['first_kills']}  |  Смерти: {agg['first_deaths']}")
        if agg.get("utility_kills"):
            lines.append(f"Утилити киллы: {agg['utility_kills']}")

    lines += [
        "",
        f"<b>📈 Карьерные</b>",
        f"Матчей: {agg['lifetime_matches']}  |  Побед: {agg['lifetime_wins']} ({_fmt_pct(agg['lifetime_win_rate'])})",
        f"K/D: {agg['lifetime_kd']}  |  ADR: {agg['lifetime_adr']}  |  HS: {_fmt_pct(agg['lifetime_hs_pct'])}",
        f"Тимплейты: {describe_skill_level(agg['skill_level'], agg['elo'], agg['lifetime_win_rate'])}",
    ]

    lines += [
        "",
        f"<b>{describe_usefulness(score)}</b> ({score})",
    ]

    return "\n".join(lines)


def format_career(agg: dict[str, Any]) -> str:
    lines = [
        f"<b>📈 Карьера {agg['nickname']}</b>",
        f"Уровень: {agg['skill_level']}  |  ELO: {agg['elo']}",
        "",
        f"<b>Основное</b>",
        f"Матчей: {agg['lifetime_matches']}",
        f"Побед: {agg['lifetime_wins']}  |  Поражений: {agg['lifetime_matches'] - agg['lifetime_wins']}",
        f"Win Rate: {_fmt_pct(agg['lifetime_win_rate'])}  |  {_bar(agg['lifetime_win_rate'], 100)}",
        "",
        f"<b>Средние</b>",
        f"K/D: {agg['lifetime_kd']:.2f}  |  {_bar(agg['lifetime_kd'], 2.0)}",
        f"ADR: {agg['lifetime_adr']}  |  HS%: {_fmt_pct(agg['lifetime_hs_pct'])}",
        f"K/R: {agg['lifetime_kr']:.2f}  |  MVPs: {agg['lifetime_mvps']}",
    ]
    if agg.get("lifetime_win_streak"):
        lines.append(f"Лучшая серия: {agg['lifetime_win_streak']} побед")
    lines.append(f"\n{describe_skill_level(agg['skill_level'], agg['elo'], agg['lifetime_win_rate'])}")
    return "\n".join(lines)


def format_match_detail(agg: dict[str, Any]) -> str:
    lines = [
        f"<b>🔫 Матч {agg['nickname']}</b>",
        f"📍 {agg['map']}  |  {agg['score']}",
        "",
        f"<b>Боевые</b>",
        f"K: {agg['kills']}  |  A: {agg['assists']}  |  D: {agg['deaths']}",
        f"K/D: {agg['kd']:.2f}  |  ADR: {agg['adr']}  |  KPR: {agg['kpr']:.2f}",
        f"HS: {agg['hs']} ({_fmt_pct(agg['hs_pct'])})  |  MVPs: {agg['mvps']}",
        f"Триплы: {agg['triple_kills']}  |  Квадры: {agg['quadro_kills']}  |  Пенты: {agg['penta_kills']}",
    ]

    extras = []
    if agg.get("first_kills"):
        extras.append(f"Первые киллы: {agg['first_kills']}")
    if agg.get("first_deaths"):
        extras.append(f"Первые смерти: {agg['first_deaths']}")
    if agg.get("kast"):
        extras.append(f"KAST: {_fmt_pct(agg['kast'])}")
    if agg.get("utility_kills"):
        extras.append(f"Утилити киллы: {agg['utility_kills']}")
    if agg.get("smoke_kills"):
        extras.append(f"Smoke киллы: {agg['smoke_kills']}")
    if agg.get("flash_kills"):
        extras.append(f"Flash киллы: {agg['flash_kills']}")
    if agg.get("flash_assists"):
        extras.append(f"Flash assists: {agg['flash_assists']}")
    if extras:
        lines += ["", "<b>📊 Дополнительно</b>"] + extras

    return "\n".join(lines)


format_stats = format_summary


def format_roster(agg: dict[str, Any]) -> str:
    team_emoji = "🟢" if agg["won"] else "🔴"
    lines = [
        f"<b>👥 Состав матча</b> {team_emoji}",
        f"📍 {agg['map']}  |  {agg['score']}",
        "",
    ]
    if agg["teammates"]:
        lines.append(f"<b>🤝 Тиммейты</b>")
        for t in agg["teammates"]:
            lines.append(f"  • {t}")
        lines.append("")
    if agg["opponents"]:
        lines.append(f"<b>👊 Противники</b>")
        for o in agg["opponents"]:
            lines.append(f"  • {o}")
    return "\n".join(lines)
