import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def process_table(data: pd):
    weekdays_indices = []
    times = []
    for i in range(len(data)):
        # ID = data.iloc[i, 0]
        # capacity = data.iloc[i, 1]
        # num_occupied_spaces = data.iloc[i, 2] + data.iloc[i, 3]
        # num_free_spaces = data.iloc[i, 5]
        timestamp = data.iloc[i, 7]

        timestamp_list = timestamp.split(' ')

        date = timestamp_list[0]
        time = timestamp_list[1]
        times.append(time)

        weekday_idx = (pd.Timestamp(date)).day_of_week
        # weekday_name = weekdays_names[weekday_idx]
        weekdays_indices.append(weekday_idx)

    data['weekday_idx'] = weekdays_indices
    data['time'] = times

    return data


def get_weekday_data(data: pd, weekday: str):
    weekdays_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_idx = weekdays_list.index(weekday)
    test = data['datum_aktualizace']
    weekday_data = data.loc[data['datum_aktualizace'] == weekday_idx]
    # time.strptime(str(data['datum_aktualizace'])).tm_wday
    return weekday_data


def get_time_weekday_data(data: pd, times_start_end: list, weekday: str):
    weekday_data = get_weekday_data(data, weekday)
    time_delta = timedelta(hours=0, minutes=20)

    # weekday_data['datum_aktualizace'] = pd.to_datetime(weekday_data['datum_aktualizace'])
    weekday_data['time'] = pd.to_datetime(weekday_data['time'])
    # test = weekday_data[(weekday_data['datum_aktualizace'] > '2022-10-25 04:30:00') & (weekday_data['datum_aktualizace'] < ' 2022-11-27 11:00:00')]
    if len(times_start_end) > 1:
        start_time = times_start_end[0]
        end_time = times_start_end[1]
        time_weekday_data = weekday_data[(weekday_data['time'] > start_time) & (weekday_data['time'] < end_time)]
    else:
        time = times_start_end[0]
        time_format = '%H:%M:%S'
        time = datetime.strptime(time, time_format)
        time_sub_delta = str(time - time_delta).split(' ')[1]
        time_add_delta = str(time + time_delta).split(' ')[1]
        time_weekday_data = weekday_data[(weekday_data['time'] > time_sub_delta) & (weekday_data['time'] < time_add_delta)]

    return time_weekday_data


def get_historical_daily_statistics(historical_data_nove_divadlo):
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
    data_array = historical_data_nove_divadlo.values

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


def get_historical_time_daily_statistics(historical_data_nove_divadlo):
    data_list = []
    weekdays_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data_array = historical_data_nove_divadlo.values
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
    res = get_time_daily_data(sorted_list)
    res = create_final_format(res)

    return res


def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    timestamp = t.replace(second=0, microsecond=0, minute=0, hour=t.hour)+timedelta(hours=t.minute//30)
    rounded_time = str(timestamp).split(' ')[1]

    return rounded_time


def alloc_matrix2d(W, H):
    """ Pre-allocate a 2D matrix of empty lists. """
    return [[[] for i in range(W)] for j in range(H)]


def get_time_daily_data(data: list):
    res = alloc_matrix2d(7,24)
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
        time_idx = int(time.split(':')[0])
        num_occupied_spaces = data_temp[2]
        num_free_spaces = data_temp[3]

        res[time_idx][weekday_idx].append((num_occupied_spaces, num_free_spaces))

    return res


def count_average_tuples(list_of_tuples):
    sum_1 = 0
    sum_2 = 0

    for tuple in list_of_tuples:
        sum_1 += tuple[0]
        sum_2 += tuple[1]

    return (round(sum_1 / len(list_of_tuples)), round(sum_2 / len(list_of_tuples)))



def create_final_format(data: list):
    res = alloc_matrix2d(7, 24)
    for i in range(len(data)):
        sublist_1 = data[i]
        for j in range(len(sublist_1)):
            sublist_2 = sublist_1[j]
            tuple_avg = count_average_tuples(sublist_2)
            res[i][j] = tuple_avg

    return res


def count_average(weekdays: dict):
    res = {}
    for weekday in weekdays:
        value = weekdays[weekday]
        avg_occupied_spaces = round(value[0] / value[2])
        avg_free_spaces = round(value[1] / value[2])

        res.update({weekday: [avg_occupied_spaces, avg_free_spaces]})

    return res


def count_weighted_average(data):
    times_datetime = [datetime.time(d) for d in data['time']]
    weights = []

    for time_datetime in times_datetime:
        weight = int(time_datetime.strftime("%H%M%S"))
        weights.append(weight)

    num_occupied_spaces = data['kp'] + data['dp_bez_rezervace']
    weight_avg_occupied_spaces = ((np.array(weights) * num_occupied_spaces).sum()) / np.array(weights).sum()

    weight_avg_free_spaces = ((np.array(weights) * data['volno']).sum()) / np.array(weights).sum()

    return ((round(weight_avg_occupied_spaces), round(weight_avg_free_spaces)))

