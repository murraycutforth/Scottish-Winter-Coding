REMOTENAME=MyGoogleDrive

all: env mwis-cronjob cic-cronjob data-backup-cronjob;

env:
	conda env create --force -f environment.yml

mwis-cronjob:
	{ crontab -l; echo "0 19 * * * ${HOME}/miniconda3/envs/scottishwinter/bin/python3.6 $(pwd)/src/scrape_latest_mwis.py"; } | crontab -

cic-cronjob:
	{ crontab -l; echo "0 19 * * * ${HOME}/miniconda3/envs/scottishwinter/bin/python3.6 $(pwd)/src/scrape_latest_cic.py"; } | crontab -

data-backup-cronjob:
	{ crontab -l; echo "0 20 * * * rclone copy $(pwd)/data ${REMOTENAME}:Scottish-Winter-Coding/data"; } | crontab -
