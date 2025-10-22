import pandas as pd

### Clean YoY stats first
# Read files and display information
original_yoy_df = pd.read_csv("raw_data/bases_stolen_league_leaders.csv")
print(f"bases_stolen_league_leaders\n{original_yoy_df.head(5)}")
print(f"original_yoy_df.dtypes\n{original_yoy_df.dtypes}")

# filter for valid rows, which will have valid years
valid_year = original_yoy_df["Year"].str.isdigit()
valid_league = original_yoy_df["League"].isin(["American League", "National League"])
valid_base = original_yoy_df["Bases Stolen"].str.isdigit()

# combine all validations together
is_valid = valid_year & valid_league & valid_base

# seperate valid and remove rows
removed_rows_yoy = original_yoy_df[is_valid == False]
valid_rows_yoy = original_yoy_df[is_valid == True]

# save removed rows
removed_rows_yoy.to_csv("removed_data/bases_stolen_league_leaders_removed.csv",
                        index=False)

# clean valid data
yoy_df = valid_rows_yoy.copy()
yoy_df["Year"] = yoy_df["Year"].astype(int)
yoy_df["Player ID"] = yoy_df["Player ID"].astype(str).str.strip()
yoy_df["Player Name"] = yoy_df["Player Name"].astype(str).str.strip()
yoy_df["Team"] = yoy_df["Team"].astype(str).str.strip()
yoy_df["Bases Stolen"] = yoy_df["Bases Stolen"].astype(int)

# save final cleaned data
print(f"yoy_df.shape\n{list(yoy_df.shape)}")
yoy_df.to_csv("cleaned_data/bases_stolen_league_leaders_cleaned.csv", index=False)

print(f"\nremoved_rows.shape\n{removed_rows_yoy.shape}")
print("\nSaved: bases_stolen_league_leaders_removed " + \
      "and bases_stolen_league_leaders_cleaned")


### Clean base_running_stats
# Read files and display information
original_stats_df = pd.read_csv("raw_data/base_running_stats.csv")
print(f"base_running_stats\n{original_stats_df.head(5)}")
print(f"original_stats_df.dtypes\n{original_stats_df.dtypes}")

# filter for valid rows, which will have valid years
valid_year_team = original_stats_df["Team"].astype(str).str.match(r"\d+ \w+", na=False)
valid_sb = original_stats_df["Stolen Bases (SB)"].str.contains(r"(\d|-)", na=False)
valid_cs = original_stats_df["Caught Stealing (CS)"].str.contains(r"(\d|-)", na=False)
valid_sbp = original_stats_df["Stolen Bases Percentage"].str.contains(r"(\d|-)", na=False)

# combine all validations together
is_valid = valid_year_team & valid_sb & valid_cs & valid_sbp

# seperate valid and remove rows
removed_rows_stats = original_stats_df[is_valid == False]
valid_rows_stats = original_stats_df[is_valid == True]

# save removed rows
removed_rows_stats.to_csv("removed_data/base_running_stats_removed.csv", 
                        index=False)

# clean valid data
stats_df = valid_rows_stats.copy()
stats_df.rename(columns={"Team": "Year and Team"}, inplace=True)
stats_df[["Year", "Team"]] = stats_df["Year and Team"].str.split(" ", n=1, expand=True)
stats_df = stats_df.drop(columns=["Year and Team"])
stats_df["Year"] = stats_df["Year"].astype(int)
stats_df["Team"] = stats_df["Team"].astype(str).str.strip()
stats_df["Stolen Bases (SB)"] = stats_df["Stolen Bases (SB)"].replace("[,-]", "", regex=True).replace("", 0).astype(int)
stats_df["Caught Stealing (CS)"] = stats_df["Caught Stealing (CS)"].replace("[,-]", "", regex=True).replace("", 0).astype(int)
stats_df["Stolen Bases Percentage"] = stats_df["Stolen Bases Percentage"].replace("[-]", "", regex=True).replace("", 0).astype(float)

# seperate career from year over year stats
stats_yoy_df = stats_df[stats_df["Team"] != "Years"]
career_df = stats_df[stats_df["Team"] == "Years"]
career_df = career_df.drop(columns=["Team"])
career_df = career_df.rename(columns={"Year":"Total Years"})

# save final cleaned data
print(f"stats_df.shape\n{stats_df.shape}")
stats_df.to_csv("cleaned_data/base_running_stats_cleaned.csv", index=False)
stats_yoy_df.to_csv("cleaned_data/base_running_stats_cleaned_yoy.csv", index=False)
career_df.to_csv("cleaned_data/base_running_stats_cleaned_career.csv", index=False)

print(f"\nremoved_rows_stats.shape\n{removed_rows_stats.shape}")
print("\nSaved: base_running_stats_removed, " + \
      "base_running_stats_cleaned, " + \
      "base_running_stats_cleaned_yoy, and" + \
      "base_running_stats_cleaned_career"
        )


### Clean base_running_stats
# Read files and display information
original_salary_df = pd.read_csv("raw_data/player_salary.csv")
print(f"bases_stolen_league_leaders\n{original_salary_df.head(5)}")
print(f"original_salary_df.dtypes\n{original_salary_df.dtypes}")

# filter for valid rows, which will have valid years
valid_year_team = original_salary_df["Team"].astype(str).str.match(r"\d+ \w+", na=False)
valid_uni_num = original_salary_df["Uniform Numbers"].str.contains(r"(\d|-|n/a)", na=False)
valid_salary = original_salary_df["Salary"].str.contains(r'(Undetermined|$|")', na=False)

# combine all validations together
is_valid = valid_year_team & valid_uni_num & valid_salary

# seperate valid and remove rows
removed_rows_salary = original_salary_df[is_valid == False]
valid_rows_salary = original_salary_df[is_valid == True]

# save removed rows
removed_rows_salary.to_csv("removed_data/player_salary_removed.csv", 
                        index=False)

# clean valid data
salary_df = valid_rows_salary.copy()
salary_df.rename(columns={"Team": "Year and Team"}, inplace=True)
salary_df[["Year", "Team"]] = salary_df["Year and Team"].str.split(" ", n=1, expand=True)
salary_df = salary_df.drop(columns=["Year and Team"])
salary_df["Year"] = salary_df["Year"].astype(int)
salary_df["Team"] = salary_df["Team"].astype(str).str.strip()
salary_df["Uniform Numbers"] = salary_df["Uniform Numbers"].astype(str).str.strip()

# salary will need more work since values will need to be
# altered and be filled by most recent salary if na
salary_df["Salary"] = salary_df["Salary"].astype(str).str.strip()
salary_df["Salary"] = salary_df["Salary"].replace('"     "', None)
salary_df["Salary"] = salary_df["Salary"].fillna(method="ffill")
salary_df["Salary"] = salary_df["Salary"].replace("Undetermined", None)
salary_df["Salary"] = salary_df["Salary"].replace("[\$,]", "", regex=True).astype(float)

# save final cleaned data
print(f"salary_df.shape\n{salary_df.shape}")
salary_df.to_csv("cleaned_data/player_salary_cleaned.csv", index=False)

print(f"\nremoved_rows_salary.shape\n{removed_rows_salary.shape}")
print("\nSaved: player_salary_removed and player_salary_cleaned")
