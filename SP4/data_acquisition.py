from pathlib import Path
import numpy as np
import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta


def load_historical_data(path_to_data: Path):
    historical_data = pd.read_csv(path_to_data)

    return historical_data


def get_actual_data(url):
    r = requests.get(url)

    if r.status_code == 200:  # url OK
        actual_data_str = str(r.content, 'utf-8')
        actual_data = pd.read_csv(StringIO(actual_data_str))

        print('Actual data downloaded successfully.')
        return actual_data

    else:
        print('ERROR: Actual data downloaded unsuccessfully.')
        return None


def get_historical_daily_statistics(historical_data):
    weekdays_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekdays_dictionary = { # {key = weekday, value = [num_occupied_spaces, num_free_spaces, num_weekday],...}
        'Monday': [0, 0, 0],
        'Tuesday': [0, 0, 0],
        'Wednesday': [0, 0, 0],
        'Thursday': [0, 0, 0],
        'Friday': [0, 0, 0],
        'Saturday': [0, 0, 0],
        'Sunday': [0, 0, 0],
    }
    data_array = historical_data.values

    for line in data_array:
        capacity = line[1]
        num_occupied_spaces = line[2] + line[3]
        num_free_spaces = line[5]
        timestamp = line[7]
        timestamp_list = timestamp.split(' ')

        date = timestamp_list[0]
        time = timestamp_list[1]

        weekday_idx = (pd.Timestamp(date)).day_of_week
        weekday_name = weekdays_list[weekday_idx]

        value = weekdays_dictionary[weekday_name]
        value[0] += num_occupied_spaces
        value[1] += num_free_spaces
        value[2] += 1

    res = count_average(weekdays_dictionary)

    return res


def get_historical_time_daily_statistics(historical_data):
    data_list = []
    weekdays_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data_array = historical_data.values
    for line in data_array:
        capacity = line[1]
        num_occupied_spaces = line[2] + line[3]
        num_free_spaces = line[5]
        timestamp = line[7]
        timestamp_list = timestamp.split(' ')

        date = timestamp_list[0]
        weekday_idx = (pd.Timestamp(date)).day_of_week
        weekday_name = weekdays_list[weekday_idx]

        time = timestamp_list[1]
        dt = datetime.strptime(time, '%H:%M:%S')
        rounded_time_full_hour = hour_rounder(dt)

        temp_data = [weekday_name, rounded_time_full_hour, num_occupied_spaces, num_free_spaces]
        data_list.append(temp_data)

    sorted_list = sorted(data_list, key=lambda x: (x[0], x[1]))
    get_time_daily_data(sorted_list)
    print()


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    timestamp = t.replace(second=0, microsecond=0, minute=0, hour=t.hour)+timedelta(hours=t.minute//30)
    rounded_time = str(timestamp).split(' ')[1]

    return rounded_time


def get_time_daily_data(data: list):
    res = np.zeros((24,7,3)) # matrix 24x7
    weekday_to_idx = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6,
    }

    for data_temp in data:
        weekday = data_temp[0]
        weekday_idx = weekday_to_idx[weekday]
        time = data_temp[1]
        num_occupied_spaces = data_temp[2]
        num_free_spaces = data_temp[3]



    pass

def count_average(weekdays: dict):
    res = {}
    for weekday in weekdays:
        value = weekdays[weekday]
        avg_occupied_spaces = round(value[0] / value[2])
        avg_free_spaces = round(value[1] / value[2])

        res.update({weekday: [avg_occupied_spaces, avg_free_spaces]})

    return res



historical_data = load_historical_data(Path('./data/data-pd-novedivadlo.csv'))
actual_data = get_actual_data('https://onlinedata.plzen.eu/data-pd-rychtarka-actual.php')

res = get_historical_daily_statistics(historical_data)
res_2 = get_historical_time_daily_statistics(historical_data)
print()