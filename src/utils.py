import pandas as pd
import numpy as np

import requests
import urllib3


def collect_strava_data(nr_activities=200):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    payload = {
        'client_id': "112087",
        'client_secret': '734911cf5c35b38944e53de86bc7102a959a827a',
        'refresh_token': 'e7455dac5580f04a6b284a8c9441cd0de7865fa9',
        'grant_type': "refresh_token",
        'f': 'json'
    }

    print("Requesting Token...\n")
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']
    print("Access Token = {}\n".format(access_token))

    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': nr_activities, 'page': 1}

    my_dataset = requests.get(activites_url,
                              headers=header,
                              params=param).json()

    return my_dataset


def preprocess_runs(data):
    all_activities = pd.DataFrame(data)
    all_activities.distance = np.round(all_activities.distance/1000, 2)
    all_activities.average_speed = 16.66666/all_activities.average_speed
    all_activities.moving_time = all_activities.moving_time/3600
    all_activities.elapsed_time = all_activities.elapsed_time/3600
    all_activities.start_date = pd.to_datetime(all_activities.start_date)
    all_activities['year_week'] = all_activities.start_date.apply(
        lambda x: str(x.isocalendar()[0]) + '_' + str(x.isocalendar()[1])
        )

    runs = all_activities[all_activities.type == "Run"].reset_index(drop=True)
    return runs


def add_weeks_without_runs(runs):
    runs = runs.sort_values(by='start_date', ascending=False)

    # Get start and end dates
    all_year_weeks = list(runs.year_week.drop_duplicates())
    startdate = all_year_weeks[-1]
    enddate = all_year_weeks[0]

    start_year, start_week = map(int, startdate.split('_'))
    end_year, end_week = map(int, enddate.split('_'))

    # Create a list of all year-week combinations
    all_year_weeks = ['{}_{}'.format(year, week) for year in range(start_year, end_year + 1) for week in range(1, 53)]

    # Create a DataFrame from this list
    df_all = pd.DataFrame(all_year_weeks, columns=['year_week'])

    # Merge with the original DataFrame
    runs_complete = pd.merge(df_all, runs, on='year_week', how='left')
    runs_complete[['year', 'week']] = runs_complete['year_week'].str.split(
        '_', expand=True
        )
    runs_complete['year'] = runs_complete['year'].astype(int)
    runs_complete['week'] = runs_complete['week'].astype(int)

    runs_filtered = runs_complete.query(
        "(year > @start_year or week >= @start_week) and (year < @end_year or week <= @end_week)"
        ).reset_index(drop=True)

    return runs_filtered