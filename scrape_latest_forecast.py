"""Script which scrapes latest forecast from MWIS for selected regions

Designed to be run once per day using cron. Appends latest forecast to pandas dataframe stored as csv.

Author:
    Murray Cutforth
"""

import re
from pathlib import Path
from typing import *
from dateutil.parser import parse
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd


URL_BASE = 'https://www.mwis.org.uk/forecasts/scottish/'
LOCATIONS = ['west-highlands',
             'the-northwest-highlands',
             'cairngorms-np-and-monadhliath']
SECTION_TITLES = ['How Wet?',
                  'How windy? (On the Munros)',
                  'How Cold? (at 900m)']
TABLE_PATH = Path('/home/murray/Projects/MWIS-Scraper/data/mwis_forecasts.csv')


def main():
    if not TABLE_PATH.parent.exists():
        TABLE_PATH.parent.mkdir()

    URLs = [URL_BASE + x + '/text' for x in LOCATIONS]
    
    pages = [requests.get(x) for x in URLs]
    
    for x in pages:
        # Check that request has succeeded
        assert x.status_code == 200
    
    print('Successfully fetched latest forecasts')

    all_forecasts = {}
    
    for l, p in zip(LOCATIONS, pages):
        area_forecast = extract_forecasts_for_area(l, p)
        all_forecasts[l] = area_forecast

    print('HTML page parsed successfully')

    df_row = forecast_to_series(all_forecasts)

    append_forecast_to_dataframe(df_row)

    print('Script completed normally')


def extract_forecasts_for_area(location: str, page: requests.Response) -> Dict:
    """Get all three forecasts for given area
    """
    soup = BeautifulSoup(page.content, 'html.parser')
    area_forecast = {}

    for i in range(3):
        day_forecast = extract_forecast_for_day(i, soup)
        area_forecast[str(i+1)] = day_forecast
    return area_forecast


def extract_forecast_for_day(i: int, soup: BeautifulSoup) -> Dict:
    """Forecasts for three days are provided, this extracts the specified one
    """
    forecast = soup.find(id='Forecast' + str(i))
    
    # Extract date - currently not used anywhere
    if False:
        datestr = forecast.find(text='Viewing Forecast For').findNext().findNext().text.split('\n')[3]
        date = str(parse(datestr).date())
    
    # Extract raw text forecast for each section of interest
    data = {}
    for x in SECTION_TITLES:
        forecast_str = forecast.find('h4', text=x).findNext('div').findNext().text

        # Remove all punctuation from forecast (except hyphens for minus signs)
        forecast_str = re.sub(r'[^\w\s-]', '', forecast_str)

        # Convert all newlines and tabs to spaces
        forecast_str = re.sub(r'\s+', ' ', forecast_str)

        data[x] = forecast_str
        
    return data


def forecast_to_series(all_forecasts: Dict) -> pd.Series:
    """Convert extracted forecast to pandas series with multiindex
    """
    all_forecasts_tuple_keys = {(i, j, k): all_forecasts[i][j][k] \
            for i in all_forecasts.keys() \
            for j in all_forecasts[i].keys() \
            for k in all_forecasts[i][j].keys()}

    mux = pd.MultiIndex.from_tuples(all_forecasts_tuple_keys.keys(),
                                    names=['Location', 'Number of days ahead', 'Forecast section'])
    df_row = pd.Series(all_forecasts_tuple_keys.values(), index=mux)

    return df_row


def append_forecast_to_dataframe(df_row: pd.Series) -> None:
    """Append to dataframe stored as csv on disk

    Note: The dataframe is organised so that today's date is the index, and all forecasts
        are organised by area, day, and section in a multicol setup. We also check the
        latest forecast in the table to make sure that we only add one new forecast per day.

        There is a possible issue with this approach, because every afternoon the forecast
        dates change. So just make sure you run this script at a consistent time every day.
    """
    today = str(datetime.datetime.today().date())
    df = pd.DataFrame(data=[df_row], index=[today])

    if not TABLE_PATH.exists():
        df.to_csv(TABLE_PATH)
    else:
        df_cached = pd.read_csv(TABLE_PATH, header=[0, 1, 2], index_col=0)
        assert (df_cached.columns == df.columns).all()

        df_cached = df_cached.append(df).drop_duplicates()
        df_cached.to_csv(TABLE_PATH)


if __name__ == '__main__':
    main()
