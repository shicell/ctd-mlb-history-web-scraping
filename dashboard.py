""" A Dashboard with Dash """
import sqlite3
import math
import numpy as np
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

# connect to database base_running
try:
    with sqlite3.connect("db/base_running.db") as conn:

        # SQL statement to retrieve from database and read into a dataframe
        sql_statement = """
                        SELECT l.year
                        , l.league
                        , l.team
                        , l.bases_stolen
                        , s.salary
                        FROM yoy_leader as l
                        LEFT JOIN player_salary as s on l.player_id = s.player_id
                                  and l.year = s.year
                        """

        # load gapminder dataset
        leader_df = pd.read_sql_query(sql_statement, conn)
        print(leader_df.head(5))

        # SQL statement to retrieve from database and read into a dataframe
        sql_statement = """
                        SELECT l.year
                        , l.league
                        , l.team
                        , l.bases_stolen AS base_number
                        , 'Bases Stolen' AS base_stat_category
                        FROM yoy_leader as l 
                        UNION ALL 
                        SELECT l.year 
                        , l.league
                        , l.team
                        , t.caught_stealing AS base_number
                        , 'Caught Stealing' AS base_stat_category
                        FROM yoy_leader as l 
                        LEFT JOIN player_yearly_stats as t on l.player_id = t.player_id 
                                  and l.year = t.year
                        """

        # load gapminder dataset
        base_stats_df = pd.read_sql_query(sql_statement, conn)
        print(base_stats_df.head(5))

        # create series of unique values for year, team, league
        leagues = leader_df["league"].unique()
        teams = leader_df["team"].unique()
        teams = np.sort(teams)

        # for the year range slider, decades will be marked
        decades = pd.to_numeric((leader_df["year"] / 10), downcast='integer') * 10
        decades_dict = dict(zip(decades, decades.astype(str)))

        # Initialize Dash app
        app = Dash(__name__)
        server = app.server

        # Create slider for years
        app.layout = html.Div([
            html.H3("Multiple Filters"),

            html.Div([
                html.Label("Year Range:"),
                dcc.RangeSlider(
                    id="year-slider",
                    min=min(leader_df["year"]),
                    max=max(leader_df["year"]),
                    step=1,
                    marks=decades_dict,
                    value=[1900, 2025],
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ]),
            html.Hr(),

            #create dropdown for leagues
            html.Div([
                html.Label("League(s):"),
                dcc.Dropdown(
                    id="league-dropdown",
                    options=[{"label": league, "value": league} for league in leagues],
                    multi=True,
                    value=leagues,
                    placeholder="Select one or more leagues"
                )
            ]),
            html.Hr(),
            
            #create dropdown for teams
            html.Div([
                html.Label("Team(s):"),
                dcc.Dropdown(
                    id="team-dropdown",
                    options=[{"label": team, "value": team} for team in teams],
                    multi=True,
                    value=teams,
                    placeholder="Select one or more teams"
                )
            ]),

            html.Hr(),
            html.Div([html.Label("Graphs:"),
                dcc.Graph(id='graphs-1'),
                dcc.Graph(id='graphs-2'), 
                dcc.Graph(id='graphs-3')])
        ])

        # Callback for stolen bases over time line graph
        @app.callback(
            Output("graphs-1", "figure"),
            [Input("year-slider", "value"),
             Input("league-dropdown", "value")]
        )

        # Create graph for stolen bases over time line graph
        def update_sb_over_time_graph(years_value, leagues_value):
            line_df = leader_df[(leader_df["league"].isin(leagues_value))
                                & (leader_df["year"] >= years_value[0])
                                & (leader_df["year"] <= years_value[1])
                                ]
            fig = px.line(line_df,
                          x="year",
                          y="bases_stolen",
                          labels={"year": "Year", "bases_stolen": "Number of Bases Stolen"},
                          title=f"Most Stolen Bases By Year ({years_value[0]}-{years_value[1]}) ")
            return fig
        
        # Callback for stolen bases vs bases caught stealing over time stacked bar graph
        @app.callback(
            Output("graphs-2", "figure"),
            [Input("year-slider", "value"),
             Input("league-dropdown", "value"),
             Input("team-dropdown", "value")]
        )

        # produce graph for stolen bases vs bases caught stealing over time stacked bar graph
        def update_sb_cs_stacked_bar_by_team_graph(years_value, leagues_value, teams_value):
            # Determine dataframe based on filters
            bar_df = base_stats_df[(base_stats_df["league"].isin(list(leagues_value)))
                                    & (base_stats_df["team"].isin(list(teams_value)))
                                    & (base_stats_df["year"] >= years_value[0])
                                    & (base_stats_df["year"] <= years_value[1])
                                   ]

            # Need to sort by Bases Stolen
            # get teams based on bases stolen
            bases_stolen_df = bar_df[bar_df["base_stat_category"] == "Bases Stolen"]

            # get total sum of all base stolen by team
            bases_stolen_sum = bases_stolen_df.groupby(["team"])["base_number"].sum()
            bases_stolen_sum_df = bases_stolen_sum.reset_index()

            # sort aggregated total bases stolen by team
            bases_stolen_sum_df = bases_stolen_sum_df.sort_values(by="base_number", ascending=False)

            # get top 10 teams
            top_10_sorted_team = list(bases_stolen_sum_df["team"].head(10))

            # Refine original dataframe so it only includes the top 10 teams
            bar_df = bar_df[(bar_df["team"].isin(top_10_sorted_team))]
            bar_agg = bar_df.groupby(["team", "base_stat_category"])["base_number"].sum()
            bar_agg_df = bar_agg.reset_index()


            fig = px.bar(bar_agg_df,
                          x="team",
                          y="base_number",
                          labels={"team": "Team Name", "base_number": "Number of Bases"},
                          color="base_stat_category",
                          barmode="stack",
                          title=f"Top 10 Teams by Total Bases Stolen Between ({years_value[0]}-{years_value[1]})")
            fig.update_layout(xaxis={'categoryorder': 'array',
                                     'categoryarray': top_10_sorted_team})
            fig.update_layout(legend_title_text="<b>Base Statistic Category</b>")
            return fig
        
        # Callback for salary historgram
        @app.callback(
            Output("graphs-3", "figure"),
            [Input("year-slider", "value"),
             Input("league-dropdown", "value"),
             Input("team-dropdown", "value")]
        )

        # Create graph for salary historgram
        def update_salary_histogram(years_value, leagues_value, teams_value):
            histogram_df = leader_df[(leader_df["league"].isin(leagues_value))
                                    & (leader_df["team"].isin(teams_value))
                                    & (leader_df["year"] >= years_value[0])
                                    & (leader_df["year"] <= years_value[1])
                                   ]
            bins = round(math.sqrt(histogram_df["salary"].count())) * 2
            fig = px.histogram(histogram_df,
                          x="salary",
                          log_y=True,
                          labels={"salary": "Player Salary($)"},
                          nbins=max(1, bins),
                          color="league",
                          title=f"Distribution of Player Salary Who Stole the Most Bases ({years_value[0]}-{years_value[1]})")
            fig.update_layout(legend_title_text="<b>Baseball League</b>")
            return fig

        # Run the app
        if __name__ == "__main__":
            app.run(debug=True)


except Exception as e:
    print(f"Database could not be created: {e}")
