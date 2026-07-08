from typing import Any
from bot.analyzer import describe_usefulness, describe_skill_level


def _fmt_pct(val: float) -> str:
    if val > 1:
        return f"{val:.1f}%"
    return f"{val * 100:.1f}%"


def _diff(val: float, lifetime_val: float) -> str:
    if lifetime_val == 0:
        return ""
    d = val - lifetime_val
    if d > 0:
        return f" (+{d:.1f})"
    if d < 0:
        return f" ({d:.1f})"
    return ""


def _result_line(won: bool, score: str) -> str:
    result = "🏆 Победа" if won else "💀 Поражение"
    return f"{result}  |  {score}"


def format_summary(agg: dict[str, Any], score: float) -> str:
    lines = [
        f"<b>{agg['nickname']}</b>",
        _result_line(agg["won"], agg["score"]),
        f"📍 {agg['map']}",
        "",
        f"<b>🎯 Боевые</b>",
        f"K/D  {agg['kd']:.2f}{_diff(agg['kd'], agg['lifetime_kd'])}  |  "
        f"ADR  {agg['adr']}{_diff(agg['adr'], agg['lifetime_adr'])}  |  "
        f"KPR  {agg['kpr']:.2f}",
        f"HS  {agg['hs']} ({_fmt_pct(agg['hs_pct'])})  |  "
        f"MVPs  {agg['mvps']}  |  "
        f"Triple/Quad/Penta  {agg['triple_kills']}/{agg['quadro_kills']}/{agg['penta_kills']}",
    ]

    extras = []
    if agg.get("kast"):
        extras.append(f"KAST  {_fmt_pct(agg['kast'])}")
    if agg["first_kills"] or agg["first_deaths"]:
        extras.append(f"First kills  {agg['first_kills']}  |  deaths  {agg['first_deaths']}")
    if agg.get("utility_kills"):
        extras.append(f"Utility kills  {agg['utility_kills']}")
    if extras:
        lines += ["", "<b>📊 Дополнительно</b>"] + extras

    if agg.get("lifetime_matches"):
        lines += [
            "",
            f"<b>📈 Карьера</b>",
            f"Матчей  {agg['lifetime_matches']}  |  "
            f"Побед  {agg['lifetime_wins']} ({_fmt_pct(agg['lifetime_win_rate'])})",
            f"K/D  {agg['lifetime_kd']}  |  "
            f"ADR  {agg['lifetime_adr']}  |  "
            f"HS  {_fmt_pct(agg['lifetime_hs_pct'])}",
            describe_skill_level(agg['skill_level'], agg['elo'], agg['lifetime_win_rate']),
        ]

    lines += [
        "",
        f"<b>{describe_usefulness(score)}</b> ({score})",
    ]

    return "\n".join(lines)


def format_career(agg: dict[str, Any]) -> str:
    if not agg.get("lifetime_matches"):
        return f"<b>📈 Карьера {agg['nickname']}</b>\n\nНет данных о карьере."

    lines = [
        f"<b>📈 Карьера {agg['nickname']}</b>",
        f"Уровень  {agg['skill_level']}  |  ELO  {agg['elo']}",
        "",
        f"<b>Основное</b>",
        f"Матчей  {agg['lifetime_matches']}  |  "
        f"Побед  {agg['lifetime_wins']}  |  "
        f"Поражений  {agg['lifetime_matches'] - agg['lifetime_wins']}",
        f"Win Rate  {_fmt_pct(agg['lifetime_win_rate'])}",
        "",
        f"<b>Средние</b>",
        f"K/D  {agg['lifetime_kd']:.2f}  |  "
        f"ADR  {agg['lifetime_adr']}  |  "
        f"HS  {_fmt_pct(agg['lifetime_hs_pct'])}",
        f"K/R  {agg['lifetime_kr']:.2f}  |  "
        f"MVPs  {agg['lifetime_mvps']}",
    ]
    if agg.get("lifetime_win_streak"):
        lines.append(f"Лучшая серия  {agg['lifetime_win_streak']} побед")
    leetify = agg.get("leetify_ratings")
    if leetify:
        parts = []
        if leetify.get("aim") is not None:
            parts.append(f"Aim  {leetify['aim']}")
        if leetify.get("positioning") is not None:
            parts.append(f"Pos  {leetify['positioning']}")
        if leetify.get("utility") is not None:
            parts.append(f"Util  {leetify['utility']}")
        if parts:
            lines += ["", "<b>🤖 Leetify ratings</b>", "  |  ".join(parts)]
    lines.append(f"\n{describe_skill_level(agg['skill_level'], agg['elo'], agg['lifetime_win_rate'])}")
    return "\n".join(lines)


def format_match_detail(agg: dict[str, Any]) -> str:
    lines = [
        f"<b>🔫 Матч {agg['nickname']}</b>",
        _result_line(agg["won"], agg["score"]),
        f"📍 {agg['map']}",
        "",
        f"<b>Боевые</b>",
        f"K  {agg['kills']}  |  A  {agg['assists']}  |  D  {agg['deaths']}",
        f"K/D  {agg['kd']:.2f}  |  ADR  {agg['adr']}  |  KPR  {agg['kpr']:.2f}",
        f"HS  {agg['hs']} ({_fmt_pct(agg['hs_pct'])})  |  MVPs  {agg['mvps']}",
        f"Triple  {agg['triple_kills']}  |  Quadro  {agg['quadro_kills']}  |  Penta  {agg['penta_kills']}",
    ]

    extras = []
    if agg.get("first_kills"):
        extras.append(f"First kills  {agg['first_kills']}")
    if agg.get("first_deaths"):
        extras.append(f"First deaths  {agg['first_deaths']}")
    if agg.get("kast"):
        extras.append(f"KAST  {_fmt_pct(agg['kast'])}")
    if agg.get("utility_kills"):
        extras.append(f"Utility kills  {agg['utility_kills']}")
    if agg.get("smoke_kills"):
        extras.append(f"Smoke kills  {agg['smoke_kills']}")
    if agg.get("flash_kills"):
        extras.append(f"Flash kills  {agg['flash_kills']}")
    if agg.get("flash_assists"):
        extras.append(f"Flash assists  {agg['flash_assists']}")
    if extras:
        lines += ["", "<b>📊 Дополнительно</b>"] + extras

    return "\n".join(lines)


def format_roster(agg: dict[str, Any]) -> str:
    lines = [
        f"<b>👥 Состав матча</b>",
        _result_line(agg["won"], agg["score"]),
        f"📍 {agg['map']}",
        "",
    ]
    if agg["teammates"]:
        lines.append("<b>🤝 Тиммейты</b>")
        for t in agg["teammates"]:
            lines.append(f"  • {t}")
        lines.append("")
    if agg["opponents"]:
        lines.append("<b>👊 Противники</b>")
        for o in agg["opponents"]:
            lines.append(f"  • {o}")
    return "\n".join(lines)
