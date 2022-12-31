from pathlib import Path


def database_cache_path() -> Path:
    return Path.home() / ".scottish-winter-coding/data.db"

def mwis_log_dir() -> Path:
    return Path.home() / ".scottish-winter-coding/log"
