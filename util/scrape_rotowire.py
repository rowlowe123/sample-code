import ast
import datetime
import glob
import os
import re
import time

import requests
import json
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
import html5lib
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
import math

from mat_models import Match, MatStatistic
from models import Player, Team
from scraper_models import Scraper

nba_team_names = [
    '76ers',
    'Bucks',
    'Bulls',
    'Cavaliers',
    'Celtics',
    'Clippers',
    'Grizzlies',
    'Heat',
    'Hawks',
    'Hornets',
    'Jazz',
    'Kings',
    'Knicks',
    'Lakers',
    'Magic',
    'Mavericks',
    'Nets',
    'Nuggets',
    'Pacers',
    'Pelicans',
    'Pistons',
    'Raptors',
    'Rockets',
    'Spurs',
    'Suns',
    'Thunder',
    'Timberwolves',
    'Warriors',
    'Wizards',
    'Trail Blazers',
]




class RotowireScraper(Scraper):

    def __init__(self, team_name=None, headers=None, cookies=None):
        super(RotowireScraper, self).__init__(name='Rotowire Odds Scraper', url='https://www.rotowire.com/betting/nba/player-props.php', id=455)
        self.team_name = team_name
        self.headers = headers
        self.cookies = cookies


# def get_lines():
#     page = requests.get('https://www.rotowire.com/betting/nba/player-props.php', cookies=cookies, headers=headers)
#
#     # Parse the page
#     soup = BeautifulSoup(page.content, 'html.parser')
#
#     # Find all div in soup that contain 'props' in the id
#     divs = soup.find_all('div', id=lambda x: x and 'props' in x)
#     print (divs)


def parse_body(body):
    # Split the body into left, centre and right columns
    left = body.find('div', class_='webix_ss_left')
    centre = body.find('div', class_='webix_ss_center')
    right = body.find('div', class_='webix_ss_right')

    # Find all role='gridcell' in left
    left_cells = left.find_all('div', role='gridcell')

    # Get all class='odds-table-entity-link' from left
    left_links = left.find_all('a', class_='odds-table-entity-link')

    # First name = left_links[2].text
    # Last name = left_links[3].text

    names = [col.contents[2].text + col.contents[3].text for col in left_links]
    # Strip /xa0 from names
    names = [name.replace('\xa0', '') for name in names]

    # Get all columns from centre where class is webix_column
    centre_cols = centre.find_all('div', class_='webix_column')

    # Get the value of each child of each column
    centre_cols = [[child.text for child in col.children] for col in centre_cols]

    # Create df from centre_cols
    df = pd.DataFrame(centre_cols).T

    # Name first column 'Team', second column 'Opponent', third is Fanduel_line, fourth is Fanduel_over, fifth is Fanduel_under
    # Repeat line, over under for DraftKings, BetMGM and PointsBet
    df.columns = ['Team', 'Opponent', 'Fanduel_line', 'Fanduel_over', 'Fanduel_under', 'DraftKings_line',
                  'DraftKings_over', 'DraftKings_under', 'BetMGM_line', 'BetMGM_over', 'BetMGM_under', 'PointsBet_line',
                  'PointsBet_over', 'PointsBet_under']

    # Add names column
    df['Name'] = names

    # Pivot columns such that any column with 'line', 'over' or 'under' in the name is pivoted
    # They are pivoted such that the first half of the column name is the bookmaker name in new column
    # This means there are now 4 columns for each name team and opponent
    # These are 'Bookmaker', 'Line', 'Over' and 'Under'
    df = df.melt(id_vars=['Name', 'Team', 'Opponent'], var_name='Bookmaker', value_name='Value')

    # Split the bookmaker column into bookmaker and line/over/under
    df[['Bookmaker', 'Line/Over/Under']] = df['Bookmaker'].str.split('_', expand=True)

    # Pivot the table such that each value in the Line/Over/Under column is a column
    df = df.pivot_table(index=['Name', 'Team', 'Opponent', 'Bookmaker'], columns='Line/Over/Under', values='Value',
                        aggfunc='first').reset_index()

    df = df.reset_index()

    # Remove any rows where a value is missing
    df = df.dropna()

    # Remove rows where line is missing
    df = df[df['line'] != '-']

    # Return df
    return df

    # # Consolidate columns such that each bookmaker set of line over under is in one row
    # df = df.melt(id_vars=['Name', 'Team', 'Opponent'], var_name='Bookmaker', value_name='Value')
    #
    # # Split Bookmaker into Bookmaker and Line/Over/Under
    # df[['Bookmaker', 'Line/Over/Under']] = df['Bookmaker'].str.split('_', expand=True)
    #
    # # Remove rows where Line/Over/Under is empty
    # df = df[df['Line/Over/Under'] != '']
    #
    # # Remove rows where Value is empty
    # df = df[df['Value'] != '']
    #
    # # Merge rows where Name Opponent and Bookmaker are the same, so that each player has one row per bookmaker but 3 columns
    # # for line over and under
    #
    # df = df.groupby(['Name', 'Opponent', 'Bookmaker']).agg({'Value': ', '.join}).reset_index()

    # Drop line/over/under column
    df = df.drop('Line/Over/Under', axis=1)

    # Drop rows where line is empty
    df = df[df['Line'].notna()]

    # Drop rows where over is empty
    df = df[df['Over'].notna()]

    # Drop rows where under is empty
    df = df[df['Under'].notna()]

    # Drop rows where value is empty
    df = df[df['Value'].notna()]


def get_lines():
    # Use Selenium to get the page
    # Use cookies and headers from requests

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()
    driver.get('https://www.rotowire.com/betting/nba/player-props.php')
    # Immediately load the page
    preload_soup = BeautifulSoup(driver.page_source, 'html.parser')
    preload_tables = preload_soup.find_all('div', class_='prop-table')
    # Get const settings from script in each table
    for table in preload_tables:
        script = table.find('script')
        # Get the const settings from the script
        const_settings = script.text.split('const settings = ')[1].split('const')[0].strip()
# Comvert from javascript const json to python

# Get data from [ onwareds

        # Get data from [
        data = const_settings.split('[', 1)[1]
        # Get data to ]
        data = data.split(']', 1)[0]
        # Split data into rows
        data = data.split('},')
        # Remove last row
        data = data[:-1]
        # Add } to end of each row except last one

        data = [row + '}' for row in data[:-1]]

        # Convert to json
        data = [json.loads(row) for row in data]

        # Create df from data
        df = pd.DataFrame(data)
        # Drop logo, playerLink
        df = df.drop(['logo', 'playerLink'], axis=1)

        # Pivot df on rows with _, with first half before _ as value in 'Type' col and second half as new column where value is value
        id_vars = [col for col in df.columns if '_' not in col]
        val_vars = [col for col in df.columns if '_' in col]
        # get the unique values in the val_vars sep by _
        name_vars = [col.split('_')[0] for col in val_vars]
        name_vars = list(set(name_vars))

        # create new df with id_VARS, name in name_vars and value in val_vars where name

        # Create new columns for each name_var, with line Under and Over
        for name_var in name_vars:
            new_row = {'Book': name_var}
            #
            for val_var in val_vars:
                if val_var.split('_')[0] == name_var:
                    # if Over in name
                    if 'Over' in val_var:
                        new_row['Over'] = df[val_var].iloc[0]
                    # if Under in name
                    elif 'Under' in val_var:
                        new_row['Under'] = df[val_var].iloc[0]
                    else:
                        new_row['Line'] = df[val_var].iloc[0]
            # Add new row to df
            df = df.append(new_row, ignore_index=True)
        # Drop the old columns
        df = df.drop(val_vars, axis=1)

        df = df.melt(id_vars=id_vars, var_name='Type', value_name='Value')

        # Data now looks like this:
        # {"gameID":"2484438","playerID":"3445","firstName":"Steven","lastName":"Adams","name":"Steven Adams","team":"MEM","opp":"@TOR","logo":"https:\/\/content.rotowire.com\/images\/teamlogo\/basketball\/100MEM.png?v=3","playerLink":"\/betting\/nba\/player\/steven-adams-odds-3445","draftkings_reb":"9.5","draftkings_rebUnder":"110","draftkings_rebOver":"-140","fanduel_reb":"10.5","fanduel_rebUnder":"-142","fanduel_rebOver":"116","mgm_reb":"9.5","mgm_rebUnder":"105","mgm_rebOver":"-139","pointsbet_reb":"10.5","pointsbet_rebUnder":"-135","pointsbet_rebOver":"105"}
        # Convert the above string to dict


        # Replace all ' with "
        data = data.replace("'", '"')
        # Strip all whitespace

        json_data = ast.literal_eval(json.dumps(data))




        # Cast to json
        jjson = json.loads(const_settings)

        const_settings = json.loads(json.dumps(const_settings))
        #b Expecting property name in double qutoes


    # Go max screen
    driver.maximize_window()

    # Disable opening new tabs
    driver.execute_script("window.open = function() {};")

    # Wait for the page to load
    time.sleep(5)

    # # Get all tables on page where id contains 'props' as a substring
    # tables = BeautifulSoup.find_all('div', id=lambda x: x and 'props' in x)
    # table_soup = []
    #
    # # for each table, get all rows and columns
    # for table in tables:
    #     # Click on the table so it can be scrolled down
    #     table.click()
    #     # Append table contents to a list
    #     table_soup.append(table)
    #
    #     # while table is not at the bottom
    #     while table.location['y'] + table.size['height'] < driver.execute_script('return document.body.scrollHeight'):
    #         # Scroll down
    #         driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    #         # Wait for page to load
    #         time.sleep(0.2)

    # # while bottom of table is not visible
    # # scroll to bottom of table
    # # wait for table to fully load
    #     while True:
    #         # Get all records table where id contains 'props' as substring
    #         table = driver.find_element_by_xpath("//div[contains(@id, 'props')]")
    #
    #         # Get the bottom of the table
    #         bottom = table.find_element_by_class_name('bottom')
    #
    #         # If the bottom of the table is not visible, scroll to it
    #         if not bottom.is_displayed():
    #             driver.execute_script("arguments[0].scrollIntoView();", bottom)
    #             time.sleep(0.5)
    #         else:
    #             break

    page = driver.page_source

    # Parse the page
    soup = BeautifulSoup(page, 'html.parser')

    # Find all div in soup that contain 'props' in the id and class is prop-table
    tables = soup.find_all('div', class_='prop-table')

    # Each table has a


    divs = soup.find_all('div', id=lambda x: x and 'props' in x)

    tables_dict = {}

    # Load table from each instance in divs from the nested 'Webix' in class
    for div in divs[:3]:

        # Get full id of div
        table_type = div['id']

        # Scroll down the page and load page source
        # Repeat until the table is loaded and visible
        isViewable = False
        while not isViewable:
            # Scroll down
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            # Wait for page to load
            time.sleep(0.2)
            # Get bs4 object of table
            table = BeautifulSoup(driver.page_source, 'html.parser').find('div', id=table_type)
            # Check if table has rows
            if table.find('div', class_='row'):
                # Check if table is visible
                if table.find('div', class_='row').is_displayed():
                    isViewable = True


        # # while cannot find element
        # try:
        #     # Find the web element of div not using find_element_by_id
        div_element = driver.find_element(By.XPATH, f"//div[@id='{table_type}']")
        #     break
        # except:
        #     # Skip this table
        #     continue
        #     # Scroll down the page 300 px
        #     driver.execute_script("window.scrollBy(0, 50);")
        #     # Wait for table to load
        #     time.sleep(1.5)
        #     pass

        # Scroll to the div
        driver.execute_script("arguments[0].scrollIntoView();", div_element)

        # Click on the div so it can be scrolled down
        div_element.click()

        # Get div where class contains 'webix_dtable'
        table = div.find('div', class_=lambda x: x and 'webix_dtable' in x)
        if not table:
            continue

        # Get num of rows from aria-rowcount in nested
        num_rows = int(table['aria-rowcount'])
        # Get num of columns from aria-colcount
        num_cols = int(table['aria-colcount'])

        df_table = pd.DataFrame()
        row_num = 1
        while row_num < num_rows:

            # Navigate web element to the rows inside column 1
            # Find in we_element where column='1'
            col_element = div_element.find_element(By.XPATH, f".//div[@column='1']")
            # Find in row_element where row='{row_num}'
            try :
                row_element = col_element.find_element(By.XPATH, f".//div[@row='{row_num}']")

                driver.execute_script("arguments[0].click();", row_element)

                # Get the row element

                # Press down 25 times

                # create action chain object
                action = ActionChains(driver)
                # send one down arrow key press
                action.send_keys(Keys.DOWN * 25)
                # perform the operation
                action.perform()
                # stop pressing down

                time.sleep(2)
                row_num += 25

            except:
                # Page is not scrole    d down enough
                # Scroll down the page 300 px
                driver.execute_script("window.scrollBy(0, 50);")
                # Wait for table to load
                time.sleep(1.5)
                pass
            # javasript clikc

            # Get the page source
            page = driver.page_source
            # Parse the page
            soup = BeautifulSoup(page, 'html.parser')
            # Get the soup of div_element
            div_soup = soup.find('div', id=table_type)

            # Find the div where role='grid'
            table = div_soup.find('div', role='grid')
            # Get the body of the table where class = 'webix_ss_body'
            body = table.find('div', class_='webix_ss_body')

            new_records = parse_body(body)

            if df_table.empty:
                df_table = new_records
            else:
                # Append new records to df_table, but only if name of new record does not exists in table
                df_table = df_table.append(new_records[~new_records['Name'].isin(df_table['Name'])])
            # Repeat with new set of rows
            # print vals at new col
            print(df_table)
        # Add midpoints from removevig
        df_table = add_midpoints(df_table)
        tables_dict[table_type] = df_table
    # Export to csv
    for table_type, df_table in tables_dict.items():
        df_table.to_csv(f'{table_type}.csv', index=False)

    print(divs)


def add_midpoints(df):
    """
    Calculates the predicted midpoint of lines with an over, under, and line
    Returns the df with a set of new rows: over_pred, under_pred and mid_pred
    :param df:
    :return:
    """
    # Create new df that takes over and under and line by seraching columns.toUpper()
    df_cols = df[[col for col in df.columns if col.upper() in ['OVER', 'UNDER', 'LINE']]]
    # Upper df_cols columns
    df_cols.columns = df_cols.columns.str.upper()
    # Make sure all columns are numeric
    df_cols = df_cols.apply(pd.to_numeric, errors='coerce')

    # Convert american odds to decimal odds for over and under
    df_cols['OVER'] = df_cols['OVER'].apply(lambda x: (100 / -x) + 1 if x < 0 else x / 100 + 1)
    df_cols['UNDER'] = df_cols['UNDER'].apply(lambda x: (100 / -x) + 1 if x < 0 else x / 100 + 1)
    # Prediction is formed by doing reverse poisson using over and under lines as odds
    # So for line 15.5 and over +100, predicted mid is poisson mean where x>=16 is 50%
    # and x<16 is 50%
    # Use reverse poisson to find value

    # # Mid prediction is used by find the sum of over and under and scaling them so them add to one
    # line_sum = 1/over + 1/under
    # over_pred = 1/over / line_sum
    # under_pred = 1/under / line_sum

    # Add vig column to df
    df_cols['VIG'] = 1 / df_cols['OVER'] + 1 / df_cols['UNDER']

    # ROUND LINE UP
    df_cols['LINE'] = df_cols['LINE'].apply(lambda x: math.ceil(x))

    # Use get_mean for over, under, and no-vig lines to find the predicted midpoint
    df_cols['OVER_PRED'] = df_cols.apply(lambda x: inv_poisson(x['LINE'], 1 / x['OVER']), axis=1)
    df_cols['UNDER_PRED'] = df_cols.apply(lambda x: inv_poisson(x['LINE'], 1 - 1 / x['UNDER']), axis=1)
    df_cols['MID_PRED'] = df_cols.apply(lambda x: inv_poisson(x['LINE'], 1 / (x['OVER'] / x['VIG'])), axis=1)
    # Add preds to df
    df = df.join(df_cols[['OVER_PRED', 'UNDER_PRED', 'MID_PRED']])
    return df


def inv_poisson(val, p):
    # poisson formula is e^(-mean) * mean^x / x!
    # so x = ln(p * mean^x / e^(-mean)) / mean
    # x = ln(p * mean^x / e^(-mean)) / mean
    # x = ln(p * mean^x) - ln(e^(-mean)) / mean
    # x = ln(p * mean^x) - (-mean) / mean
    # x = ln(p * mean^x) + mean / mean
    # x = ln(p * mean^x) / mean + 1
    # x-1 = ln(p * mean^x) / mean
    # (x-1) * mean = ln(p * mean^x)
    # e^((x-1) * mean) = p * mean^x
    # e^((x-1) * mean) / mean^x = p

    # Use numerical method to brute force solution for inverse poisson
    # Start at val-2 and run poisson until it is greater than p
    # Then return val-2

    # Start at val-2
    x = val - 2

    from scipy.stats import poisson
    while 1 - poisson.cdf(k=val - 1, mu=x) < p:
        x += 0.01
    return x


def rotowire_csv_to_db():
    """
    Imports csv files from rotowire into a sqlite database
    :return:
    """
    from init_db import session
    # Get list of csv files in currnt dir
    csv_files = [file for file in os.listdir() if file.endswith('.csv')]

    # Read statmap csv from project root

    df_statmap = pd.read_csv('stat_map.csv')

    df_all = pd.DataFrame()

    # Create table for each csv file except statmap
    for csv_file in csv_files:
        # Check file contains 'props' in name
        if 'props' in csv_file:
            # Read csv file
            df = pd.read_csv(csv_file)
            # Get table name
            table_name = csv_file.replace('.csv', '')
            # Srtips 'Props-' from table name
            table_name = table_name.replace('props-', '')

            # Upper case table name
            table_name = table_name.upper()
            # Find the statistic_id from name in statmap
            statistic_id = df_statmap[df_statmap['name'] == table_name]['statistic_id'].values[0]
            df['statistic_id'] = statistic_id
            # Add to df_all
            df_all = pd.concat([df_all, df])

    # Check if games in df_all have already passed

    # Remove line, over and under cols from df_all
    df_all = df_all[[col for col in df_all.columns if col.upper() not in ['LINE', 'OVER', 'UNDER']]]

    # Lowecase all columns
    df_all.columns = df_all.columns.str.lower()

    # Get the player_id from the player_name in Player table using session
    df_all['player_id'] = df_all['name'].apply(lambda x: session.query(Player.id).filter(Player.name == x).first())

    # Get players where player_id is None
    df_new_players = df_all[df_all['player_id'].isnull()]
    # Add new players to Player table
    for player in df_new_players['name'].unique():
        session.add(Player(full_name=player, name=player, is_active=True))
    # Commit changes
    session.commit()
    # Get the player_id from the player_name in Player table using session only for players that were just added
    df_new_players['player_id'] = df_new_players['name'].apply(
        lambda x: session.query(Player.id).filter(Player.name == x).first())
    # Concat df_new_players to df_all
    df_all = pd.concat([df_all, df_new_players])

    # Drop player_name column
    df_all = df_all.drop('name', axis=1)
    # Change team and oppenent to home and away team where if opponent has '@' then team is away and opponent is home
    # If the opponent contains '@' then the team is away and the opponent is home
    df_all['home'] = df_all.apply(lambda x: x['team'] if '@' not in x['opponent'] else x['opponent'], axis=1)
    df_all['away'] = df_all.apply(lambda x: x['opponent'] if '@' not in x['opponent'] else x['team'], axis=1)
    # Strip '@' from home and away
    df_all['home'] = df_all['home'].apply(lambda x: x.replace('@', ''))
    df_all['away'] = df_all['away'].apply(lambda x: x.replace('@', ''))
    # Drop team and opponent
    df_all = df_all.drop(['team', 'opponent'], axis=1)
    # Get the team names from Team where home, away are team.abbreviated_name
    df_all['home'] = df_all['home'].apply(
        lambda x: session.query(Team.short_name).filter(Team.abbreviated_name == x).all())
    df_all['away'] = df_all['away'].apply(
        lambda x: session.query(Team.short_name).filter(Team.abbreviated_name == x).all())

    # Strip all non letters, numbers or spaces from home and away
    df_all['home'] = df_all['home'].apply(lambda x: re.sub('[^A-Za-z0-9 ]+', '', str(x)))
    df_all['away'] = df_all['away'].apply(lambda x: re.sub('[^A-Za-z0-9 ]+', '', str(x)))
    # Use nba_team_names to find correct values for home and away
    # Change series to list
    # Check if any value in nba_teams_list is substring in home or away
    # If so then replace home or away with that value
    df_all['home'] = df_all['home'].apply(lambda x: [team for team in nba_team_names if team in x][0])
    df_all['away'] = df_all['away'].apply(lambda x: [team for team in nba_team_names if team in x][0])

    # Create match name from home and away in format away + '@' + home
    df_all['match_name'] = df_all['away'] + ' @ ' + df_all['home']
    # Drop home and away
    df_all = df_all.drop(['home', 'away'], axis=1)

    # Get the match_id, date and time from the match_name in Match table using session and datetime of match has not passed
    # Get the match id, date and time where mattch.name is match_name and match.date is greater than now
    # Do all in one query
    df_all['match_info'] = df_all['match_name'].apply(lambda x: session.query(Match.id, Match.date, Match.time).filter(
        Match.name == x, Match.date >= datetime.datetime.now()).first())

    # Remove records where match_info is None
    df_all = df_all[df_all['match_info'].notnull()]
    df_all['match_id'] = df_all['match_info'].apply(lambda x: x[0])
    df_all['date'] = df_all['match_info'].apply(lambda x: x[1])
    df_all['time'] = df_all['match_info'].apply(lambda x: x[2])

    # Check if match_id exists for every record
    # If not then add match to Match table
    if df_all['match_id'].isnull().any():
        pause = True

    # Check if all matches started at least 4 hours ago
    # Convert to datetime
    df_all['datetime'] = df_all['date'].astype(str) + ' ' + df_all['time'].astype(str)
    # Convert to datetime
    df_all['datetime'] = df_all['datetime'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    # Get current datetime
    earliest_valid_datetime = datetime.datetime.now() - datetime.timedelta(hours=4)
    # Remove all games that started before earliest_valid_datetime
    df_all = df_all[df_all['datetime'] > earliest_valid_datetime]

    # Drop datetime, date and time
    df_all = df_all.drop(['datetime', 'date', 'time'], axis=1)

    # Check if items still exist after removing old matches
    if df_all.shape[0] == 0:
        print('No matches in csv')
        # ask if want new lines
        # if yes run get lines again
        # if no exit

    # Remove matches where id is None, this is broken becuase searching by abbreviation brings up nfl teams
    # Solve this by joining teams to leagueroster table to find the teams only in that league
    df_all = df_all[df_all['match_id'].notnull()]
    df_new_matches = df_all[df_all['match_id'].isnull()]
    # Add new matches to Match table
    for match in df_new_matches['match_name'].unique():
        # Add match to Match table
        session.add(Match(name=match, date=datetime.datetime.now()))
    # Drop match_name
    df_all = df_all.drop('match_name', axis=1)
    # Convert bookamaker to id from name, with 'Fanduel' as 3000, 'Draftkings' as 4000, 'Pointsbet' as 5000
    df_all['bookmaker_id'] = df_all['bookmaker'].apply(
        lambda x: 3000 if x == 'Fanduel' else 4000 if x == 'Draftkings' else 5000)
    # Drop bookmaker
    df_all = df_all.drop('bookmaker', axis=1)

    # Melt columns with 'pred' in name
    df_all = pd.melt(df_all, id_vars=['player_id', 'match_id', 'statistic_id', 'bookmaker_id'],
                     value_vars=[col for col in df_all.columns if 'pred' in col])

    # Create source id from bookmaker id + 1 for under in varialbe column, bookmaker id + 2 for over in variable column, and bookmaker id + 3 for mid in variable
    df_all['source_id'] = df_all.apply(
        lambda x: x['bookmaker_id'] + 1 if 'under' in x['variable'] else x['bookmaker_id'] + 2 if 'over' in x[
            'variable'] else x['bookmaker_id'] + 3, axis=1)
    # Drop variable
    df_all = df_all.drop('variable', axis=1)
    # Convert player_id, match_id, statistic_id, bookmaker_id, source_id to int
    # if player_id is series then convert [0] to int
    # if player_id is int then convert to int
    if not isinstance(df_all['player_id'][0], int):
        df_all['player_id'] = df_all['player_id'].apply(lambda x: int(x[0]))
    # df_all['player_id'] = df_all['player_id'].apply(lambda x: int(x[0]) if type(x) == pd.Series else int(x))
    # df_all['player_id'] = df_all['player_id'].apply(lambda x: int(x[0]))
    # Add name by combining player match statistic source ids sep by _
    df_all['name'] = df_all['player_id'].astype(str) + '_' + df_all['match_id'].astype(str) + '_' + df_all[
        'statistic_id'].astype(str) + '_' + df_all['source_id'].astype(str)

    # Remove duplicates
    df_all = df_all.drop_duplicates(subset=['name'])

    # TEMPORARY
    # drop all records where source id doesn't end in 2
    df_all = df_all[df_all['source_id'].apply(lambda x: str(x)[-1] == '2')]

    from init_db import add_records
    # Split df_all into chunks of 1000
    chunks = [df_all[i:i + 1000] for i in range(0, df_all.shape[0], 1000)]
    # Add each chunk to the database
    for chunk in chunks:
        add_records(chunk, MatStatistic, None, 0)

    return df_all

    # Clear all stored from session


if __name__ == "__main__":
    # get_lines()
    rotowire_csv_to_db()
