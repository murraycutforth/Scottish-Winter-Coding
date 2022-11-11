WD := $(shell pwd)

all: env cronjobs;

cronjobs: mwis-cronjob

env: requirements.txt
	virtualenv swc-env
	. swc-env/bin/activate; python -m pip install -r requirements.txt

mwis-cronjob:
	{ crontab -l; echo "0 */3 * * * . ${WD}/swc-env/bin/activate && python ${WD}/src/scrape_latest_mwis.py"; } | crontab -

