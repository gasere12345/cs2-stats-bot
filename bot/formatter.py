from typing import Any
from bot.analyzer import compute_usefulness, describe_usefulness, describe_skill_level
from bot.rating import compute_rating, win_probability, required_rating_to_win, required_kd_to_win


def _fmt_pct(val: float) -> str:
    if val > 1:
        return f"{val:.1f}%"
    return f"{val * 100:.1f}%"


def _fmt(val: Any) -> str:
    if isinstance(val, float):
        return f"{val:.1f}"
    return str(val)


def _diff(val: float, lifetime_val: float) -> str:
    if not lifetime_val:
        return ""
    d = val - lifetime_val
    if abs(d) < 0.01:
        return ""
    arrow = "▲" if d > 0 else "▼"
    return f" {arrow}{abs(d):.1f}"


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
        f"KPR  {agg['kpr']:.2f}{_diff(agg['kpr'], agg['lifetime_kr'])}",
        f"HS  {agg['hs']} ({_fmt_pct(agg['hs_pct'])})  |  "
        f"MVPs  {agg['mvps']}  |  "
        f"Triple/Quad/Penta  {agg['triple_kills']}/{agg['quadro_kills']}/{agg['penta_kills']}",
    ]

    extras = []
    ek = agg.get("entry_success_pct", 0)
    fk = agg.get("first_kills", 0)
    fd = agg.get("first_deaths", 0)
    if fk or fd:
        extras.append(f"Entry  {ek}%  ({fk}W / {fd}L)")
    if agg.get("kast"):
        extras.append(f"KAST  {_fmt_pct(agg['kast'])}")
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

    rating = compute_rating(agg, score)
    lines += [
        "",
        f"📊 <b>Рейтинг:</b> {rating}  |  Usefulness: {score}",
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


def format_roster(agg: dict[str, Any], team_scores: dict[str, Any] | None = None) -> str:
    lines = [
        f"<b>👥 Состав матча</b>",
        _result_line(agg["won"], agg["score"]),
        f"📍 {agg['map']}",
        "",
    ]

    def player_line(nick: str) -> str:
        if not team_scores or nick not in team_scores:
            return f"  • {nick}"
        ps = team_scores[nick]
        s = ps["score"]
        tag = describe_usefulness(s).split(" —")[0]
        return f"  • {nick}  —  {tag} ({s})  |  K/D {ps['kd']:.2f}  ADR {ps['adr']}"

    if agg["teammates"]:
        lines.append(f"<b>🤝 Команда</b>")
        for t in agg["teammates"]:
            lines.append(player_line(t))
        lines.append("")
    if agg["opponents"]:
        lines.append(f"<b>👊 Противники</b>")
        for o in agg["opponents"]:
            lines.append(player_line(o))

    if team_scores:
        nick = agg["nickname"]
        mates = agg["teammates"]
        team_avg = sum(team_scores[n]["score"] for n in mates + [nick] if n in team_scores) / (len(mates) + 1) if mates else 0
        opps = agg["opponents"]
        opp_avg = sum(team_scores[n]["score"] for n in opps if n in team_scores) / len(opps) if opps else 0
        lines += [
            "",
            f"<b>📊 Средний Usefulness по командам</b>",
            f"Ваша  {team_avg:.2f}  |  Противники  {opp_avg:.2f}",
        ]

    return "\n".join(lines)


def format_rating_tab(agg: dict[str, Any], rating_data: dict[str, Any] | None, team_scores: dict[str, Any] | None) -> str:
    if not rating_data:
        return f"<b>📊 Рейтинг {agg['nickname']}</b>\n\nНет данных для расчёта рейтинга."

    pr = rating_data["player_rating"]
    elo = rating_data["player_elo"]
    tar = rating_data["team_avg_rating"]
    oar = rating_data["opp_avg_rating"]
    twp = rating_data["team_win_prob"]
    pwp = rating_data["player_win_prob"]

    lines = [
        f"<b>📊 Рейтинг {agg['nickname']}</b>",
        "",
        f"<b>🎯 Рейтинг игрока:</b> {pr}",
        f"Faceit ELO: {elo}  |  Performance: {pr - elo:+.1f}",
        "",
        f"<b>👥 Средний рейтинг команды:</b> {tar}",
        f"<b>👊 Средний рейтинг противников:</b> {oar}",
        "",
        f"<b>📈 Шанс победы</b>",
        f"Команды: {twp}%",
        f"Игрока: {pwp}%",
    ]

    if pwp < 50:
        needed_rating = required_rating_to_win(pr, oar)
        needed_kd = required_kd_to_win(agg.get("elo", 1000), needed_rating, agg.get("adr", 70))
        lines += [
            "",
            f"<b>⚡ Что нужно для победы</b>",
            f"Нужен рейтинг: {needed_rating} (сейчас {pr})",
            f"Нужный K/D: {needed_kd} (сейчас {agg.get('kd', 0):.2f})",
        ]
    else:
        lines += [
            "",
            f"<b>✅ Твой рейтинг выше среднего противника</b>",
            f"При такой игре шанс победы — {pwp}%",
        ]

    if team_scores:
        lines += ["", "<b>📊 Все игроки (рейтинг)</b>"]
        nick = agg["nickname"]
        mates = agg.get("teammates", [])
        opps = agg.get("opponents", [])
        lines.append("🤝 <b>Команда</b>")
        for n in [nick] + mates:
            if n in team_scores:
                ts = team_scores[n]
                marker = " ← Вы" if n == nick else ""
                lines.append(f"  • {n}{marker} — {ts['rating']}  |  K/D {ts['kd']:.2f}")
        lines.append("")
        lines.append("👊 <b>Противники</b>")
        for n in opps:
            if n in team_scores:
                ts = team_scores[n]
                lines.append(f"  • {n} — {ts['rating']}  |  K/D {ts['kd']:.2f}")

    return "\n".join(lines)
