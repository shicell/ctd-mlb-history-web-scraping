"""This program gathers data from the website https://www.baseball-almanac.com/ 
via web scraping with Selenium"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# initialize Selenium and the appropriate driver
# configure driver to run in 'headless' mode
options = Options()
options.add_argument('--headless')  # Enable headless mode
options.add_argument('--disable-gpu')  # Optional, recommended for Windows
options.add_argument('user-agent=Mozilla/5.0')
options.add_argument("--log-level=3")

# fetch a web page
yearly_data = []
base_running_stats = []
player_salary = []

try:
    driver = webdriver.Chrome(options=options)

    # visit the website for bases stolen leadership board
    driver.get("https://www.baseball-almanac.com/hitting/hisb4.shtml")
    wait = WebDriverWait(driver, 10)

    # look for a table
    table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]

    # gather all data from leadership board and store to a table called yearly data
    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) == 8:
                year_al = cells[0].text.strip()
                player_al = cells[1]
                bases_al = cells[2].text.strip()
                team_al = cells[3].text.strip()

                year_nl = cells[4].text.strip()
                player_nl = cells[5]
                bases_nl = cells[6].text.strip()
                team_nl = cells[7].text.strip()

                # to gather data on players, their id must be gathered and stored
                # the id can be found as part of the link, at the end. Only the ending player id is gathered not the entire link
                player_al_id = ""
                player_al_name = player_al.text.strip()
                player_al_href = player_al.find_elements(By.CSS_SELECTOR, 'a[href]')
                if player_al_href:
                    player_al_link = player_al_href[0].get_attribute('href').strip()
                    _, _, player_al_id = player_al_link.partition("p=")

                player_nl_id = ""
                player_nl_name = player_nl.text.strip()
                player_nl_href = player_nl.find_elements(By.CSS_SELECTOR, 'a[href]')
                if player_nl_href:
                    player_nl_link = player_nl_href[0].get_attribute('href').strip()
                    _, _, player_nl_id = player_nl_link.partition("p=")
                
                # add row from table on website to table yearly data
                yearly_data.append([year_al, "American League", player_al_id, player_al_name, team_al, bases_al])
                yearly_data.append([year_nl, "National League", player_nl_id, player_nl_name, team_nl, bases_nl])

        except Exception as row_err:
            print(f"Row Exception: {type(row_err).__name__} {row_err}")

    # once yearly data has be retrieved, need to gather data on players
    # to not go to the same player pager multiple time, unique values were gathered
    player_ids = list(set(row[2] for row in yearly_data if row[2]))
    index = 0

    # go to each player's page. The base link is the same but the player ids differ
    # This player id will allow for it to be easier to match between the yearly table
    # and table related to players
    for player in player_ids:
        index = index + 1
        print(f"Page {index} of {len(player_ids)}") # used to help keep track of how many pages were scraped
        try:
            # go to each indivual player page
            time.sleep(5)
            driver.get(f"https://www.baseball-almanac.com/players/player.php?p={player}")
            wait = WebDriverWait(driver, 10)

            # get all tables on page
            tables = driver.find_elements(By.TAG_NAME, "table")

            # get second to last table, which stores overall base running stats
            base_running_stats_table = tables[-2]
            brs_rows = base_running_stats_table.find_elements(By.TAG_NAME, "tr")[1:]
            for row in brs_rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")

                    if len(cells) == 13:
                        team = cells[0].text.strip()
                        sb = cells[1].text.strip()
                        cs = cells[2].text.strip()
                        sb_per = cells[3].text.strip()

                        # add to base running stats table
                        base_running_stats.append([player, team, sb, cs, sb_per])

                except Exception as row_err:
                    print(f"Row Exception: {type(row_err).__name__} {row_err}")

            # get last table which stores information on player salary
            salary_table = tables[-1]
            salary_rows = salary_table.find_elements(By.TAG_NAME, "tr")[1:]
            for row in salary_rows:
                try:
                    cells = row.find_elements(By.TAG_NAME, "td")

                    if len(cells) == 5:
                        team_roster = cells[0].text.strip()
                        uniform_number = cells[1].text.strip()
                        salary = cells[2].text.strip()

                        # add to player salary table
                        player_salary.append([player, team_roster, uniform_number, salary])

                except Exception as row_err:
                    print(f"Row Exception: {type(row_err).__name__} {row_err}")
        except Exception as e:
            print(f"Exception: {type(e).__name__} {e}")
except Exception as e:
    print(f"Exception: {type(e).__name__} {e}")

finally:
    driver.quit()

try:
    # store each table into a csv file
    yearly_df = pd.DataFrame(yearly_data,
                             columns=["Year", "League",
                                      "Player ID", "Player Name",
                                      "Team", "Bases Stolen"])
    yearly_df.to_csv("raw_data/bases_stolen_league_leaders.csv", index=False)
    print("Saved bases_stolen_league_leaders.csv")

    base_stat_df = pd.DataFrame(base_running_stats,
                                columns=["Player ID",
                                         "Team", "Stolen Bases (SB)",
                                         "Caught Stealing (CS)",
                                         "Stolen Bases Percentage"])
    base_stat_df.to_csv("raw_data/base_running_stats.csv", index=False)
    print("Saved base_running_stats.csv")

    salary_df = pd.DataFrame(player_salary,
                             columns=["Player ID", "Team",
                                      "Uniform Numbers", "Salary"])
    salary_df.to_csv("raw_data/player_salary.csv", index=False)
    print("Saved player_salary.csv")

except Exception as file_err:
    print(f"File Exception: {type(file_err).__name__} {file_err}")
