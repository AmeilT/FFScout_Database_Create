
# tables refers to the separate dataframes containing data on separate aspects of the game: Defending, Attacking, Goal Threat, Distribution etc.
from database_constants import tables
from database_functions import *

# Import all the tables and combine all the seasons for the particular table
df = pd.DataFrame()
add_df = pd.DataFrame()
for table in tables:
    if df.empty:
        df = combine_data(data=table)
        print(f"Added {table}")
    else:
        add_df = combine_data(data=table)
        cols_to_use = list(add_df.columns[:].difference(df.columns))
        cols_to_use.insert(0, "Name")
        cols_to_use.insert(1, "Season")
        cols_to_use.insert(2, "Gameweek")
        df = pd.merge(left=df, right=add_df[cols_to_use], how="outer", on=["Season", "Gameweek", "Name"])
        print(f"Added {table}")

# For each season and each GW within a season map the home and away teams- do this using the short name
opponents = create_fixtures()

# Import the separately created form data for each team for each GW in a season
form_df_opponents = create_opponents_form_df()

# Import team level stats
team_stats, opponent_stats = add_opponents_data()

# Merge the main df with form data on the opponents they are playing
df = pd.merge(df, form_df_opponents[
    ["Season", "GW ID", "Short Team Name", "Form Measure EWM", "Last N games", "Form Measure EWM_Opponent",
     "Last N games_Opponent", "Opponent"]], how='inner',
              left_on=["Season", "Gameweek", "Team"],
              right_on=["Season", "GW ID", "Short Team Name"])

# Then merge with opponents stats. This give us a players stats and opponents stats in one df /
# for a specific GW in a given season
df = pd.merge(df, opponent_stats[['Season', 'GW ID', 'Opponent',
                                  'MA Opponent GoalsTotal',
                                  'MA Opponent AttemptsTotal', 'MA Opponent AttemptsIn', 'MA Opponent AttemptsBCT',
                                  'MA Opponent AttemptsSP', 'MA Opponent AttemptsBlkd',
                                  'MA Opponent AttemptsHit WW', 'MA Opponent AttemptsMins Per Chance',
                                  'MA Opponent AttemptsOn Target', 'MA Opponent Conversion %Shots',
                                  'MA Opponent Conversion %Goals', 'MA Opponent Goals Conceded',
                                  'MA Opponent Clean Sheets', 'MA Opponent Shots ConcededIn',
                                  'MA Opponent Shots ConcededOut', 'MA Opponent Shots ConcededTotal',
                                  'MA Opponent Shots ConcededOn Target', 'MA Opponent Shots ConcededHead',
                                  'MA Opponent Shots ConcededSP', 'MA Opponent Shots ConcededBC',
                                  'MA Opponent Crosses ConcededLeft Flank',
                                  'MA Opponent Crosses ConcededRight Flank',
                                  'MA Opponent Chances ConcededLeft Flank',
                                  'MA Opponent Chances ConcededCentre',
                                  'MA Opponent Chances ConcededRight Flank', 'MA Opponent Defensive SlipsLost',
                                  'MA Opponent Defensive SlipsErr', 'MA Opponent Defensive SlipsErr Goal']],
              how="inner", left_on=["Season", "Gameweek", "Opponent"], right_on=["Season", "GW ID", "Opponent"])

# Same as above but bringing in own team stats
df = pd.merge(df, team_stats[['Season', 'GW ID', 'Team',
                              'MA Team GoalsTotal',
                              'MA Team AttemptsTotal', 'MA Team AttemptsIn', 'MA Team AttemptsBCT',
                              'MA Team AttemptsSP', 'MA Team AttemptsBlkd',
                              'MA Team AttemptsHit WW', 'MA Team AttemptsMins Per Chance',
                              'MA Team AttemptsOn Target', 'MA Team Conversion %Shots',
                              'MA Team Conversion %Goals', 'MA Team Goals Conceded',
                              'MA Team Clean Sheets', 'MA Team Shots ConcededIn',
                              'MA Team Shots ConcededOut', 'MA Team Shots ConcededTotal',
                              'MA Team Shots ConcededOn Target', 'MA Team Shots ConcededHead',
                              'MA Team Shots ConcededSP', 'MA Team Shots ConcededBC',
                              'MA Team Crosses ConcededLeft Flank',
                              'MA Team Crosses ConcededRight Flank',
                              'MA Team Chances ConcededLeft Flank',
                              'MA Team Chances ConcededCentre',
                              'MA Team Chances ConcededRight Flank', 'MA Team Defensive SlipsLost',
                              'MA Team Defensive SlipsErr', 'MA Team Defensive SlipsErr Goal']], how="inner",
              left_on=["Season", "Gameweek", "Team"], right_on=["Season", "GW ID", "Team"])

# Combining on same names however _y fields represent opponents and _x the player's own team
a = [x.replace("_y", "_Opponent") for x in list(df.columns)]
a = [x.replace("_x", "") for x in a]
df.columns = a

# Cleaning column names either to make them more understandable or to remap a column that is named differently to an old column that represents the same level of data. #
# For example in 2020 FFScout change Goal Attempts In box to mean Goals scored in error and this needs to be corrected
# new_column_names = dict.fromkeys(list(df.columns) , 1)
# new_column_names={i:i for i in new_column_names.keys()}
new_column_names = {'Name': 'Name',
                    'Season': 'Season',
                    'Gameweek': 'GW ID1',
                    'Position': 'Position',
                    'Short Team Name': 'Team',
                    'Unnamed: 3_level_0App': 'Apps',
                    'Unnamed: 4_level_0Mins': 'Mins1',
                    'Unnamed: 5_level_0Tot': 'DELETE1',
                    'TouchesOpp Half': 'TouchesOpp Half',
                    'TouchesFin 3rd': 'TouchesFin 3rd',
                    'TouchesMins/ Tch': 'TouchesMins/ Tch',
                    'TouchesTot': 'Touches Total for 20, Total Passes Received pre 20',
                    'Passes ReceivedOpp Half': 'Passes ReceivedOpp Half',
                    'Passes ReceivedFin 3rd': 'Passes ReceivedFin 3rd',
                    'Passes ReceivedMins/ Pass Rec': 'Passes ReceivedMins/ Pass Rec',
                    'Passes ReceivedTot': 'Passes Received 20, Take ons Pre 20',
                    'Take OnsSucc': 'Take OnsSucc',
                    'Take Ons%': 'Take Ons%',
                    'Take OnsTkld': 'Take OnsTkld',
                    'Take OnsGI': 'Goal Involvement pre 20',
                    'GoalsFGI': "FPL Goal Inv",
                    'GoalsUnnamed: 19_level_1': "DELETE2",
                    'Cost': 'Cost',
                    'Apps': 'Apps',
                    'Mins': 'Mins2',
                    'Take OnsTot': 'Take Ons 20',
                    'GoalsGI': 'Goal Involvements 20',
                    'Assist PotentialA': 'Assists',
                    'Assist PotentialBCC': 'Big Chances Created',
                    'Assist PotentialCC': 'Chances Created 20',
                    'Assist PotentialFA': 'Fantasy Assists',
                    'Assist PotentialM/ CC': 'Assist PotentialM/ CC',
                    'Assist PotentialTA': 'Total Assists',
                    'Assist PotentialUnnamed: 21_level_1': 'DELETE3',
                    'Crossing%': 'Cross Completion',
                    'CrossingCC': 'Chances Created2 pre 20',
                    'CrossingCr': 'Crosses 20',
                    'CrossingSP': 'Successful Crosses',
                    'Final Third%': 'Pass Completion Final Third 20',
                    'Final ThirdCr': 'Crosses Pre 20',
                    'Final ThirdSP': 'Final Third Successful Passes 20',
                    'Opponents Half%': 'Pass Completion Opponents Half',
                    'Opponents HalfSP': 'Final Third Successful Passes pre 20, Opp Half SP 20',
                    'Total Passes%': 'Pass Completion',
                    'Total PassesSP': 'Total Successfull Passes',
                    'Total PassesSP.1': 'Opponents Half Successful Passes pre 20',
                    'Total PassesTotal': 'Total Passes 20',
                    'Unnamed: 5_level_0Total': 'Total Passes pre 20',
                    'AttemptsBCT': 'Attempts from Big Chances',
                    'AttemptsH': 'Attempts Headed',
                    'AttemptsIn': 'Attempts In Box',
                    'AttemptsM/C': 'AttemptsM/C',
                    'AttemptsOn': 'Attempts On Target',
                    'AttemptsShots': 'Shot Accuracy pre 20',
                    'AttemptsTot': 'Attempts 20',
                    'ConversionGoals': 'Conversion Goals',
                    'ConversionShots': 'Shot Accuracy 20',
                    'ConversionUnnamed: 20_level_1': 'DELETE5',
                    'GoalsBCS': 'Big Chances Scored',
                    'GoalsH': 'Headed Goals',
                    'GoalsIn': 'Goals In the Box',
                    'GoalsM/G': 'GoalsM/G',
                    'GoalsOut': 'Goals Out of the Box',
                    'GoalsTot': 'Goals Attempts pre20 or Goals 20',
                    'Unnamed: 5_level_0Pen Tchs': 'Penalty Touches 20',
                    'Unnamed: 6_level_0Pen Tchs': 'Penalty Touches Pre 20',
                    'Unnamed: 6_level_0Tot': 'Goals pre 20',
                    'Aerial Duels%': '% Aerial Duels Won',
                    'Aerial DuelsTot': 'Aerial Duels Total',
                    'Aerial DuelsWon': 'Aerial Duels Won',
                    'ErrorsELC': 'Delete5',
                    'ErrorsELG': 'Delete6',
                    'ErrorsUnnamed: 20_level_1': 'Delete7',
                    'FantasyCS': 'Fantasy Clean Sheet 20',
                    'FantasyGC': 'Fantasy Goals Conceded',
                    'FantasyTot': 'Aerial Duels pre20',
                    'Loose BallBlks': 'Loose BallBlks',
                    'Loose BallCBI': 'Loose BallCBI',
                    'Loose BallClr': 'Loose BallClr',
                    'Loose BallELC': 'Loose BallELC',
                    'Loose BallInt': 'Interceptions 20',
                    'Loose BallRec': 'Loose BallRec',
                    'Tackles%': 'Tackle Success %',
                    'TacklesInt': 'Interceptions pre 20',
                    'TacklesTot': 'Tackles 20 ',
                    'TacklesWon': 'Tackles Won',
                    'Unnamed: 5_level_0CS': 'Fantasy Clean Sheet Pre 20',
                    'Assist PotentialCnrs Succ': 'Successful Corners',
                    'Assist PotentialCnrs Taken': 'Corners Taken 20',
                    'Assist PotentialUnnamed: 11_level_1': 'DELETE10',
                    'Set Piece GoalsAtt': 'Attempts from Set Pieces pre 20',
                    'Set Piece GoalsPen': 'Goals from Penalties 20',
                    'Set Piece GoalsTotal': 'Goals from Set Pieces',
                    'Set Piece ThreatAtt': 'Attempts from Set Pieces 20',
                    'Set Piece ThreatCnrs Taken': 'Corners Taken pre 20',
                    'Set Piece ThreatHead': 'Headed Attempts from Set Pieces',
                    'Unnamed: 5_level_0Pen': 'Goals from Penalties pre 20',
                    'Minutes PerChance': 'Minutes PerChance 20',
                    'Minutes PerChance Created': 'Minutes PerChance Created',
                    'Minutes PerCross': 'Minutes PerCross',
                    'Minutes PerGoal': 'Minutes PerGoal',
                    'Minutes PerGoal Attempt In Box': 'Minutes PerGoal Attempt In Box',
                    'Minutes PerPass Received': 'Minutes PerPass Received',
                    'Minutes PerShot On Target': 'Minutes PerShot On Target',
                    'Minutes PerSucc Pass - Final Third': 'Minutes PerSucc Pass - Final Third',
                    'Minutes PerTouch - Pen Box': 'Minutes PerTouch - Pen Box',
                    'Minutes PerUnnamed: 14_level_1': "DELETE11",
                    'Minutes PerUnnamed: 15_level_1': "DELETE12",
                    'Unnamed: 3_level_0Starts': "Starts pre 20",
                    'Unnamed: 4_level_0Starts': 'Starts 20',
                    'Unnamed: 5_level_0Chance': "Minutes PerChance pre 20",
                    'Minutes PerBlock': 'Minutes PerBlock',
                    'Minutes PerClearance': 'Minutes PerClearance',
                    'Minutes PerInterception': 'Minutes PerInterception',
                    'Minutes PerRecovery': 'Minutes PerRecovery',
                    'Minutes PerTackle': 'Minutes PerTackle',
                    'Minutes PerTackle Won': 'Minutes PerTackle Won',
                    'Minutes PerUnnamed: 11_level_1': 'Minutes PerUnnamed: 11_level_1',
                    'Unnamed: 5_level_0Block': "DELETE13",
                    'GW ID': 'GW ID2',
                    'Short Team Name': 'Short Team Name',
                    'Form Measure': 'Form Measure',
                    'Last N games': 'Last N games',
                    'Form Measure_Opponent': 'Form Measure_Opponent',
                    'Last N games_Opponent': 'Last N games_Opponent',
                    'Opponent': 'Opponent'}
df.rename(mapper=new_column_names, inplace=True, axis=1)
df = df.loc[:, ~df.columns.duplicated()]

df["Goals from Penalties"] = df["Goals from Penalties pre 20"].fillna(0) + df["Goals from Penalties 20"].fillna(0)
df.drop(["Goals from Penalties pre 20", "Goals from Penalties 20"], inplace=True, axis=1)
df["Attempts from Set Pieces"] = df["Attempts from Set Pieces pre 20"].fillna(0) + df[
    "Attempts from Set Pieces 20"].fillna(0)
df.drop(["Attempts from Set Pieces pre 20", "Attempts from Set Pieces 20"], inplace=True, axis=1)
df["Passes Final Third"] = df.apply(final_thirdpasses, axis=1)
df["Passes Opponents Half"] = df.apply(opponenthalf_passes, axis=1)
df.drop(["Final Third Successful Passes pre 20, Opp Half SP 20",
         "Final Third Successful Passes 20", "Opponents Half Successful Passes pre 20"], inplace=True, axis=1)
df["Corners Taken"] = df["Corners Taken pre 20"].fillna(0) + df["Corners Taken 20"].fillna(0)
df.drop(["Corners Taken pre 20", "Corners Taken 20"], inplace=True, axis=1)
df["Starts"] = df["Starts pre 20"].fillna(0) + df["Starts 20"].fillna(0)
df.drop(["Starts pre 20", "Starts 20"], inplace=True, axis=1)
df["Minutes PerChance"] = df["Minutes PerChance pre 20"].fillna(0) + df["Minutes PerChance 20"].fillna(0)
df.drop(["Minutes PerChance pre 20", "Minutes PerChance 20"], inplace=True, axis=1)
df["Interceptions"] = df["Interceptions pre 20"].fillna(0) + df["Interceptions 20"].fillna(0)
df.drop(["Interceptions pre 20", "Interceptions 20"], inplace=True, axis=1)
df["Goal Attempts"] = df.apply(attempts_create, axis=1)
df["Goals"] = df.apply(goals_create, axis=1)
df.drop(["Attempts 20", "Goals Attempts pre20 or Goals 20", "Goals pre 20"], inplace=True, axis=1)
df["Chances Created"] = df["Chances Created 20"].fillna(0) + df["Chances Created2 pre 20"].fillna(0)
df.drop(["Chances Created 20", "Chances Created2 pre 20"], inplace=True, axis=1)
df["Crosses"] = df["Crosses 20"].fillna(0) + df["Crosses Pre 20"].fillna(0)
df.drop(["Crosses 20", "Crosses Pre 20"], inplace=True, axis=1)
df["Shot Accuracy"] = df["Shot Accuracy 20"].fillna(0) + df["Shot Accuracy pre 20"].fillna(0)
df.drop(["Shot Accuracy pre 20", "Shot Accuracy 20"], inplace=True, axis=1)
df["Penalty Touches"] = df["Penalty Touches 20"].fillna(0) + df["Penalty Touches Pre 20"].fillna(0)
df.drop(["Penalty Touches Pre 20", "Penalty Touches 20"], inplace=True, axis=1)
df["Fantasy Clean Sheet"] = df["Fantasy Clean Sheet Pre 20"].fillna(0) + df["Fantasy Clean Sheet 20"].fillna(0)
df.drop(["Fantasy Clean Sheet Pre 20", "Fantasy Clean Sheet 20"], inplace=True, axis=1)
df["Mins"] = df["Mins1"].fillna(0) + df["Mins2"].fillna(0)
df.drop(["Mins1", "Mins2"], inplace=True, axis=1)
df["GW ID"] = df["GW ID1"]
df.drop(["GW ID1", "GW ID2"], inplace=True, axis=1)
df["Total Passes"] = df["Total Passes pre 20"].fillna(0) + df["Total Passes 20"].fillna(0)
df.drop(["Total Passes 20", "Total Passes pre 20"], inplace=True, axis=1)
df["Goal Involvement"] = df["Goal Involvements 20"].fillna(0) + df["Goal Involvement pre 20"].fillna(0)
df.drop(["Goal Involvements 20", "Goal Involvement pre 20"], inplace=True, axis=1)
droplist = [x for x in list(df.columns) if "DELETE" in x.upper()]
df.drop(droplist, inplace=True, axis=1)

# New field to assign attacking points to each player.
df["Attacking FPL Points"] = list(
    map(calculate_fpl_points, df["Position"], df["Goals"], df["Total Assists"], df["Fantasy Clean Sheet"]))
droplist = [x for x in list(df.columns) if "20" in x.upper()]
df.drop(droplist, inplace=True, axis=1)

print(df.head)
