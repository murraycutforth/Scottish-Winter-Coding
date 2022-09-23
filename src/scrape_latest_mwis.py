import re
from typing import Dict, List
import os
from pathlib import Path
from typing import *
from dateutil.parser import parse
import datetime
import requests
import logging

from bs4 import BeautifulSoup
import pandas as pd


logger = logging.getLogger(__name__)


URL_BASE = 'https://www.mwis.org.uk/forecasts/scottish/'


LOCATIONS = ['west-highlands',
             'the-northwest-highlands',
             'cairngorms-np-and-monadhliath',
             'southeastern-highlands']


class MwisForecast():
    location: str = ""
    date: str = ""
    days_ahead: int = 0
    headline: str = ""
    how_wet: str = ""
    how_windy: str = ""
    cloud_on_hills: str = ""
    chance_cloud_free: str = ""
    sunshine: str = ""
    how_cold: str = ""
    freezing_level: str = ""

    def __iter__(self):
        """Sorted iteration over attribute names
        """
        for k in sorted(self.__annotations__):
            yield k

    def __repr__(self) -> str:
        return f"MwisForecast(location={self.location}, date={self.date}, days_ahead={self.days_ahead})"

    @staticmethod
    def attr_to_section_title() -> Dict:
        """Mapping from attribute name to section title in HTML
        """
        return {"how_wet": "How Wet?",
                 "how_windy": "How windy? (On the Munros)",
                 "cloud_on_hills": "Cloud on the hills?",
                 "chance_cloud_free": "Chance of cloud free Munros?",
                 "sunshine": "Sunshine and air clarity?",
                 "how_cold": "How Cold? (at 900m)",
                 "freezing_level": "Freezing Level"}
            


def scrape_latest_mwis() -> List[MwisForecast]:
    """Top level function in this module, scrapes latest MWIS forecast
    """
    URLs = [URL_BASE + x + '/text' for x in LOCATIONS]
    
    pages = [requests.get(x) for x in URLs]
    
    for x in pages:
        # Check that request has succeeded
        assert x.status_code == 200
    
    logger.info('Successfully fetched latest forecasts')

    all_forecasts = []
    
    for l, p in zip(LOCATIONS, pages):
        extract_forecasts_for_area(l, p, all_forecasts)

    logger.info('HTML page parsed successfully')

    return all_forecasts


def extract_forecasts_for_area(location: str, page: requests.Response, all_forecasts: List) -> None:
    """Get all three forecasts for given area
    """
    soup = BeautifulSoup(page.content, 'html.parser')

    for i in range(3):
        all_forecasts.append(extract_forecast_for_day(location, i, soup, all_forecasts))


def extract_forecast_for_day(location: str, i: int, soup: BeautifulSoup, all_forecasts: List) -> MwisForecast:
    """Forecasts for three days are provided, this extracts the specified one
    """
    forecast_soup = soup.find(id='Forecast' + str(i))
    forecast = MwisForecast()
    forecast.location = location
    forecast.days_ahead = i + 1

    if i == 0:
        # Headline only exists for next day forecast
        headline = f"Headline for {soup.find('h1').text}"
        forecast.headline = extract_forecast_section(forecast_soup, headline)

    # Populate all default sections
    for k, title in MwisForecast.attr_to_section_title().items():
        forecast_str = extract_forecast_section(forecast_soup, title)
        setattr(forecast, k, forecast_str)

    # Extract date of forecast
    datestr = forecast_soup.find(text='Viewing Forecast For').findNext().findNext().text.split('\n')[3]
    date = str(parse(datestr).date())
    forecast.date = date

    return forecast


def extract_forecast_section(forecast_soup, title) -> str:
    """Extract single section from soup
    """
    try:
        forecast_str = forecast_soup.find('h4', text=title).findNext('div').findNext().text

        # Convert all newlines and tabs to spaces
        forecast_str = re.sub(r'\s+', ' ', forecast_str)

        return forecast_str

    except Exception as e:
        print("Problem with ", x)
        print("Exception: ", e)
        return ""


def forecast_to_series(all_forecasts: Dict) -> pd.Series:
    """Convert extracted forecast to pandas series with multiindex

    NOTE: this function not used atm, unless it is called in another file?
    """
    all_forecasts_tuple_keys = {(i, j, k): all_forecasts[i][j][k] \
            for i in all_forecasts.keys() \
            for j in all_forecasts[i].keys() \
            for k in all_forecasts[i][j].keys()}

    mux = pd.MultiIndex.from_tuples(all_forecasts_tuple_keys.keys(),
                                    names=['Location', 'Number of days ahead', 'Forecast section'])
    df_row = pd.Series(all_forecasts_tuple_keys.values(), index=mux)

    return df_row

