WD := $(shell pwd)

.PHONY: mwis-cronjob, all

all:
	echo "No default make target. Choose from env, env_scraper, cronjobs"

cronjobs: mwis-cronjob

env: requirements.txt
	virtualenv swc-env
	. swc-env/bin/activate; python -m pip install -r requirements.txt; python -m spacy download en_core_web_md

env_scraper: requirements_scraper_only.txt
	virtualenv swc-scraper-env
	. swc-scraper-env/bin/activate; python -m pip install -r requirements_scraper_only.txt

mwis-cronjob:
	{ crontab -l; echo "0 */3 * * * . ${WD}/swc-scraper-env/bin/activate && cd ${WD} && python -m  src.scrape_latest_mwis"; } | crontab -

