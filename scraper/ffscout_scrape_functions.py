from  selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
import numpy as np
import pandas as pd

from selenium.webdriver.support.ui import Select

from scraper_constants import *

def get_historicals_by_gw(season, gameweeklist, form):
    # Choose League URL
    driver = webdriver.Chrome(chromdriverpath)
    url = start_url
    driver.get(url)
    driver.find_element_by_id("user_login").send_keys(user_id)
    driver.find_element_by_id("user_pass").send_keys(password)
    time.sleep(2)
    driver.find_element_by_name("login").click()

    positions = ["defenders", "midfielders", "forwards"]
    df_dict = {"defenders": (), "midfielders": (), "forwards": ()}
    df = pd.DataFrame()

    for gw in gameweeklist:

        for position in positions:

            url = f"https://members.fantasyfootballscout.co.uk/player-stats/{position}/{form}/"
            driver.get(url)

            select = Select(driver.find_element_by_id('fsid'))
            select.select_by_value(season)

            # click team button
            team_button = driver.find_elements_by_xpath('//*[@id="ms-list-1"]/button')[0]
            team_button.click()

            # unselect top6 team button
            unselect6_team_button = driver.find_elements_by_xpath('//*[@id="ms-list-1"]/div/ul/li[1]/a')[0]
            unselect6_team_button.click()

            # select all team button
            select_all_team_button = driver.find_elements_by_xpath('//*[@id="ms-list-1"]/div/a')[0]
            select_all_team_button.click()

            # apply filter button
            select_all_team_button = \
            driver.find_elements_by_xpath('//*[@id="content"]/div/div[1]/div[2]/div/div[2]/form/div/input[1]')[0]
            select_all_team_button.click()

            select = Select(driver.find_element_by_id('frange'))
            select.select_by_value("GAMEWEEK_RANGE")

            select = Select(driver.find_element_by_id('fgameweek-start'))
            select.select_by_visible_text(str(gw))
            select = Select(driver.find_element_by_id('fgameweek-end'))
            select.select_by_visible_text(str(gw))

            driver.find_element_by_xpath("//*[@id='content']/div/div[1]/div[2]/div/div[2]/form/div/input[1]").click()

            tbl = driver.find_element_by_xpath("//*[@id='DataTables_Table_0']").get_attribute('outerHTML')
            df_list = pd.read_html(tbl)
            tablename = df_list[0]
            cols = list(map("".join, tablename.columns.values))
            tablename.columns = cols
            tablename.drop('Unnamed: 0_level_0Unnamed: 0_level_1', axis=1, inplace=True)
            tablename = tablename.rename(columns={'Unnamed: 1_level_0Name': 'Name',
                                                  'Unnamed: 2_level_0Team': 'Team',
                                                  'Unnamed: 3_level_0Cost': 'Cost',
                                                  'Unnamed: 4_level_0App': 'Apps',
                                                  'Unnamed: 5_level_0Mins': 'Mins'})
            tablename["Position"] = np.nan

            for x in list(np.arange(0, len(tablename["Name"]))):
                firstname = tablename["Name"].iloc[x].split()[1]
                secondname = tablename["Name"].iloc[x].split()[0]
                tablename["Position"].iloc[x] = f"{position.title()[:-1]}"
                if firstname == secondname:
                    tablename["Name"].iloc[x] = f"{firstname}"
                else:
                    tablename["Name"].iloc[x] = f"{firstname} {secondname}"

            df_dict[position] = tablename
            df_dict[position]["Gameweek"] = gw
            print(f"Gameweek:{gw} done")

        playerdf = pd.concat([df_dict["defenders"], df_dict["midfielders"], df_dict["forwards"]], axis=0,
                             ignore_index=True)
        df = df.append(playerdf)

    return df


