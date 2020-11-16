# MWIS Scraper

This repo contains a Python script which can scrape weather forecast data from MWIS, to be stored in a pandas dataframe.

Currently configured to extract:

 1. How wet?
 2. How cold at 900m?
 3. How windy?

From each of the the three main highland regions.


## Crontab

Set up cron to run the script once per day in the evening:

 1. Run `cron -e` to start editing your crontab
 2. Add the line: `0 19 * * * grep /path/to/env/python /path/to/scrape_latest_forecast.py`
 3. Optionally also add `0 20 * * * /path/to/push_latest_forecast.sh` to push latest data to github immediately

The log messages are sent to `/var/mail/username`
