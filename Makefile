WD := $(shell pwd)

all: env cronjobs;

cronjobs: mwis-cronjob

env: requirements.txt
	virtualenv swc-env
	. swc-env/bin/activate; python -m pip install -r requirements.txt; python -m spacy download en_core_web_sm

mwis-cronjob:
	{ crontab -l; echo "0 */3 * * * . ${WD}/swc-env/bin/activate && cd ${WD} && python -m  src.scrape_latest_mwis"; } | crontab -

