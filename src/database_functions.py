import sqlite3
import sys
import logging
from typing import List

from utils import database_cache_path
from scrape_latest_mwis import MwisForecast


logger = logging.getLogger(__name__)


def execute_query(query: str, cursor) -> None:
    try:
        cursor.execute(query)
    except Exception as e:
        logger.critical(e)
        logger.critical(f"query = {query}")
        sys.exit()


def add_mwis_forecast_to_database(all_forecasts: List[MwisForecast]) -> None:
    """Update database with new forecast. Has no effect if forecast has already been added.
    
    Note:
        The forecast is a three-level dictionary like
        {location: {# days ahead: {forecast section: forecast text}}}
    """
    db_path = database_cache_path()
    assert db_path.exists()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    for forecast in all_forecasts:
        # Check if (location, date, days_ahead) are already in the database
        # TODO

        values = ",".join("'" + str(getattr(forecast, k)) + "'" for k in forecast)

        query = f"INSERT INTO mwis VALUES({values})"
        execute_query(query, cursor)

        logger.debug("Added MWIS forecast to table")
        logger.debug(execute_query("SELECT * FROM mwis", cursor).fetchall())


def setup_database() -> None:
    """Perform initial setup of database. Has no effect if database is already set up.
    """
    db_path = database_cache_path()

    if not db_path.exists():
        db_path.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    attr_names = list(MwisForecast())
    col_str = " text NOT NULL, ".join(attr_names + [""]).strip(" ,")

    create_mwis_table = f"""CREATE TABLE IF NOT EXISTS mwis (
                            id integer PRIMARY KEY,
                            {col_str}
                            );"""

    execute_query(create_mwis_table, cursor)

    logger.info("Table setup completed normally")


