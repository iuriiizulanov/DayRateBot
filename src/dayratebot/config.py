from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: Path


def load_settings() -> Settings:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("BOT_TOKEN is not set. Copy .env.example to .env and add your token.")

    return Settings(
        bot_token=token,
        database_path=Path(os.getenv("DATABASE_PATH", "data/dayrate.sqlite3")),
    )
