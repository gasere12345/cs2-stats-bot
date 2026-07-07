import os

FACEIT_API_KEY: str = os.getenv("FACEIT_TOKEN", "")
FACEIT_BASE_URL: str = "https://open.faceit.com/data/v4"

FA_API_KEY: str = os.getenv("FA_TOKEN", "")
FA_BASE_URL: str = "https://faceitanalyser.com/api"

BOT_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

FACEIT_RETRY_ATTEMPTS: int = 3
FACEIT_TIMEOUT_SEC: float = 15.0
