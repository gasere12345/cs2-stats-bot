from typing import Any
from bot.analyzer import compute_usefulness, describe_usefulness, describe_skill_level
from bot.rating import compute_rating, required_score_to_win


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
    elo = agg.get("elo", 0)
    elo_part = f"  |  Faceit ELO: {elo}" if elo else ""
    lines += [
        "",
        f"📊 <b>Рейтинг в матче:</b> {rating}{elo_part}",
    ]

    lines += [
        "",
        f"<b>{describe_usefulness(score)}</b> ({score})",
    ]

    return "\n".join(lines)


def _fmt_map_stats(agg: dict[str, Any]) -> str:
    maps = agg.get("map_stats") or []
    if not maps:
        return ""
    lines = ["", "<b>📊 По картам (топ-5):</b>"]
    for m in maps[:5]:
        name = m["name"]
        if not name:
            continue
        matches = m["matches"]
        kd = m["kd"]
        adr = m["adr"]
        wr = round(m["wins"] / matches * 100, 1) if matches and m["wins"] else 0
        kd_str = f"{kd:.2f}" if kd else "—"
        adr_str = f"{adr}" if adr else "—"
        win_str = f"{wr}%" if wr else "—"
        m_word = "матч" if matches == 1 else "матчей" if 2 <= matches <= 4 else "матчей"
        lines.append(f"  {name:<12} — {matches} {m_word}, K/D {kd_str}, ADR {adr_str}, Win {win_str}")
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
    map_block = _fmt_map_stats(agg)
    if map_block:
        lines.append(map_block)
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


def format_profile(agg: dict[str, Any]) -> str:
    if not agg.get("lifetime_matches"):
        return f"<b>👤 Профиль {agg['nickname']}</b>\n\nНет данных о карьере."

    lines = [
        f"<b>👤 Профиль {agg['nickname']}</b>",
        f"Страна: {agg.get('country', '—').upper()}  |  "
        f"Уровень: {agg['skill_level']}  |  "
        f"ELO: {agg['elo']}",
        f"🔗 <a href='https://www.faceit.com/en/players/{agg['nickname']}'>Faceit</a>",
        "",
        f"<b>📈 Карьера</b>",
        f"Матчей  {agg['lifetime_matches']}  |  "
        f"Побед  {agg['lifetime_wins']}  |  "
        f"Поражений  {agg['lifetime_matches'] - agg['lifetime_wins']}",
        f"Win Rate  {_fmt_pct(agg['lifetime_win_rate'])}",
    ]
    if agg.get("lifetime_win_streak"):
        lines.append(f"Лучшая серия  {agg['lifetime_win_streak']} побед")
    lines += [
        "",
        f"<b>Средние</b>",
        f"K/D  {agg['lifetime_kd']:.2f}  |  "
        f"ADR  {agg['lifetime_adr']}  |  "
        f"HS  {_fmt_pct(agg['lifetime_hs_pct'])}",
        f"MVPs  {agg['lifetime_mvps']}  |  "
        f"K/R  {agg['lifetime_kr']:.2f}",
    ]

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

    map_block = _fmt_map_stats(agg)
    if map_block:
        lines.append(map_block)

    lines.append(f"\n{describe_skill_level(agg['skill_level'], agg['elo'], agg['lifetime_win_rate'])}")
    return "\n".join(lines)


def format_compare(agg1: dict[str, Any], agg2: dict[str, Any]) -> str:
    n1, n2 = agg1['nickname'], agg2['nickname']
    col_w = max(len(n1), len(n2), 8) + 2
    label_w = max(len("Win Rate"), len("Уровень"), 10) + 2

    lines = [
        f"<b>⚔️ Сравнение: {n1} vs {n2}</b>",
        "",
        f"<code>{'':{label_w}}   {n1:<{col_w}}   {n2:<{col_w}}</code>",
    ]

    fields = [
        ("Уровень", "skill_level", "{}", int),
        ("ELO", "elo", "{}", int),
        ("Матчи", "lifetime_matches", "{}", int),
        ("Win Rate", "lifetime_win_rate", "{:.1f}%", float),
        ("K/D", "lifetime_kd", "{:.2f}", float),
        ("ADR", "lifetime_adr", "{:.1f}", float),
        ("HS%", "lifetime_hs_pct", "{:.1f}%", float),
        ("MVPs", "lifetime_mvps", "{}", int),
        ("K/R", "lifetime_kr", "{:.2f}", float),
    ]

    better_n1 = 0
    better_n2 = 0
    for label, key, fmt, caster in fields:
        v1 = caster(agg1.get(key, 0))
        v2 = caster(agg2.get(key, 0))
        s1 = fmt.format(v1)
        s2 = fmt.format(v2)
        if v1 > v2:
            better_n1 += 1
            s1 += " ←"
        elif v2 > v1:
            better_n2 += 1
            s2 += " ←"
        lines.append(f"<code>{label:<{label_w}}   {s1:<{col_w}}   {s2:<{col_w}}</code>")

    total_fields = len(fields)
    ties = total_fields - better_n1 - better_n2
    parts = [f"{n1} лидирует в {better_n1}/{total_fields}" if better_n1 else ""]
    parts.append(f"{n2} лидирует в {better_n2}/{total_fields}" if better_n2 else "")
    parts.append(f"ничья в {ties}" if ties else "")
    verdict = ", ".join(p for p in parts if p)
    lines += ["", f"<b>Итог:</b> {verdict}"]
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
    usefulness = rating_data.get("usefulness", 0)

    lines = [
        f"<b>📊 Рейтинг {agg['nickname']}</b>",
        "",
        f"<b>🎯 Твой рейтинг в матче:</b> {pr}",
    ]
    if elo:
        lines.append(f"Faceit ELO: {elo} (для справки, в расчёте не участвует)")
    lines += [
        "",
        f"<b>👥 Средний рейтинг команды:</b> {tar}",
        f"<b>👊 Средний рейтинг противников:</b> {oar}",
        "",
        f"<b>📈 Шанс победы</b>",
        f"Команды: {twp}%  |  Твой: {pwp}%",
    ]

    if pwp < 50:
        needed_usefulness = required_score_to_win(usefulness, oar, pr)
        lines += [
            "",
            f"<b>⚡ Что нужно для победы</b>",
            f"Нужен Usefulness: {needed_usefulness} (сейчас {usefulness})",
            f"То есть нужен рейтинг матча ≈ {1000 + needed_usefulness * 250:.0f} (сейчас {pr})",
        ]
    else:
        lines += [
            "",
            f"<b>✅ Твой рейтинг выше среднего противника</b>",
            f"При такой игре шанс победы команды — {twp}%",
        ]

    if team_scores:
        lines += ["", "<b>📊 Все игроки</b>"]
        nick = agg["nickname"]
        mates = agg.get("teammates", [])
        opps = agg.get("opponents", [])
        lines.append("🤝 <b>Команда</b>")
        for n in [nick] + mates:
            if n in team_scores:
                ts = team_scores[n]
                marker = " ← Вы" if n == nick else ""
                lines.append(f"  • {n}{marker} — рейтинг {ts['rating']}  |  K/D {ts['kd']:.2f}  |  usefulness {ts['score']}")
        lines.append("")
        lines.append("👊 <b>Противники</b>")
        for n in opps:
            if n in team_scores:
                ts = team_scores[n]
                lines.append(f"  • {n} — рейтинг {ts['rating']}  |  K/D {ts['kd']:.2f}  |  usefulness {ts['score']}")

    return "\n".join(lines)
