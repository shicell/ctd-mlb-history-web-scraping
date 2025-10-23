"""This program allows users to query the database base_running from 3 predefined queries"""
import sqlite3

# allows you to connect to database when needed
def get_connected():
    try:
        return sqlite3.connect("db/base_running.db")
    except sqlite3.Error as e:
        print(f"Error connecting to DB: {e}")
        return None

# shows menu of options to pick from
def show_menu():
    print("\nQuery options include:")
    print("1. Top N players from range of years by salary")
    print("2. Top N players by Stolen Base Percentage of Leading Year in a team")
    print("3. Top N players by Difference between Leadership Stolen Base Percentage" \
            "and overall Stolen Base Percentage")
    print("4. Exit")

# first query option
def option_1(conn):
    try:
        # print instructions to user
        print("\nYou will be asked to enter values for a varierty of variables.")
        print("To skip, leave entry blank. Input will include:")
        print("    year (start): the lower bound of for year, from which players" \
              "were top base stealers")
        print("    year (end): the upper bound of for year, from which players" \
              "were top base stealers")
        print("    top n: the maximum number of players to display, ordered by" \
              "salary descending. Default is 10.")

        # validate input
        while True:
            year_start = input("Enter year (start): ").strip()
            try:
                if not year_start:
                    year_start = 1900
                year_start = int(year_start)
                break  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        while True:
            year_end = input("Enter year (end): ").strip()
            try:
                if not year_end:
                    year_end = 3000
                year_end = int(year_end)
                break  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        while True:
            top_n = input("Enter top n: ").strip()
            try:
                if not top_n:
                    top_n = 10
                top_n = int(top_n)
                break  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # send query and get results
        cursor = conn.execute(
            """SELECT l.year, p.name, s.salary
            FROM yoy_leader as l
            LEFT JOIN players as p on l.player_id = p.player_id
            LEFT JOIN player_salary as s on l.player_id = s.player_id and l.year = s.year
            WHERE l.year BETWEEN ? AND ?
            ORDER BY s.salary desc
            LIMIT ?
            """, (year_start, year_end, top_n))

        results = cursor.fetchall()

        # print results to user
        if results:
            print(f"\nTop {top_n} players by salary: ")
            print("\nYear: Player Name - Salary")
            for row in results:
                print(f"{row[0]}: {row[1]} - ${row[2]:,.2f}")
        else:
            print("No results found.")
    except Exception as e:
        print(f"Error: {e}")

# second query option
def option_2(conn):
    try:
        # print instructions to user
        print("\nYou will be asked to enter values for a varierty of variables.")
        print("To skip, leave entry blank. Input will include:")
        print("    team: the name of the team from either the American or National League " \
        "(eg. Miami)")
        print("    top n: the maximum number of players to display, ordered by Stolen Base" \
              "Percentage descending. Default is 10.")

        # validate input
        selected_team = input("Enter team: ").strip()
        all_team = 1 if not selected_team else 0

        while True:
            top_n = input("Enter top n: ").strip()
            try:
                if not top_n:
                    top_n = 10
                top_n = int(top_n)
                break  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # send query and get results
        cursor = conn.execute(
            """
            SELECT l.year, p.name, s.stolen_base_perc, l.team
            FROM yoy_leader as l
            LEFT JOIN players as p on l.player_id = p.player_id
            LEFT JOIN player_yearly_stats as s on l.player_id = s.player_id and l.year = s.year
            WHERE l.team = ? OR ? = 1
            ORDER BY s.stolen_base_perc desc
            LIMIT ?
            """, (selected_team, all_team, top_n))
        
        # print results to user
        results = cursor.fetchall()
        if results:
            print(f"\nTop {top_n} players by Stolen Base %: ")
            print("\nYear: Team, Player Name - Stolen Base Perc")
            for row in results:
                print(f"{row[0]}: {row[3]}, {row[1]} - {row[2]:.2f}")
        else:
            print("No results found.")
    except Exception as e:
        print(f"Error: {e}")

# third query option
def option_3(conn):
    try:
        # print instructions to user
        print("You will be asked to enter values for a varierty of variables. ")
        print("To skip, leave entry blank. Input will include: ")
        print("    max threshold: maximum difference between the player's leadership and " \
              "overall Stolen Base Percentage")
        print("    top n: the maximum number of players to display, ordered by difference " \
                "descending. Default is 10.")
        
        # validate input
        while True:
            threshold = input("Enter max threshold: ").strip()
            try:
                if not threshold:
                    threshold = 100
                threshold = float(threshold)
                break  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        while True:
            top_n = input("Enter top n: ").strip()
            try:
                if not top_n:
                    top_n = 10
                top_n = int(top_n)
                break  # Exit the loop if conversion is successful
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        # send query and get results
        cursor = conn.execute("""
            SELECT l.year, p.name, s.stolen_base_perc, c.total_sb_perc,
                               ABS(s.stolen_base_perc - c.total_sb_perc) AS diff
            FROM yoy_leader as l 
            LEFT JOIN players as p on l.player_id = p.player_id 
            LEFT JOIN player_yearly_stats as s on l.player_id = s.player_id 
                      and l.year = s.year 
            LEFT JOIN player_career_stats as c on l.player_id = c.player_id 
            WHERE ABS(s.stolen_base_perc - c.total_sb_perc) <= ? 
                   AND s.stolen_base_perc > 0
                   AND c.total_sb_perc > 0
            ORDER BY ABS(s.stolen_base_perc - c.total_sb_perc) desc 
            LIMIT ?
            """, (threshold, top_n))
        
        # print results to user
        results = cursor.fetchall()
        if results:
            print(f"\nTop {top_n} players by salary: ")
            print("\nYear: Player Name - SB Per from Year - SB Per from Career - Difference")
            for row in results:
                print(f"{row[0]}: {row[1]} - {row[2]:.2f} - {row[3]:.2f} - {row[4]:.2f}")
        else:
            print("No results found.")
    except Exception as e:
        print(f"Error: {e}")

# Print welcome and manage flow of query request
print("Welcome! With this menu, you will be able to query the base_running db.")
query_num = "0"
while query_num != "4":
    show_menu()
    query_num = input("Please enter query selection: ").strip()

    match query_num:
        case "1": option_1(get_connected())
        case "2": option_2(get_connected())
        case "3": option_3(get_connected())
        case "4": print("Thank you for exploring! Have a good day!")
        case _: print("That was an invalid entry, please try again.")

