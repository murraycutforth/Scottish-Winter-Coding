# Scottish-Winter-Coding

This repo contains a bunch of Python and shell scripts related to weather and conditions analysis for Scottish winter climbing.
Some scripts are designed to be run daily (using `cron`) to extract current MWIS forecasts and CIC observations, while others can just be run once, such as the script used to store UKC logbook information.
`rclone` is used to back up all data to Google Drive. The `selenium` and `beautifulsoup` packages are used for web scraping. All data is processed using Pandas and stored in a SQLite database.


## Getting Started

### Setting up the MWIS scraper

A makefile is provided to automate the setup process, a unix OS is required for this.

 - Run `make env_scraper` to create a virtualenv called `swc-scraper-env` which will be used by the code
 - Run `make cronjobs` to modify the user crontab to scrape conditions data every 3 hours (duplicate data is handled properly)
 
The resulting data is stored in a SQLite database at `~/scottish-winter-coding/data.db`. 

### Setting up environment for other functionality

 - Run `make env` to create a virtualenv called `swc-env`


## Functionality

### MWIS

All forecast fields from the MWIS website are saved.

### CIC

TODO: this part of the scraper needs to be refactored. The aim will be to scrape:

 1. Max/min temperature
 2. Max/min wind speed
 3. Max/min humidity

From the past 24 hours at the CIC hut.

### UKC

Currently set up so that when pointed at a crag overview page, the script extracts all winter routes on the crag, and then iterates through them and stores a separate csv file for each logbook. The code is purposefully slowed down to be kind to the UKC servers (if you're reading this Alan James, pls don't ban me). Just needs to be run once to get all historical logbook data in one go. Because logbook information is only visible to members, you need to first run the ukc\_login.py script (and click the 'stay logged in' box). This stores login cookies in the path specified in the config file, and then uses these to log in automatically in the scraper script.


## Previous data

Some data which I have collected during winter 2021/2022 during an early incarnation of this project is available here in a csv format: https://drive.google.com/drive/folders/1hlkd8XGGwuV2eQZz11RnEQknbp7bJOtx?usp=sharing
