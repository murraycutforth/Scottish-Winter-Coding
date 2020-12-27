"""Script which scrapes logbook information from UKC

Author:
    Murray Cutforth
"""
import chromedriver_binary
from pathlib import Path
from typing import *
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
import time
import pandas as pd
import gin


def main():
    driver = get_web_driver(profile_path=gin.REQUIRED, crag_url=gin.REQUIRED)
    print('Successfully fetched crag page')

    time.sleep(5)

    routes = find_all_routes(driver.page_source)
    print(f'Found a total of {len(routes)} routes on page')

    for route in routes[18:20]:
        route_url = 'http://www.ukclimbing.com' + route['href'] + '#public_logbooks'
        process_single_route_page(route_url, driver)

        time.sleep(5)

    print('Script completed normally')


@gin.configurable()
def get_web_driver(profile_path: str, crag_url: str):
    options = webdriver.ChromeOptions()
    options.add_argument("user-data-dir=" + profile_path)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(crag_url)

    return driver


def find_all_routes(page_source: str):
    soup = BeautifulSoup(page_source, 'html.parser')
    routes = soup.find_all('a', {'class', 'small not-small-md'}, href=True)

    return routes


def process_single_route_page(route_url: str, driver: webdriver.Chrome):
    driver.get(route_url)
    print('Looking at route page:', route_url)

    # Extract route name, grade, type
    info = extract_route_info(driver.page_source)

    # This returns either 2 or 3 tables: feedback, partners logs, and public logs
    # We want to merge the second and third tables, and drop the first (if it exists)
    # The partner/public log tables have slightly different column header names.
    tables = pd.read_html(driver.page_source)

    if len(tables) == 3:
        tables = tables[1:]

    assert len(tables) == 2 or len(tables) == 1

    for i in range(len(tables)):
        assert tables[i].shape[1] == 4

        # Tidy up - the following two lines seem to do the job
        tables[i] = tables[i].dropna(how='all')
        tables[i] = tables[i][tables[i].nunique(axis=1).ne(1)]

        # Rename four columns
        tables[i].columns = ['User', 'Date', 'Style', 'Notes & Partners']
    
    df = pd.concat(tables, axis=0).reset_index(drop=True)

    print(df)


def extract_route_info(page_source: str):
    soup = BeautifulSoup(page_source, 'html.parser')

    x = open('temproutepage', 'w')
    x.write(soup.prettify())


if __name__ == '__main__':
    gin.parse_config_file('ukc_config.gin', skip_unknown=True)
    main()
