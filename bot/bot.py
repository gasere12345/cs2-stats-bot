import os
import asyncio
import logging
import threading
from dataclasses import asdict
from http.server import HTTPServer, BaseHTTPRequestHandler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import FACEIT_API_KEY, CS2_SPACE_KEY, BOT_TOKEN
from bot.faceit_client import FaceitClient
from bot.cs2space_client import Cs2SpaceClient
from bot.parser import parse_faceit_url
from bot.aggregator import aggregate_player_data
from bot.analyzer import compute_usefulness
from bot.formatter import format_summary, format_career, format_match_detail, format_roster, format_rating_tab, format_profile, format_compare
from bot.rating import compute_rating, team_win_probability, win_probability

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FACEIT_TOKEN = FACEIT_API_KEY
TELEGRAM_TOKEN = BOT_TOKEN

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set")
if not FACEIT_TOKEN:
    raise ValueError("FACEIT_TOKEN is not set")

faceit = FaceitClient(api_key=FACEIT_TOKEN)
cs2space = Cs2SpaceClient(api_key=CS2_SPACE_KEY) if CS2_SPACE_KEY else None

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

_sessions: dict[int, dict] = {}
_waiting_for: dict[int, str] = {}

TAB_SUMMARY = "tab_summary"
TAB_CAREER = "tab_career"
TAB_MATCH = "tab_match"
TAB_ROSTER = "tab_roster"
TAB_RATING = "tab_rating"

EXAMPLE_MATCH_URL = "https://www.faceit.com/en/cs2/room/1-bef556dc-1883-4cad-b111-b3546972519c"
EXAMPLE_NICKNAME = "f1lipmeister"


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
        InlineKeyboardButton(text="⚔️ Сравнить", callback_data="compare"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 Помощь", callback_data="help"),
        InlineKeyboardButton(text="📌 Пример", callback_data="example"),
    )
    return builder.as_markup()


def match_buttons(match_url: str, player_url: str | None = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Сводка", callback_data=TAB_SUMMARY),
        InlineKeyboardButton(text="📈 Карьера", callback_data=TAB_CAREER),
    )
    builder.row(
        InlineKeyboardButton(text="🔫 Матч", callback_data=TAB_MATCH),
        InlineKeyboardButton(text="👥 Состав", callback_data=TAB_ROSTER),
        InlineKeyboardButton(text="📊 Рейтинг", callback_data=TAB_RATING),
    )
    builder.row(InlineKeyboardButton(text="🔗 Открыть матч", url=match_url))
    if player_url:
        builder.row(InlineKeyboardButton(text="👤 Профиль", url=player_url))
    builder.row(InlineKeyboardButton(text="🔄 Новый поиск", callback_data="start"))
    return builder.as_markup()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    _waiting_for.pop(message.chat.id, None)
    await message.reply(
        "🎮 <b>CS2 Faceit Stats Bot</b>\n\n"
        "Анализирую статистику игроков в матчах Faceit.\n\n"
        "Используй кнопки ниже или команды:\n"
        "• <code>/faceit &lt;url&gt; &lt;ник&gt;</code> — статистика матча\n"
        "• <code>/profile &lt;ник&gt;</code> — профиль игрока\n"
        "• <code>/compare &lt;ник1&gt; &lt;ник2&gt;</code> — сравнение",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.reply(
        "📋 <b>Все команды</b>\n\n"
        "<b>/start</b> — главное меню\n"
        "<b>/help</b> — эта справка\n"
        "<b>/faceit</b> <i>&lt;url&gt; &lt;ник&gt;</i> — статистика матча\n"
        "<b>/profile</b> <i>&lt;ник&gt;</i> — профиль игрока\n"
        "<b>/compare</b> <i>&lt;ник1&gt; &lt;ник2&gt;</i> — сравнить игроков\n\n"
        "📌 <b>Пример:</b>\n"
        f"<code>/faceit {EXAMPLE_MATCH_URL} {EXAMPLE_NICKNAME}</code>\n\n"
        "📊 <b>Что умеет бот:</b>\n"
        "• Usefulness Score (−2..+2)\n"
        "• Разбор по картам (топ-5)\n"
        "• Elo-рейтинг и шанс победы\n"
        "• Leetify рейтинги (aim/pos/util)\n"
        "• Профиль и сравнение игроков\n",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )


@dp.callback_query(F.data == "start")
async def cb_start(callback: types.CallbackQuery):
    _waiting_for.pop(callback.message.chat.id, None)
    await callback.message.edit_text(
        "🎮 <b>CS2 Faceit Stats Bot</b>\n\n"
        "Анализирую статистику игроков в матчах Faceit.\n\n"
        "Используй кнопки ниже или команды:\n"
        "• <code>/faceit &lt;url&gt; &lt;ник&gt;</code> — статистика матча\n"
        "• <code>/profile &lt;ник&gt;</code> — профиль игрока\n"
        "• <code>/compare &lt;ник1&gt; &lt;ник2&gt;</code> — сравнение",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "help")
async def cb_help(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📋 <b>Все команды</b>\n\n"
        "<b>/start</b> — главное меню\n"
        "<b>/help</b> — эта справка\n"
        "<b>/faceit</b> <i>&lt;url&gt; &lt;ник&gt;</i> — статистика матча\n"
        "<b>/profile</b> <i>&lt;ник&gt;</i> — профиль игрока\n"
        "<b>/compare</b> <i>&lt;ник1&gt; &lt;ник2&gt;</i> — сравнить игроков\n\n"
        "📌 <b>Пример:</b>\n"
        f"<code>/faceit {EXAMPLE_MATCH_URL} {EXAMPLE_NICKNAME}</code>\n\n"
        "📊 <b>Что умеет бот:</b>\n"
        "• Usefulness Score (−2..+2)\n"
        "• Разбор по картам (топ-5)\n"
        "• Elo-рейтинг и шанс победы\n"
        "• Leetify рейтинги (aim/pos/util)\n"
        "• Профиль и сравнение игроков\n",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "example")
async def cb_example(callback: types.CallbackQuery):
    await callback.message.edit_text(
        f"📌 <b>Пример команды:</b>\n\n"
        f"<code>/faceit {EXAMPLE_MATCH_URL} {EXAMPLE_NICKNAME}</code>\n\n"
        "Просто скопируй и отправь это сообщение боту 👆",
        parse_mode="HTML",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.message(Command("faceit"))
async def cmd_faceit(message: types.Message, command: CommandObject):
    args = command.args
    if not args:
        await message.reply(
            "❌ Укажи ссылку на матч и ник игрока.\n\n"
            "Пример:\n"
            f"<code>/faceit {EXAMPLE_MATCH_URL} {EXAMPLE_NICKNAME}</code>",
            parse_mode="HTML",
        )
        return

    parts = args.rsplit(maxsplit=1)
    if len(parts) < 2:
        await message.reply(
            "❌ Укажи и ссылку, и ник.\n\n"
            f"Пример: <code>/faceit {EXAMPLE_MATCH_URL} {EXAMPLE_NICKNAME}</code>",
            parse_mode="HTML",
        )
        return

    raw_url, nickname = parts[0].strip(), parts[1].strip()

    match_id = parse_faceit_url(raw_url)
    if not match_id:
        await message.reply("❌ Не удалось извлечь ID матча из ссылки.")
        return

    status_msg = await message.reply("🔍 Получаю данные с Faceit API...")

    try:
        match_data = await faceit.get_match(match_id)
        if not match_data:
            await status_msg.edit_text("❌ Матч не найден.")
            return

        match_stats = await faceit.get_match_stats(match_id)
        if not match_stats or "players" not in match_stats:
            await status_msg.edit_text("❌ Статистика матча не найдена.")
            return

        await status_msg.edit_text("🔍 Получаю расширенную аналитику...")

        match_player_id = None
        for p in (match_stats.get("players") or []):
            if p.get("nickname", "").lower() == nickname.lower():
                match_player_id = p.get("player_id")
                break

        player_faceit = None
        try:
            player_faceit = await faceit.get_player_by_nickname(nickname)
        except Exception as e:
            logger.warning("Не удалось найти профиль игрока по нику: %s", e)

        player_id = None
        if player_faceit and player_faceit.player_id:
            player_id = player_faceit.player_id
        elif match_player_id:
            player_id = match_player_id
            try:
                player_faceit = await faceit.get_player_by_id(match_player_id)
            except Exception as e:
                logger.warning("Не удалось найти профиль по ID: %s", e)

        lifetime = None
        if player_id:
            lifetime = await faceit.get_lifetime_stats(player_id)

        leetify = await _fetch_leetify(player_faceit)
        await status_msg.edit_text("📊 Анализирую...")

        player_info = asdict(player_faceit) if player_faceit else None
        agg = aggregate_player_data(nickname, match_stats, None, asdict(lifetime) if lifetime else None, player_info, leetify)
        if agg["kills"] == 0 and agg["deaths"] == 0:
            await status_msg.edit_text(f"❌ Игрок {nickname} не найден в этом матче.")
            return

        score = compute_usefulness(agg)

        team_scores = {}
        for p in (match_stats.get("players") or []):
            p_agg = aggregate_player_data(p["nickname"], match_stats, None, None, None, None)
            p_score = compute_usefulness(p_agg)
            team_scores[p["nickname"]] = {
                "score": p_score,
                "team_id": p.get("team_id", ""),
                "kd": p_agg["kd"],
                "kills": p_agg["kills"],
                "deaths": p_agg["deaths"],
                "adr": p_agg["adr"],
                "rating": compute_rating(p_agg, p_score),
            }

        faceit_url = f"https://www.faceit.com/en/cs2/room/{match_id}"
        player_faceit_url = f"https://www.faceit.com/en/players/{nickname}" if player_faceit else None

        player_team_id = team_scores.get(nickname, {}).get("team_id", "")
        team_ratings = [ts["rating"] for ts in team_scores.values() if ts.get("team_id") == player_team_id]
        opp_ratings = [ts["rating"] for ts in team_scores.values() if ts.get("team_id") != player_team_id]
        team_avg_rating = round(sum(team_ratings) / len(team_ratings), 1) if team_ratings else 0
        opp_avg_rating = round(sum(opp_ratings) / len(opp_ratings), 1) if opp_ratings else 0
        player_rating = compute_rating(agg, score)
        twp = team_win_probability(team_avg_rating, opp_avg_rating)
        pwp = win_probability(player_rating, opp_avg_rating)

        _sessions[message.chat.id] = {
            "agg": agg, "score": score,
            "match_url": faceit_url, "player_url": player_faceit_url,
            "team_scores": team_scores,
            "rating_data": {
                "player_rating": player_rating,
                "player_elo": agg.get("elo", 0),
                "team_avg_rating": team_avg_rating,
                "opp_avg_rating": opp_avg_rating,
                "team_win_prob": twp,
                "player_win_prob": pwp,
                "usefulness": score,
            },
        }

        text = format_summary(agg, score)
        kb = match_buttons(faceit_url, player_faceit_url)

        await status_msg.edit_text(text, parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        logger.exception("Ошибка при обработке команды")
        await status_msg.edit_text(f"❌ Ошибка: {e}")


async def _fetch_leetify(player_faceit):
    leetify = None
    if cs2space and player_faceit and player_faceit.steam_id:
        try:
            profile = await cs2space.get_profile(player_faceit.steam_id)
            leetify = (profile or {}).get("leetify")
        except Exception as e:
            logger.warning("cs2.space API не отвечает: %s", e)
    return leetify


async def _fetch_profile(nickname: str):
    player = await faceit.get_player_by_nickname(nickname)
    if not player:
        return None
    lifetime = await faceit.get_lifetime_stats(player.player_id)
    leetify = await _fetch_leetify(player)
    agg = aggregate_player_data(
        nickname, None, None,
        asdict(lifetime) if lifetime else None,
        asdict(player) if player else None,
        leetify,
    )
    return agg


async def _do_profile(nickname: str, status_msg: types.Message):
    agg = await _fetch_profile(nickname)
    if not agg or not agg.get("lifetime_matches"):
        await status_msg.edit_text(f"❌ Игрок {nickname} не найден.")
        return
    text = format_profile(agg)
    await status_msg.edit_text(text, parse_mode="HTML", reply_markup=main_menu())


async def _do_compare(names: str, status_msg: types.Message):
    parts = names.split(None, 1)
    if len(parts) < 2:
        await status_msg.edit_text("❌ Введи два ника через пробел.")
        return
    n1, n2 = parts[0].strip(), parts[1].strip()
    agg1 = await _fetch_profile(n1)
    agg2 = await _fetch_profile(n2)
    if not agg1 or not agg1.get("lifetime_matches"):
        await status_msg.edit_text(f"❌ Игрок {n1} не найден.")
        return
    if not agg2 or not agg2.get("lifetime_matches"):
        await status_msg.edit_text(f"❌ Игрок {n2} не найден.")
        return
    text = format_compare(agg1, agg2)
    await status_msg.edit_text(text, parse_mode="HTML", reply_markup=main_menu())


@dp.message(Command("profile"))
async def cmd_profile(message: types.Message, command: CommandObject):
    nickname = (command.args or "").strip()
    if not nickname:
        await message.reply(
            "👤 Введи ник игрока.\n\n"
            "Например: <code>/profile f1lipmeister</code>",
            parse_mode="HTML",
        )
        return
    status_msg = await message.reply("🔍 Ищу игрока...")
    try:
        await _do_profile(nickname, status_msg)
    except Exception as e:
        logger.exception("Ошибка /profile")
        await status_msg.edit_text(f"❌ Ошибка: {e}")


@dp.message(Command("compare"))
async def cmd_compare(message: types.Message, command: CommandObject):
    args = (command.args or "").strip()
    if not args or " " not in args:
        await message.reply(
            "⚔️ Введи два ника через пробел.\n\n"
            "Например: <code>/compare f1lipmeister donk</code>",
            parse_mode="HTML",
        )
        return
    status_msg = await message.reply("🔍 Ищу игроков...")
    try:
        await _do_compare(args, status_msg)
    except Exception as e:
        logger.exception("Ошибка /compare")
        await status_msg.edit_text(f"❌ Ошибка: {e}")


@dp.message(F.text, ~F.command())
async def handle_input(message: types.Message):
    state = _waiting_for.pop(message.chat.id, None)
    if not state:
        return
    status_msg = await message.reply("🔍 Обрабатываю...")
    try:
        if state == "profile":
            await _do_profile(message.text.strip(), status_msg)
        elif state == "compare":
            await _do_compare(message.text.strip(), status_msg)
    except Exception as e:
        logger.exception("Ошибка в handle_input")
        await status_msg.edit_text(f"❌ Ошибка: {e}")


async def _show_tab(callback: types.CallbackQuery, tab: str, formatter):
    session = _sessions.get(callback.message.chat.id)
    if not session:
        await callback.answer("❌ Данные устарели, отправь /faceit заново")
        return
    text = formatter(session["agg"], session["score"])
    kb = match_buttons(session["match_url"], session.get("player_url"))
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data == TAB_SUMMARY)
async def cb_tab_summary(callback: types.CallbackQuery):
    await _show_tab(callback, TAB_SUMMARY, format_summary)


@dp.callback_query(F.data == TAB_CAREER)
async def cb_tab_career(callback: types.CallbackQuery):

    def formatter(agg, _score):
        return format_career(agg)
    await _show_tab(callback, TAB_CAREER, formatter)


@dp.callback_query(F.data == TAB_MATCH)
async def cb_tab_match(callback: types.CallbackQuery):

    def formatter(agg, _score):
        return format_match_detail(agg)
    await _show_tab(callback, TAB_MATCH, formatter)


@dp.callback_query(F.data == TAB_ROSTER)
async def cb_tab_roster(callback: types.CallbackQuery):

    def formatter(agg, _score):
        session = _sessions.get(callback.message.chat.id)
        return format_roster(agg, (session or {}).get("team_scores"))
    await _show_tab(callback, TAB_ROSTER, formatter)


@dp.callback_query(F.data == TAB_RATING)
async def cb_tab_rating(callback: types.CallbackQuery):

    def formatter(agg, _score):
        session = _sessions.get(callback.message.chat.id)
        if not session:
            return "❌ Данные устарели, отправь /faceit заново"
        return format_rating_tab(agg, (session or {}).get("rating_data"), (session or {}).get("team_scores"))
    await _show_tab(callback, TAB_RATING, formatter)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *args):
        pass


def _start_health_server():
    port = int(os.environ.get("PORT", "8000"))
    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    server.serve_forever()


async def main():
    if os.environ.get("PORT"):
        threading.Thread(target=_start_health_server, daemon=True).start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
