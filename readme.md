# Scottish-Winter-Coding

This repo contains a bunch of Python and shell scripts related to weather and conditions analysis for Scottish winter climbing.
Some scripts are designed to be run daily (using `cron`) to extract current MWIS forecasts and CIC observations, while others can just be run once, such as the script used to store UKC logbook information.
`rclone` is used to back up all data to Google Drive. The `selenium` and `beautifulsoup` packages are used for web scraping. All data is processed using Pandas and stored as .csv files.


## Getting Started

 - Install miniconda (https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html). If you install in a non-standard location you will need to change the Makefile.

 - Install and configure rclone by running:
```
sudo apt install rclone
rclone config
```
and follow the interactive prompts to set up a remote with any cloud storage provider. Set the name to "MyGoogleDrive", otherwise edit the REMOTENAME variable in the makefile.

 - Next, just run `make all`. This uses the simple Makefile in the project to automatically set up the Python environment, and add crontab entries to scrape and back up MWIS and CIC data daily.
Each script has a corresponding gin-config file which contains any parameters used by the script. Be careful to just run `make all` once, as running it repeatedly will add duplicates to the crontab. 

Data which I have scraped is available here: https://drive.google.com/drive/folders/1hlkd8XGGwuV2eQZz11RnEQknbp7bJOtx?usp=sharing

### MWIS

Currently configured to extract:

 1. How wet?
 2. How cold at 900m?
 3. How windy?

From each of the the three main highland regions, for all 3 forecast dates.


### CIC

Currently configured to extract:

 1. Max/min temperature
 2. Max/min wind speed
 3. Max/min humidity

From the past 24 hours at the CIC hut.


### UKC

Currently set up so that when pointed at a crag overview page, the script extracts all winter routes on the crag, and then iterates through them and stores a separate csv file for each logbook. The code is purposefully slowed down to be kind to the UKC servers (if you're reading this Alan James, pls don't ban me). Just needs to be run once to get all historical logbook data in one go. Because logbook information is only visible to members, you need to first run the ukc\_login.py script (and click the 'stay logged in' box). This stores login cookies in the path specified in the config file, and then uses these to log in automatically in the scraper script.
