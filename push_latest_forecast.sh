#!/bin/sh

cd /home/murray/Projects/MWIS-Scraper
git add data/mwis_forecasts.csv
git add data/cic_observations.csv
git commit -m "Auto commit with forecast data"
git push
