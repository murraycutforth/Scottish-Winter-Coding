TODO:

- refactor out pandas from the mwis parsing, just parse html directly into the sqlite table
- directly extract date from the mwis forecast page, and then update database appropriately using date (so can be run all day)
- package code as executable using pyinstaller, so can easily be distributed
- set up makefile to enable packaging
- set up makefile to use cronjob to attempt scraping every hour

- update cic code
