# MWIS Scraper

This repo contains a Python script which can scrape weather forecast data from MWIS, to be stored in a pandas dataframe.

Currently configured to extract: How wet, How cold at 900, and how windy (for the three main highland areas).


## Crontab

Set up cron to run the script once per day in the evening:

 1. Run `cron -e` to start editing your crontab
 2. Add the line: `0 19 * * * grep /path/to/env/python /path/to/scrape_latest_forecast.py`
 3. Optionally also add `0 20 * * * /path/to/push_latest_forecast.sh` to push latest data to github immediately

The log messages are sent to `/var/mail/username`
