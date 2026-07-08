import os

FACEIT_API_KEY: str = os.getenv("FACEIT_TOKEN", "")
FACEIT_BASE_URL: str = "https://open.faceit.com/data/v4"

FA_API_KEY: str = os.getenv("FA_TOKEN", "")
FA_BASE_URL: str = "https://faceitanalyser.com/api"

BOT_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

CS2_SPACE_KEY: str = os.getenv("CS2_SPACE_KEY", "")
CS2_SPACE_BASE_URL: str = "https://cs2.space/api"

FACEIT_RETRY_ATTEMPTS: int = 3
FACEIT_TIMEOUT_SEC: float = 15.0
