import pandas as pd

from database_constants import seasons, datafilepath

#Combines data from multiple seasons into one dataframe
def combine_data(data):
    combined=pd.DataFrame()
    for season in seasons:
        df=pd.read_csv(rf"{datafilepath}/{data}_{season}")
        df.drop(df.columns[0],1,inplace=True)
        df["Season"]=season
        cols=list(df.columns)
        cols=cols[0:1]+[cols[-1]]+[cols[-2]]+[cols[-3]]+cols[1:-3]
        df=df[cols]
        #cols=[x[x.index("_0")+2:]if "_0" in x  else x for x in cols]
        df.columns=cols
        combined=pd.concat([combined,df])
    return combined

#Creates a dataframe of historical fixtures in the format: short team name vs short opponent name

def create_fixtures():
    # Import form data
    form_df = pd.read_csv(f"{datafilepath}/PL Form Historical", index_col=False)
    # Import historical results data
    results = pd.read_csv(f"{datafilepath}/PL Results Historical", index_col=False)
    # Map long version of team names to short version
    long_team_names = list(form_df["Team"].unique())
    long_team_names.sort()
    short_team_names = ['ARS', 'AVL', 'BLA', 'BOL', 'BOU', "BHA", 'BUR',
                        'CAR', 'CHE', 'CRY', 'EVE', 'FUL', 'HUD', 'HUL', 'LEE', 'LEI', 'LIV', 'MCI', 'MUN', 'MID',
                        'NEW', 'NOR', 'QPR', 'RDG', 'SHU', 'SOU', 'STK', 'SUN', 'SWA', 'TOT', 'WAT', 'WBA', 'WHU',
                        'WIG', 'WOL']
    dict_team = {i: j for i, j in zip(long_team_names, short_team_names)}
    reverse_dict_team = {j: i for i, j in zip(long_team_names, short_team_names)}
    form_df["Short Team Name"] = [dict_team[x] for x in form_df["Team"]]
    results["Short Home"] = [dict_team[x] for x in results["Home"]]
    results["Short Away"] = [dict_team[x] for x in results["Away"]]

    # Create an Opponents DF- for each gameweek have team 1 vs team 2 and team 2 vs team 1
    opponents1 = results.copy()
    opponents1 = opponents1[["Season", "Gameweek ID", "Short Home", "Short Away"]]
    opponents1 = opponents1.rename(columns={"Short Home": "Short Team Name", "Short Away": "Opponent"})
    opponents2 = results.copy()
    opponents2 = opponents2[["Season", "Gameweek ID", "Short Home", "Short Away"]]
    opponents2 = opponents2.rename(columns={"Short Home": "Opponent", "Short Away": "Short Team Name"})

    opponents = opponents1.append(opponents2)
    opponents = opponents.rename(columns={"Gameweek ID": "GW ID"})
    opponents.sort_values(["Season", "GW ID"])

    return opponents


def create_opponents_form_df():
    # Import historical form data
    form_df = pd.read_csv(f"{datafilepath}/PL Form Historical", index_col=False)
    long_team_names = list(form_df["Team"].unique())
    long_team_names.sort()
    short_team_names = ['ARS', 'AVL', 'BLA', 'BOL', 'BOU', "BHA", 'BUR',
                        'CAR', 'CHE', 'CRY', 'EVE', 'FUL', 'HUD', 'HUL', 'LEE', 'LEI', 'LIV', 'MCI', 'MUN', 'MID',
                        'NEW', 'NOR', 'QPR', 'RDG', 'SHU', 'SOU', 'STK', 'SUN', 'SWA', 'TOT', 'WAT', 'WBA', 'WHU',
                        'WIG', 'WOL']
    dict_team = {i: j for i, j in zip(long_team_names, short_team_names)}
    form_df["Short Team Name"] = [dict_team[x] for x in form_df["Team"]]

    opponents=create_fixtures()

    form_df_opponents = pd.merge(form_df, opponents[["Season", "GW ID", "Short Team Name", "Opponent"]], how='inner',
                                 left_on=["Season", "GW ID", "Short Team Name"],
                                 right_on=["Season", "GW ID", "Short Team Name"])
    form_df_opponents = pd.merge(form_df_opponents, form_df, how='inner',
                                 left_on=["Season", "GW ID", "Opponent"],
                                 right_on=["Season", "GW ID", "Short Team Name"])
    a = [x.replace("_y", "_Opponent") for x in list(form_df_opponents.columns)]
    a = [x.replace("_x", "") for x in a]
    form_df_opponents.columns = a

    return form_df_opponents


def create_opponents_form_df():
    # Import historical form data
    form_df = pd.read_csv(f"{datafilepath}/PL Form Historical", index_col=False)
    long_team_names = list(form_df["Team"].unique())
    long_team_names.sort()

    short_team_names = ['ARS', 'AVL', 'BLA', 'BOL', 'BOU', "BHA", 'BUR',
                        'CAR', 'CHE', 'CRY', 'EVE', 'FUL', 'HUD', 'HUL', 'LEE', 'LEI', 'LIV', 'MCI', 'MUN', 'MID',
                        'NEW', 'NOR', 'QPR', 'RDG', 'SHU', 'SOU', 'STK', 'SUN', 'SWA', 'TOT', 'WAT', 'WBA', 'WHU',
                        'WIG', 'WOL']
    dict_team = {i: j for i, j in zip(long_team_names, short_team_names)}
    form_df["Short Team Name"] = [dict_team[x] for x in form_df["Team"]]

    opponents=create_fixtures()

    form_df_opponents = pd.merge(form_df, opponents[["Season", "GW ID", "Short Team Name", "Opponent"]], how='inner',
                                 left_on=["Season", "GW ID", "Short Team Name"],
                                 right_on=["Season", "GW ID", "Short Team Name"])
    form_df_opponents = pd.merge(form_df_opponents, form_df, how='inner',
                                 left_on=["Season", "GW ID", "Opponent"],
                                 right_on=["Season", "GW ID", "Short Team Name"])
    a = [x.replace("_y", "_Opponent") for x in list(form_df_opponents.columns)]
    a = [x.replace("_x", "") for x in a]
    form_df_opponents.columns = a

    return form_df_opponents


# So far only focused on getting data on the team played for, but need have data on the opponent's defence/attack

def add_oppoenents_data():
    data = ["defending", "goalthreat"]
    teams_defending = pd.DataFrame()
    teams_attacking = pd.DataFrame()
    for season in seasons:
        team_defending = pd.read_csv(rf"{datafilepath}/team_{season}_defending")
        team_attacking = pd.read_csv(rf"{datafilepath}/team_{season}_goalthreat")
        print(season, len(team_defending), len(team_attacking))

        for form in data:
            if form == "defending":
                if team_defending.empty:
                    teams_defending = team_defending
                else:
                    teams_defending = teams_defending.append(team_defending)
            elif form == "goalthreat":
                if teams_attacking.empty:
                    teams_attacking = team_attacking
                else:
                    teams_attacking = teams_attacking.append(team_attacking)
            else:
                continue

    teams_defending.reset_index(inplace=True)
    teams_attacking.reset_index(inplace=True)
    team_stats = pd.merge(teams_attacking, teams_defending, how="inner", on=["Season", "GW ID", "Team"])
    a = [x.replace("_x", "") for x in team_stats.columns]
    team_stats.columns = a
    team_stats = team_stats[['Season', 'GW ID', 'Team', 'Games Played', 'GoalsTotal', 'AttemptsTotal', 'AttemptsIn',
                             'AttemptsBCT', 'AttemptsSP', 'AttemptsBlkd', 'AttemptsHit WW',
                             'AttemptsMins Per Chance', 'AttemptsOn Target', 'Conversion %Shots',
                             'Conversion %Goals',
                             'Goals Conceded', 'Clean Sheets', 'Shots ConcededIn',
                             'Shots ConcededOut', 'Shots ConcededTotal', 'Shots ConcededOn Target',
                             'Shots ConcededHead', 'Shots ConcededSP', 'Shots ConcededBC',
                             'Crosses ConcededLeft Flank', 'Crosses ConcededRight Flank',
                             'Chances ConcededLeft Flank', 'Chances ConcededCentre',
                             'Chances ConcededRight Flank', 'Defensive SlipsLost',
                             'Defensive SlipsErr', 'Defensive SlipsErr Goal']]

    team_stats = team_stats.groupby(["Season", "Team", "GW ID"]).mean().reset_index()
    team_stats[['MA Team GoalsTotal', 'MA Team AttemptsTotal', 'MA Team AttemptsIn',
                'MA Team AttemptsBCT', 'MA Team AttemptsSP', 'MA Team AttemptsBlkd', 'MA Team AttemptsHit WW',
                'MA Team AttemptsMins Per Chance', 'MA Team AttemptsOn Target', 'MA Team Conversion %Shots',
                'MA Team Conversion %Goals',
                'MA Team Goals Conceded', 'MA Team Clean Sheets', 'MA Team Shots ConcededIn',
                'MA Team Shots ConcededOut', 'MA Team Shots ConcededTotal', 'MA Team Shots ConcededOn Target',
                'MA Team Shots ConcededHead', 'MA Team Shots ConcededSP', 'MA Team Shots ConcededBC',
                'MA Team Crosses ConcededLeft Flank', 'MA Team Crosses ConcededRight Flank',
                'MA Team Chances ConcededLeft Flank', 'MA Team Chances ConcededCentre',
                'MA Team Chances ConcededRight Flank', 'MA Team Defensive SlipsLost',
                'MA Team Defensive SlipsErr', 'MA Team Defensive SlipsErr Goal']] = team_stats[
        team_stats.columns[4:]].rolling(3).mean().shift()
    opponent_stats = team_stats.copy()
    opponent_stats.columns = [str(x).replace("Team", "Opponent") for x in opponent_stats.columns]

    return team_stats, opponent_stats


def attempts_create(df):
    if df["Season"] == 2020:
        return df["Attempts 20"]
    if df["Season"] < 2020:
        return df["Goals Attempts pre20 or Goals 20"]


def goals_create(df):
    if df["Season"] == 2020:
        return df["Goals Attempts pre20 or Goals 20"]
    if df["Season"] < 2020:
        return df["Goals pre 20"]


def final_thirdpasses(df):
    if df["Season"] == 2020:
        return df['Final Third Successful Passes 20']
    if df["Season"] < 2020:
        return df['Final Third Successful Passes pre 20, Opp Half SP 20']


def opponenthalf_passes(df):
    if df["Season"] == 2020:
        return df['Final Third Successful Passes pre 20, Opp Half SP 20']
    if df["Season"] < 2020:
        return df["Opponents Half Successful Passes pre 20"]

    def attempts_create(df):
        if df["Season"] == 2020:
            return df["Attempts 20"]
        if df["Season"] < 2020:
            return df["Goals Attempts pre20 or Goals 20"]

    def goals_create(df):
        if df["Season"] == 2020:
            return df["Goals Attempts pre20 or Goals 20"]
        if df["Season"] < 2020:
            return df["Goals pre 20"]

    def final_thirdpasses(df):
        if df["Season"] == 2020:
            return df['Final Third Successful Passes 20']
        if df["Season"] < 2020:
            return df['Final Third Successful Passes pre 20, Opp Half SP 20']

    def opponenthalf_passes(df):
        if df["Season"] == 2020:
            return df['Final Third Successful Passes pre 20, Opp Half SP 20']
        if df["Season"] < 2020:
            return df["Opponents Half Successful Passes pre 20"]

def calculate_fpl_points(position,goals,assists,cleansheets):
    points=0
    if position=="Defender":
        points+=(cleansheets*0)+(goals*5)+(assists*3)
    if position=="Midfielder":
        points+=(cleansheets*0)+(goals*5)+(assists*3)
    if position=="Forward":
        points+=(cleansheets*0)+(goals*4)+(assists*3)
    return points

