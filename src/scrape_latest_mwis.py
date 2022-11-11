import re
from typing import Dict, List
import os
from pathlib import Path
from typing import *
from dateutil.parser import parse
import datetime
import requests
import logging
from pprint import pformat

from bs4 import BeautifulSoup
import pandas as pd

from database_functions import setup_database, add_mwis_forecast_to_database
from mwis_forecast import MwisForecast


logger = logging.getLogger(__name__)


URL_BASE = 'https://www.mwis.org.uk/forecasts/scottish/'


LOCATIONS = ['west-highlands',
             'the-northwest-highlands',
             'cairngorms-np-and-monadhliath',
             'southeastern-highlands']


def main():
    logging.basicConfig(level=logging.DEBUG)

    logger.info("Started main script")

    setup_database()
    
    mwis_forecast = scrape_latest_mwis()

    logger.debug(pformat(mwis_forecast, width=240))

    add_mwis_forecast_to_database(mwis_forecast)

    logger.info("Program finished normally")



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


if __name__ == "__main__":
    main()
