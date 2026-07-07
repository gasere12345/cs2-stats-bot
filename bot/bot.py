import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from bot.faceit_client import FaceitClient
from bot.fa_client import FaceitAnalyserClient
from bot.parser import parse_faceit_url
from bot.aggregator import aggregate_player_data
from bot.analyzer import compute_usefulness
from bot.formatter import format_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FACEIT_TOKEN = os.environ.get("FACEIT_TOKEN", "")
FA_TOKEN = os.environ.get("FA_TOKEN", "")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")

faceit = FaceitClient(api_key=FACEIT_TOKEN)
fa = FaceitAnalyserClient(api_key=FA_TOKEN)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(Command("start", "help"))
async def cmd_start(message: types.Message):
    await message.reply(
        "Пришли ссылку на Faceit-матч и ник игрока командой:\n"
        "<code>/faceit &lt;ссылка&gt; &lt;ник&gt;</code>\n\n"
        "Пример:\n"
        "<code>/faceit https://www.faceit.com/en/cs2/room/abc123 NiKo</code>"
    )


@dp.message(Command("faceit"))
async def cmd_faceit(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Использование: /faceit <ссылка> <ник>")
        return

    raw_url = args[1]
    nickname = args[2]

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

        player_faceit = await faceit.get_player_by_nickname(nickname)
        lifetime = None
        if player_faceit:
            lifetime = await faceit.get_lifetime_stats(player_faceit["player_id"])

        extended = None
        try:
            extended = await fa.get_match_extended_stats(match_id)
        except Exception as e:
            logger.warning("Faceit Analyser API не отвечает: %s", e)

        await status_msg.edit_text("📊 Анализирую...")

        agg = aggregate_player_data(nickname, match_stats, extended, lifetime)
        if agg["kills"] == 0 and agg["deaths"] == 0:
            await status_msg.edit_text(f"❌ Игрок {nickname} не найден в этом матче.")
            return

        score = compute_usefulness(agg)
        text = format_stats(agg, score)

        await status_msg.edit_text(text, parse_mode="HTML")
    except Exception as e:
        logger.exception("Ошибка при обработке команды")
        await status_msg.edit_text(f"❌ Ошибка: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
