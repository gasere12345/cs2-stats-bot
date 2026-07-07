# CS2 Stats Telegram Bot

## Stack
- Python 3.11+, aiogram 3, Tesseract OCR, OpenCV, Pillow

## Structure
- `bot.py` — entry point, Telegram handlers
- `config.py` — BOT_TOKEN, weights, thresholds
- `ocr.py` — image preprocessing + Tesseract OCR
- `parser.py` — parse OCR text → PlayerStats / MatchData
- `analyzer.py` — weighted rating (−2..+2) + verdict text
- `requirements.txt` — pip dependencies

## How to run
```bash
cd cs2-stats-bot
pip install -r requirements.txt
sudo apt install tesseract-ocr
# set BOT_TOKEN in config.py
python bot.py
```

## Commands
- `/start` — welcome
- `/help` — usage
- `/me Nickname` reply to photo — analyze specific player
- Just send a screenshot — analyze all found players

## Data flow
User screenshot → download → OCR preprocessing (gray+otsu+scale2x) → Tesseract → raw text → regex parse → PlayerStats → weighted score → verdict → reply
