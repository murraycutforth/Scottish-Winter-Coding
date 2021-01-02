REMOTENAME := MyGoogleDrive
WD := $(shell pwd)

all: env cronjobs;

cronjobs: mwis-cronjob cic-cronjob data-backup-cronjob;

env: environment.yml
	conda env create --force -f environment.yml

mwis-cronjob:
	{ crontab -l; echo "0 19 * * * PROJ_DIR=${WD} ${HOME}/miniconda3/envs/scottishwinter/bin/python3.6 ${WD}/src/scrape_latest_mwis.py"; } | crontab -

cic-cronjob:
	{ crontab -l; echo "0 19 * * * PROJ_DIR=${WD} ${HOME}/miniconda3/envs/scottishwinter/bin/python3.6 ${WD}/src/scrape_latest_cic.py"; } | crontab -

data-backup-cronjob:
	{ crontab -l; echo "0 20 * * * rclone copy ${WD}/data ${REMOTENAME}:Scottish-Winter-Coding/data"; } | crontab -
