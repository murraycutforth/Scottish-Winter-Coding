"""Script which scrapes latest forecast from MWIS for selected regions

Designed to be run once per day using cron. Appends latest forecast to pandas dataframe stored as csv.

Author:
    Murray Cutforth
"""

import re
import os
from pathlib import Path
from typing import *
from dateutil.parser import parse
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd


URL = 'https://www.smc.org.uk/cicwebcam/cic_weather.php'
TABLE_PATH = Path(os.environ['PROJ_DIR']) / 'data/CIC/cic_observations.csv'


def main():
    table_df = pd.read_html(URL, attrs={'class': 'table'})[1]
    append_forecast_to_dataframe(table_df)
    print('scrape_latest_CIC_observations.py completed normally')


def append_forecast_to_dataframe(df: pd.DataFrame) -> None:
    """Append to dataframe stored as csv on disk
    """
    today = str(datetime.datetime.today().date())
    df.index = [today]

    if not TABLE_PATH.parent.exists():
        TABLE_PATH.parent.mkdir()

    if not TABLE_PATH.exists():
        df.to_csv(TABLE_PATH)
    else:
        df_cached = pd.read_csv(TABLE_PATH, header=[0], index_col=0)
        assert (df_cached.columns == df.columns).all()

        df_cached = df_cached.append(df).drop_duplicates()
        df_cached.to_csv(TABLE_PATH)


if __name__ == '__main__':
    main()
