"""Create database based on tables from cleaned data"""
import sqlite3
import pandas as pd

try:
    # Connect to SQLite database, db/base_running.db
    yoy_leader_df = pd.read_csv("cleaned_data/bases_stolen_league_leaders_cleaned.csv")
    career_stats_df = pd.read_csv("cleaned_data/base_running_stats_cleaned_career.csv")
    year_stats_df = pd.read_csv("cleaned_data/base_running_stats_cleaned_yoy.csv")
    salary_df = pd.read_csv("cleaned_data/player_salary_cleaned.csv")
    player_df = yoy_leader_df[["Player ID", "Player Name"]].drop_duplicates()

    with sqlite3.connect("db/base_running.db") as conn:
        print("Database created successfully")

        conn.execute("PRAGMA foreign_keys = 1")
        cursor = conn.cursor()

        # Define Database Structure
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL 
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS yoy_leader (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            league TEXT NOT NULL,
            player_id TEXT NOT NULL,
            team TEXT NOT NULL,
            bases_stolen INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_career_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            total_bases_stolen INTEGER NOT NULL,
            total_caught_stealing INTEGER NOT NULL,
            total_sb_perc FLOAT NOT NULL,
            total_years INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_yearly_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            bases_stolen INTEGER NOT NULL,
            caught_stealing INTEGER NOT NULL,
            stolen_base_perc FLOAT NOT NULL,
            year INTEGER NOT NULL,
            team TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )
        """)

        cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS player_salary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            uniform_nums TEXT,
            salary FLOAT,
            year INTEGER NOT NULL,
            team TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES players (player_id)
        )""")

        print("Tables created successfully.")

        # Add entries to tables
        for _, row in player_df.iterrows():
            cursor.execute(
                """
                INSERT INTO players (player_id, name)
                VALUES (?, ?)
                """, (row["Player ID"], row["Player Name"]))

        for _, row in yoy_leader_df.iterrows():
            cursor.execute(
                """
                INSERT INTO yoy_leader (year, league, player_id, team, bases_stolen)
                VALUES (?, ?, ?, ?, ?)
                """, (row["Year"], row["League"], row["Player ID"], row["Team"], row["Bases Stolen"]))

        for _, row in career_stats_df.iterrows():
            cursor.execute(
                """
                INSERT INTO player_career_stats (player_id, total_bases_stolen, total_caught_stealing, total_sb_perc, total_years)
                VALUES (?, ?, ?, ?, ?)
                """, (row["Player ID"], row["Stolen Bases (SB)"], row["Caught Stealing (CS)"], row["Stolen Bases Percentage"], row["Total Years"]))

        for _, row in year_stats_df.iterrows():
            cursor.execute(
                """
                INSERT INTO player_yearly_stats (player_id, bases_stolen, caught_stealing, stolen_base_perc, year, team)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (row["Player ID"], row["Stolen Bases (SB)"], row["Caught Stealing (CS)"], row["Stolen Bases Percentage"], row["Year"], row["Team"]))

        for _, row in salary_df.iterrows():
            cursor.execute(
                """
                INSERT INTO player_salary (player_id, uniform_nums, salary, year, team)
                VALUES (?, ?, ?, ?, ?)
                """, (row["Player ID"], row["Uniform Numbers"], row["Salary"], row["Year"], row["Team"]))

        conn.commit()
        print("Tables populated successfully.")


except Exception as e:
    print(f"Database could not be created: {e}")
