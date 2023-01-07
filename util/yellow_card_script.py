# USE API TO GET THE YELLOW CARDS FOR EACH TEAM IN EACH MATCH SO FAR IN THE CHAMPIONSHIP
import json
import math
import os
import time

import requests
import pandas as pd
from scipy.stats import binom
# Find the range of binominal values at the 5% significance level
from util.p_value_tools import bin_from_agg

active_championship_id = 4365



key = input("Enter API key: ")
host = input("Enter API host: ")
headers = {
    "X-RapidAPI-Key": key,
    "X-RapidAPI-Host": host
}

# Read from fixtures.json
# Path from content root: fixtures.json
# input if refresh fixs
refresh_fixs = input('Refresh fixtures? (y/n): ')
if refresh_fixs == 'y':
    # Get the fixtures from the API
    fixtures = requests.get(
        'https://api-football-v1.p.rapidapi.com/v2/fixtures/league/{}'.format(active_championship_id),
        headers=headers).json()
    # Save the fixtures to fixtures.json
    with open('fixtures.json', 'w') as f:
        json.dump(fixtures, f)
else:
    if os.path.exists('fixtures.json'):
        # read json
        with open('fixtures.json', 'r') as f:
            fixtures = json.load(f)
    else:
        print('No fixtures.json file found. Please refresh fixtures.')
        exit()

# Show keys in the dictionary
fixtures.keys()

# Split into results and fixtures
res = fixtures['api']['results']
fix = fixtures['api']['fixtures']

# Get the results ids
res_ids = [r['fixture_id'] for r in fix]

# Split fix whether status is Match Finished or not
finished_fix = [f for f in fix if f['statusShort'] == 'FT']
unfinished_fix = [f for f in fix if f['statusShort'] != 'FT']

# Get the finished fixtures ids
finished_fix_ids = [f['fixture_id'] for f in finished_fix]
# Get the team ids in the finished fixtures
finished_fix_teams = [{'home': f['homeTeam'], 'away': f['awayTeam']} for f in finished_fix]

# if championship stats csv exists, load it
# Path from content root: championship_stats.csv
if os.path.exists('championship_stats.csv'):
    df_stats = pd.read_csv('championship_stats.csv')
    # set finished as bool
    df_stats['finished'] = df_stats['finished'].astype(bool)

else:
    df_stats = pd.DataFrame()
    # Add fixture_id and team_id columns
    # Create fixtures from finished_fix
    fixtures_list = [{'fixture_id': f['fixture_id'], 'home': f['homeTeam'], 'away': f['awayTeam']} for f in fix]
    # Create two records for each fixture, one for home team and one for away team
    fixtures_list = [{'fixture_id': f['fixture_id'], 'team_id': f['home']['team_id']} for f in fixtures_list] + [
        {'fixture_id': f['fixture_id'], 'team_id': f['away']['team_id']} for f in fixtures_list]
    # Create a dataframe from the fixtures
    df_stats = pd.DataFrame(fixtures_list)
    # Add column for if game has occured
    # Do this by checking if id in finished_fix_ids
    df_stats['finished'] = df_stats['fixture_id'].apply(lambda x: x in finished_fix_ids)

# Set a multi index of fixture and team
df_stats.set_index(['fixture_id', 'team_id'], inplace=True)
# ask to set max_count
max_count = int(input('Requests remaining: '))
counter = 0
# Repeat above for all the finished fixtures
for i in finished_fix_ids:
    # Check if the fixture has already been added to the df_stats
    if counter >= max_count:
        break
    if i not in df_stats.index.get_level_values('fixture_id') or df_stats.loc[i]['Passes %'].isnull().all():
        counter += 1
        # # Get the statistics for the fixture
        stats = requests.get(
            "https://api-football-v1.p.rapidapi.com/v2/statistics/fixture/{fixture_id}".format(fixture_id=i),
            headers=headers).json()
        # Convert stats to df of statistics
        df_stats_temp = pd.DataFrame(stats['api']['statistics'])
        # Index of df_stats is home and away
        # Add team id to df_stats where finished_fix_teams[0][index]['team_id'] is the id for home and away
        # for each index in df
        # replace the index with the team id

        for col in df_stats_temp.columns:
            # Convert None to 0
            # Change NoneTypes to '0'
            df_stats_temp[col] = df_stats_temp[col].apply(lambda x: '0' if not x else x)
            if col not in df_stats.columns:
                df_stats[col] = None
            if (col == 'Ball Possession' or col == 'Passes %') and not isinstance(df_stats_temp[col][0], float):
                # Convert to float in temp
                # Strip %
                df_stats_temp[col] = df_stats_temp[col].apply(lambda x: float(x.strip('%')))
            else:
                # Convert to int in temp
                df_stats_temp[col] = df_stats_temp[col].apply(lambda x: int(x))

        # Add the fixture id to the df_stats
        df_stats_temp['fixture_id'] = i
        for index, row in df_stats_temp.iterrows():
            # Get the team id
            team_str = index + 'Team'
            # team id wher finished_fix[fixture_id=i][team_str]['team_id']
            team_id = finished_fix[finished_fix_ids.index(i)][team_str]['team_id']
            # At fixture i team_id, replace the values for the row
            # Add cols if not in df_stats
            # Convert None in row to 0
            # Set
            # Add team_id to df_stas_temp

            row['team_id'] = int(team_id)
            # Set index as team_id
            row['finished'] = True
            df_stats.loc[(i, team_id)] = row

        # Pause for 2 seconds
        print('Finished fixture: {}'.format(i))
        time.sleep(2)

# Save the df_stats to championship_stats.csv
df_stats.to_csv('championship_stats.csv')

team_dict = {}
# Get the ids and names into dict
# format of finished_fix_teams is {0: {'home': {'team_id': 33, 'team_name': 'Brentford'}, 'away': {'team_id': 34, 'team_name': 'Bristol City'}}}
# Get the team names from the team ids
for i in finished_fix_teams:
    for j in i.values():
        team_dict[j['team_id']] = j['team_name']

# Convert from strings
# If percentage, divide by 100
# Replace nan with 0
df_stats = df_stats.fillna(0)
for col in df_stats.columns:
    # If not bool
    if col == 'finished':
        continue
    if col == 'Ball Possession' or col == 'Passes %':
        # If not float, convert to float
        df_stats[col] = df_stats[col].str.replace('%', '').astype(float) / 100
    else:
        df_stats[col] = df_stats[col].astype(float)
# repeat with var called df_new_stats

# Convert finished to bool
df_stats['finished'] = df_stats['finished'].astype(bool)

# Get cards from finished and offsides is not nan
df_cards = df_stats[df_stats['finished'] & df_stats['Passes %'].notnull()][['Red Cards', 'Yellow Cards']]
# Drop games where a fixture does not have two records
for i in df_cards.index.get_level_values('fixture_id').unique():
    if len(df_cards.loc[i]) != 2:
        df_cards.drop(i, inplace=True)

# Sort by fixture_id
df_cards.sort_index(inplace=True)

# Get the count of cards
df_cards['total'] = df_cards['Red Cards'] + df_cards['Yellow Cards']

# Get the count of games where both teams had x+ cards for x in range(1, 5)
for i in range(1, 5):
    # if both teams in fixture had i-0.5 cards
    df_cards['over' + str(i)] = df_cards['total'] >= i - 0.5
    counts = df_cards.groupby('fixture_id')['over' + str(i)]
    # .transform(lambda x: x.all())
    # Get games where both values are true
    df_cards['over' + str(i) + '_both'] = counts.transform(lambda x: x.all())

    print('Games where both teams had ' + str(i) + ' or more cards: ' + str(
        df_cards['over' + str(i) + '_both'].sum() / 2))

    # Get the distinct fixture counts in counts

    # Run bin_from_agg
    wins = len(df_cards[df_cards['over' + str(i) + '_both']]) / 2
    total = len(df_cards) / 2

    p_range = bin_from_agg(wins, total, 0.05)
    odds_range = [1 / p for p in p_range]
    # Sort odds range
    odds_range.sort()
    print('Odds range: ' + str(odds_range))
    inv_odds = [1 / (1 - p) for p in p_range]
    inv_odds.sort()
    print('Inverse odds range: ' + str(inv_odds))

# Create a column incards for the team with the most cards in a foxtire
df_cards['most'] = df_cards.groupby('fixture_id')['total'].transform(lambda x: x.max())
# df_cards['most'] = True if most = total but false if both equal max
df_cards['most'] = df_cards['most'] == df_cards['total']
# Set as false if both teams have the same number of cards
df_cards['most'] = df_cards['most'] & df_cards.groupby('fixture_id')['total'].transform(lambda x: x.nunique() > 1)

# Create a df that aggregates the sums of each colymn for each team
# Add a column that tracks the number of games
df_agg = df_cards.groupby('team_id').sum()
df_agg['games'] = df_cards.groupby('team_id').count()['total']
# Add a column that maps team name
df_agg['team_name'] = df_agg.index.map(team_dict)

# For each col with over, run bin_from_agg with val and games col at 0.01% sig for each row
for col in df_agg.columns:
    if 'over' in col and 'odds' not in col:
        # print the values in this col
        df_agg[col + '_odds'] = df_agg.apply(lambda x: sorted(
            [round(1 / y, 4) if y != 0 else 10000 for y in bin_from_agg(int(x[col]), int(x['games']), 0.001)]), axis=1)

pause = True
# Sort a list called lst
