# CS2 Faceit Stats Telegram Bot

## Stack
- Python 3.11+, aiogram 3, httpx

## Structure
- `bot/bot.py` — entry point, Telegram handlers
- `bot/config.py` — токены, URL, таймауты
- `bot/faceit_client.py` — Faceit API
- `bot/cs2space_client.py` — cs2.space API (Leetify)
- `bot/aggregator.py` — склейка данных из источников
- `bot/analyzer.py` — Usefulness Score
- `bot/formatter.py` — форматирование сообщений
- `bot/parser.py` — парсинг ссылок на матчи
- `bot/rating.py` — Elo-рейтинг
- `bot/models.py` — датаклассы
- `tests/` — pytest тесты

## How to run
```bash
cd cs2-stats-bot
.venv/bin/python -m bot.bot
```

## How to test
```bash
.venv/bin/python -m pytest tests/ -v
```

## Workflow
После каждого изменения кода ОБЯЗАТЕЛЬНО:
1. Запустить тесты: `.venv/bin/python -m pytest tests/ -v`
2. Запустить субагента-ревьюера (subagent_type=general) с задачей проверить весь проект на баги, безопасность, качество кода
3. Если тесты не зеленые или ревьюер нашёл critical/high — исправить перед коммитом
4. Залить на GitHub: `git add -A && git commit -m "msg" && git push`

## Environment
- `.env`: FACEIT_TOKEN, TELEGRAM_TOKEN, CS2_SPACE_KEY, FA_TOKEN
- Render авто-деплой при пуше в master

## Commands
- `/faceit <url> <ник>` — статистика матча
- `/profile <ник>` — профиль игрока
- `/compare <ник1> <ник2>` — сравнение игроков
