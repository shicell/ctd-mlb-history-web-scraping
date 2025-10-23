# ctd-mlb-history-web-scraping

This series of programs is meant to gather data and develop a dashboard from the website https://www.baseball-almanac.com/yearmenu.shtml

1. web_scraping.py
The project begins with webscraping where raw data is gathered from the website. Data on stolen bases and some details on
players is gathered. 
To initiate you can enter the command `py web_scraping.py` to a terminal, once in the `ctd-mlb-history-web-scraping` directory.

2. clean.py
The project then moves to cleaning the raw data which was extracted. This is needed so that it can be easier to create a
database. In addition to creating clean tables, it also stores any items which were removed from each table.
To initiate you can enter the command `py clean.py` to a terminal, once in the `ctd-mlb-history-web-scraping` directory.

3. sql_database.py
This program then creates a database from the cleaned tables created by clean.py.
To initiate you can enter the command `py sql_database.py` to a terminal, once in the `ctd-mlb-history-web-scraping` directory.

4. query.py
This program allows for you to query the created databased via the command line. You can enter in some variable to view results from three predefined queries.
To view you can enter the command `py query.py` to a terminal, once in the `ctd-mlb-history-web-scraping` directory.

5. myapp.py
This program generates 3 visualizations based on the database created and uses dash to generate them. They can be filtered by year, league, and teams. 
To view them, the Render website below can be visited or you can enter the command `py myapp.py` to a terminal to run locally. One must visit the link below to view locally.
Link to view locally: http://localhost:8050/
Link to Render website: https://shicell-santos-ctd-mlb-history-web.onrender.com/
