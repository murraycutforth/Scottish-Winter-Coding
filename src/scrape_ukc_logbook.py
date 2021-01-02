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
import re


def main():
    driver = get_web_driver(profile_path=gin.REQUIRED, crag_url=gin.REQUIRED)
    time.sleep(5)
    routes, crag_name = find_all_routes(driver.page_source)

    print(f'Successfully fetched crag page for {crag_name}')
    print(f'Found a total of {len(routes)} routes on page')

    route_info = []

    for r in routes:
        route_url = extract_route_url(r)
        route_name = extract_route_name(r)
        route_type = extract_route_type(r)
        route_grade = extract_route_grade(r)

        logs = extract_route_logbook(route_url, driver)
        logbook_path = get_logbook_path(crag_name, route_name)

        route_info.append((route_name, route_type, route_grade, logbook_path))
        logs.to_csv(logbook_path)
        
        print(f'Processing complete for name={route_name}, type={route_type}, grade={route_grade}')

        time.sleep(2)

    write_crag_csv(crag_name, route_info)

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
    crag_name = extract_crag_name(soup)

    return routes, crag_name


def extract_crag_name(c: BeautifulSoup) -> str:
    return ' '.join(c.title.text.split()[3:])


def get_crag_path(crag_name: str) -> Path:
    data_path = Path('./../data')  # Assumption that script is being run from src dir

    crag_path = data_path / 'UKC' / re.sub('\s\W', '_', crag_name)

    if not crag_path.exists():
        crag_path.mkdir(parents=True)

    return crag_path.resolve()


def write_crag_csv(crag_name: str, route_info: List) -> None:
    col_name = ['Name', 'Type', 'Grade', 'Logbook path']
    col_data = zip(*route_info)
    crag_path = get_crag_path(crag_name)
    
    df = pd.DataFrame({k:v for k, v in zip(col_name, col_data)})
    df.to_csv(crag_path / 'crag_overview.csv')
    



def get_logbook_path(crag_name: str, route_name: str) -> Path:
    crag_path = get_crag_path(crag_name)

    (crag_path / 'logbooks').mkdir(exist_ok=True)

    logbook_path = crag_path / 'logbooks' / (re.sub('[\s\W]', '_', route_name) + '.csv')

    if logbook_path.exists():
        # Deal with case where summer and winter routes have same name
        logbook_path = logbook_path.with_name(logbook_path.stem + '_.csv')

    return logbook_path





def extract_route_logbook(route_url: str, driver: webdriver.Chrome) -> pd.DataFrame:
    driver.get(route_url)
    time.sleep(2)

    # This returns 1-4 tables: feedback, my logs, partners logs, and public logs
    # We want to merge the third and fourth tables, and drop the first two (if exists)
    # The partner/public log tables have slightly different column headers, and are renamed.
    try:
        tables = pd.read_html(driver.page_source)[-2:]

        if tables[0].shape[1] != 4:
            if len(tables) == 2:
                tables = tables[1:]
            else:
                raise ValueError

        for i in range(len(tables)):
            assert tables[i].shape[1] == 4

            # Tidy up - the following two lines seem to do the job
            tables[i] = tables[i].dropna(how='all')
            tables[i] = tables[i][tables[i].nunique(axis=1).ne(1)]

            # Rename four columns
            tables[i].columns = ['User', 'Date', 'Style', 'Notes & Partners']
        
        df = pd.concat(tables, axis=0).reset_index(drop=True)

    except ValueError:
        df = pd.DataFrame({})

    return df


def extract_route_info(page_source: str):
    soup = BeautifulSoup(page_source, 'html.parser')

    x = open('temproutepage', 'w')
    x.write(soup.prettify())


def extract_route_type(r: BeautifulSoup) -> str:
    """Returns type of route, e.g. "Winter"/"Trad"/"Summit"
    """
    return r.parent.parent.find('td', {'class', 'datatable_column_type'}).span['title']


def extract_route_name(r: BeautifulSoup) -> str:
    return r.text.strip()


def extract_route_grade(r: BeautifulSoup) -> str:
    return r.parent.parent.find('td', {'class', 'datatable_column_grade'}).text.strip()


def extract_route_url(r: BeautifulSoup) -> str:
    return 'http://www.ukclimbing.com' + r['href'] + '#public_logbooks'



if __name__ == '__main__':
    gin.parse_config_file('ukc_config.gin', skip_unknown=True)
    main()
