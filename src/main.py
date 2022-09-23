import logging
import sqlite3
from pathlib import Path
from pprint import pprint

from scrape_latest_mwis import scrape_latest_mwis
from database_functions import setup_database, add_mwis_forecast_to_database


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.DEBUG)

    logger.info("Started main script")

    setup_database()
    
    mwis_forecast = scrape_latest_mwis()

    pprint(mwis_forecast, width=240)

    add_mwis_forecast_to_database(mwis_forecast)

    logger.info("Program finished normally")



#def append_mwis_forecast_to_dataframe(df_row: pd.Series) -> None:
#    """Append to dataframe stored as csv on disk
#
#    Note: The dataframe is organised so that today's date is the index, and all forecasts
#        are organised by area, day, and section in a multicol setup. We also check the
#        latest forecast in the table to make sure that we only add one new forecast per day.
#
#        There is a possible issue with this approach, because every afternoon the forecast
#        dates change. So just make sure you run this script at a consistent time every day.
#    """
#    today = str(datetime.datetime.today().date())
#    df = pd.DataFrame(data=[df_row], index=[today])
#
#    if not TABLE_PATH.exists():
#        df.to_csv(TABLE_PATH)
#    else:
#        df_cached = pd.read_csv(TABLE_PATH, header=[0, 1, 2], index_col=0)
#        assert (df_cached.columns == df.columns).all()
#
#        df_cached = df_cached.append(df).drop_duplicates()
#        df_cached.to_csv(TABLE_PATH)



if __name__ == "__main__":
    main()
