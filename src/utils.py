from pathlib import Path


def database_cache_path() -> Path:
    return Path.home() / ".scottish-winter-coding/data.db"
