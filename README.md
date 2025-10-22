# ctd-mlb-history-web-scraping

This series of programs is meant to gather data and develop a dashboard from the website https://www.baseball-almanac.com/yearmenu.shtml


1. web_scraping.py
The project begins with webscraping where raw data is gathered from the website. Data on stolen bases and some details on
players is gathered. 

2. clean.py
The project then moves to cleaning the raw data which was extracted. This is needed so that it can be easier to create a
database. In addition to creating clean tables, it also stores any items which were removed from each table.

3. sql_database.py
This program then creates a database from the cleaned tables created by clean.py.

4. query.py
This program allows for you to query the created databased via the command line. You can enter in some variable to view results from three predefined queries.

5. vizualization.py
