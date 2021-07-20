# import relevant modules

from selenium import webdriver
import time
import numpy as np
import pandas as pd
from selenium.webdriver.support.ui import Select

from scraper.scraper_constants import user_id, password, chromdriverpath, seasons
from scraper.scrape_functions import get_result, get_date, home_goals, away_goals, get_GW_ID, form_to_numbers, \
    number_to_measure, match_points

username = user_id
password = password

driver = webdriver.Chrome(chromdriverpath)
url = f"https://members.fantasyfootballscout.co.uk/matches/"
driver.get(url)
driver.find_element_by_id("user_login").send_keys(f"{username}")
driver.find_element_by_id("user_pass").send_keys(f"{password}")
time.sleep(2)
driver.find_element_by_name("login").click()

# Store in a results DF
results = pd.DataFrame()

for season in seasons:

    select = Select(driver.find_element_by_id('fsid'))
    select.select_by_value(str(season))
    driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div[2]/div/div/form/div/input[1]").click()

    for i in range(1, 39):
        try:
            table = f"//*[@id='content']/div/div[1]/div[2]/div/table[{i}]"
            tbl = driver.find_element_by_xpath(table).get_attribute('outerHTML')
            df_list = pd.read_html(tbl)
            gw = (f'//*[@id="content"]/div/div[1]/div[2]/div/h2[{i}]')
            gwtext = driver.find_element_by_xpath(gw).text.title()
            df_list[0]["Gameweek"] = gwtext
            df_list[0]["Season"] = season
            results = results.append(df_list[0])
        except:
            print(f"An exception occurred:{season},{i}")

results["Result"] = results["Score"].apply(get_result)
results["Date"] = results["Score"].apply(get_date)
results["Home Goals"] = results["Result"].apply(home_goals)
results["Away Goals"] = results["Result"].apply(away_goals)

conditions = [results["Home Goals"] > results["Away Goals"], results["Home Goals"] < results["Away Goals"],
              results["Home Goals"] == results["Away Goals"]]
choices = [results["Home"], results["Away"], 'Draw']

results["Outcome"] = np.select(conditions, choices)
results.drop("Score", inplace=True, axis=1)

results["Gameweek ID"] = [int(x.split()[1]) for x in results["Gameweek"]]
results = results.sort_values(["Season", "Gameweek ID"]).reset_index()

form_history = pd.DataFrame()

for season in seasons:
    results_season = results[results["Season"] == season]
    teams = list(results_season["Home"].unique())
    teams = teams * results_season["Gameweek ID"].max()

    # Make a list of Gameweek X * Number of team in the league (20)
    gameweek_numbers = []

    for i in np.arange(1, results_season["Gameweek ID"].max() + 1):
        gameweek_numbers.append(i)
    gameweek_numbers = gameweek_numbers * 20
    gameweek_numbers.sort()

    gameweek = []
    for i in gameweek_numbers:
        gameweek.append(f"Gameweek {i}")

    # create a form DF
    form_table = pd.DataFrame()
    form_table["Team"] = teams
    form_table["Gameweek"] = gameweek
    form_table["Season"] = season
    form_table["Form"] = ""
    form_table.sort_values("Gameweek", ascending=False)

    form_table["GW ID"] = form_table["Gameweek"].apply(get_GW_ID)
    form_table["Last N games"] = ""

    # Assign a W,L,D to the form table based on the results table
    for i in np.arange(0, len(results_season)):
        outcome = results_season["Outcome"].iloc[i]
        home_team = results_season["Home"].iloc[i]
        away_team = results_season["Away"].iloc[i]
        gameweek = results_season["Gameweek"].iloc[i]

        row = form_table[(form_table["Team"] == home_team) & (form_table["Gameweek"] == gameweek)].index[0]

        column = "Form"

        if outcome == home_team:
            form_table.at[row, column] = "W"

        elif outcome == "Draw":
            form_table.at[row, column] = "D"
        else:
            form_table.at[row, column] = "L"

        row = form_table[(form_table["Team"] == away_team) & (form_table["Gameweek"] == gameweek)].index[0]

        if outcome == away_team:
            form_table.at[row, column] = "W"

        elif outcome == "Draw":
            form_table.at[row, column] = "D"
        else:

            form_table.at[row, column] = "L"

    # Aggregate form over a 4 week period. The first 3 weeks will just use the longest trackrecord available
    for i in np.arange(0, form_table.shape[0]):
        form = form_table["Form"].iloc[i]
        gwid = form_table["GW ID"].iloc[i]
        team = form_table["Team"].iloc[i]
        GWID = list(form_table["GW ID"].unique())

        rows = form_table[(form_table["Team"] == team)].index

        column = "Last N games"

        if gwid == 1:

            form_table.at[rows[0], column] = ""

        elif gwid == 2:

            trackrecord = form_table.at[rows[gwid - 2], "Form"]
            form_table.at[rows[gwid - 1], column] = trackrecord


        elif gwid == 3:

            trackrecord = form_table.at[rows[gwid - 2], "Form"] + form_table.at[rows[gwid - 3], "Form"]
            form_table.at[rows[gwid - 1], column] = trackrecord

        else:

            trackrecord = form_table.at[rows[gwid - 2], "Form"] + form_table.at[rows[gwid - 2], column]

            if len(trackrecord) > 4:
                trackrecord = trackrecord[:4]

            form_table.at[rows[gwid - 1], column] = trackrecord

    form_table = form_table[form_table["Form"] != ""]

    form_history = form_history.append(form_table)

    form_history["numbers"] = form_history["Last N games"].apply(form_to_numbers)
    form_history["Form Measure"] = form_history["numbers"].apply(number_to_measure)
    form_history.drop(columns=['numbers'], inplace=True)

print("DONE!")

form_history["Points"] = form_history.apply(match_points, axis=1)
form_history = form_history.rename(columns={"Form Measure": "Form Measure User Defined"})
rolling_data = form_history.groupby(["Season", "Team", "GW ID"]).mean().reset_index()
rolling_data["Form Measure Rolling Points"] = rolling_data["Points"].rolling(4).mean()

df = pd.merge(rolling_data, form_history[["Season", "Team", "GW ID", "Last N games", "Form"]],
              left_on=["Season", "Team", "GW ID"], right_on=["Season", "Team", "GW ID"])

df["Form Measure EWM Points"]=rolling_data["Points"].ewm(min_periods=3,alpha=0.1).mean()

df_noshift = df.copy()

df["Form Measure EWM Points"] = df["Form Measure EWM Points"].shift()
df["Form Measure User Defined"] = df["Form Measure User Defined"].shift()
df["Form Measure Rolling Points"] =df["Form Measure Rolling Points"].shift()

df.to_csv("PL Form Historical", index=False)
df_noshift.to_csv("PL Form Historical_noshift", index=False)
results.to_csv("PL Results Historical", index=False)
