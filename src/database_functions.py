import sqlite3
import csv
import sys
import logging
from typing import List
from pathlib import Path

from src.utils import database_cache_path
from src.mwis_forecast import MwisForecast


logger = logging.getLogger(__name__)


def execute_query(query: str, cursor, *args) -> None:
    try:
        logger.debug(f"Executing query: {query}")
        logger.debug(f"With args: {args}")
        cursor.execute(query, *args)
    except Exception as e:
        logger.critical(e)
        logger.critical(f"query = {query}")
        sys.exit()


def forecast_already_present(cursor, forecast: MwisForecast) -> bool:
    query = f"""SELECT * FROM mwis 
    WHERE location='{forecast.location}' 
    AND date='{forecast.date}'
    AND days_ahead='{forecast.days_ahead}'"""

    execute_query(query, cursor)

    #execute_query("SELECT location, date, days_ahead FROM mwis WHERE location='west-highlands'", cursor)
    #print(cursor.fetchall())
    #assert 0

    return len(cursor.fetchall()) > 0


def add_mwis_forecast_to_database(all_forecasts: List[MwisForecast]) -> None:
    """Update database with new forecast. Has no effect if forecast has already been added.
    """
    db_path = database_cache_path()
    assert db_path.exists()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    for forecast in all_forecasts:
        if forecast_already_present(cursor, forecast):
            logger.debug(f"Forecast already present for {forecast.location, forecast.date, forecast.days_ahead}")
            continue

        logger.debug(f"Forecast not present for {forecast.location, forecast.date, forecast.days_ahead}")
        logger.debug("Adding to database...")

        values = (None,) + tuple(str(getattr(forecast, k)) for k in forecast)
        query = f"INSERT INTO mwis VALUES({','.join(['?'] * len(values))})"
        execute_query(query, cursor, values)

        logger.debug("Added MWIS forecast to database")

    conn.commit()

    execute_query("SELECT * FROM mwis", cursor)
    logger.info(f"Database now contains {len(cursor.fetchall())} rows")


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
                            id integer PRIMARY KEY AUTOINCREMENT,
                            {col_str}
                            );"""

    logger.debug(create_mwis_table)

    execute_query(create_mwis_table, cursor)

    logger.info("Table setup completed normally")


def mwis_table_to_csv(outpath: Path) -> None:
    db_path = database_cache_path()
    assert db_path.exists()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    execute_query("SELECT * FROM mwis", cursor)

    with open(outpath, "w", newline="") as outfile:
        writer = csv.writer(outfile)

        for row in cursor:
            writer.writerow(row)

    


