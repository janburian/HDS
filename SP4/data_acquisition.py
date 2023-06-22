from pathlib import Path
import pandas as pd
import requests
from io import StringIO
from datetime import datetime, timedelta


def load_historical_data(path_to_data: Path):
    historical_data = pd.read_csv(path_to_data)
    timestamp_conversion = pd.to_datetime(historical_data['datum_aktualizace'])
    historical_data['datum_aktualizace'] = timestamp_conversion

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


def get_data_weekday(data: pd, weekday: str):
    date_indices = get_indices_weekday(data, weekday)
    relevant_data = data.iloc[date_indices]

    return relevant_data


def get_indices_weekday(data: pd, weekday: str):
    indices = []
    weekdays_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_idx = weekdays_list.index(weekday)
    for i in range(len(data)):
        timestamp = data.iloc[i, 7]
        # timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        if timestamp.day_of_week == weekday_idx:
            indices.append(i)

    return indices


def get_data_month(data: pd, month: str):
    month_indices = get_indices_month(data, month)
    relevant_data = data.iloc[month_indices]

    return relevant_data


def get_indices_month(data: pd, month: str):
    indices = []
    months_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                   'November', 'December']
    month_idx = months_list.index(month)
    for i in range(len(data)):
        timestamp = data.iloc[i, 7]
        # timestamp = time.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

        if timestamp.month == (month_idx + 1):
            indices.append(i)

    return indices


def get_indices_certain_date(data: pd, year, month, day):
    indices = []
    certain_date = datetime(year, month, day).date()

    for i in range(len(data)):
        timestamp_date = (data.iloc[i, 7]).date()

        if timestamp_date == certain_date:
            indices.append(i)

    return indices


def get_data_certain_date_time(data: pd, year: int, month: int, day: int, hour: int, minute: int, second: int):
    date_indices = get_indices_certain_date(data, year, month, day)
    relevant_data = data.iloc[date_indices]
    certain_time = str(datetime(year, month, day, hour, minute, second).time())
    IDs_date_time = get_IDs_time(relevant_data, [certain_time])
    date_time_relevant_data = relevant_data.loc[relevant_data['ID'].isin(IDs_date_time)]

    return date_time_relevant_data


def get_data_certain_date(data: pd, year: int, month: int, day: int):
    date_indices = get_indices_certain_date(data, year, month, day)
    relevant_data = data.iloc[date_indices]

    return relevant_data


def get_IDs_time(data: pd, times_start_end):
    time_delta = timedelta(hours=0, minutes=20)

    if len(times_start_end) > 1:
        return get_IDs_between_start_end(data, times_start_end)

    else:
        return get_IDs_only_one_time(data, time_delta, times_start_end)


def get_IDs_only_one_time(data, time_delta, times_start_end):
    IDs = []
    one_time_timestamp = datetime.strptime(times_start_end[0], '%H:%M:%S')
    time_sub_delta = (one_time_timestamp - time_delta).time()
    time_add_delta = (one_time_timestamp + time_delta).time()
    for i in range(len(data)):
        timestamp = data.iloc[i, 7]
        time = timestamp.time()
        if time_sub_delta <= time <= time_add_delta:
            IDs.append(data.iloc[i, 0])

    return IDs


def get_IDs_between_start_end(data, times_start_end):
    IDs = []
    start_timestamp = datetime.strptime(times_start_end[0], '%H:%M:%S')
    end_timestamp = datetime.strptime(times_start_end[1], '%H:%M:%S')
    start = start_timestamp.time()
    end = end_timestamp.time()
    for i in range(len(data)):
        timestamp = data.iloc[i, 7]
        time = timestamp.time()
        if start <= time <= end:
            IDs.append(data.iloc[i, 0])

    return IDs


def get_data_weekday_time(data: pd, day, times_start_end):
    day_indices = get_indices_weekday(data, day)
    print(max(day_indices))
    day_relevant_data = data.iloc[day_indices]
    day_relevant_data.reset_index(drop=True)
    time_day_IDs = get_IDs_time(day_relevant_data, times_start_end)
    # day_time_relevant_data = data.iloc[time_day_IDs]
    day_time_relevant_data = day_relevant_data.loc[day_relevant_data['ID'].isin(time_day_IDs)]

    return day_time_relevant_data


def get_actual_info(actual_data: pd):
    return actual_data.iloc[[0]]


def count_average(data: pd):
    num_occupied_spaces = data['kp'] + data['dp_bez_rezervace']
    num_average_occupied_spaces = num_occupied_spaces.mean()

    num_average_free_spaces = data['volno'].mean()

    return num_average_occupied_spaces, num_average_free_spaces


# Obtaining data
# Historical
historical_data_nove_divadlo = load_historical_data(Path('./data/data-pd-novedivadlo.csv'))
# historical_data_nove_divadlo = process_table(historical_data_nove_divadlo)

historical_data_rychtarka = load_historical_data(Path('./data/data-pd-rychtarka.csv'))
# historical_data_rychtarka = process_table(historical_data_rychtarka)

# Actual
url_nove_divadlo = 'https://onlinedata.plzen.eu/data-pd-novedivadlo-actual.php'
url_rychtarka = 'https://onlinedata.plzen.eu/data-pd-rychtarka-actual.php'

actual_data_nove_divadlo = get_actual_data(url_nove_divadlo)
actual_data_rychtarka = get_actual_data(url_rychtarka)

# Queries
actual_info_rychtarka = get_actual_info(actual_data_rychtarka)
actual_info_nove_divadlo = get_actual_info(actual_data_nove_divadlo)

weekday_data = get_data_weekday(historical_data_nove_divadlo, 'Thursday')
month_data = get_data_month(historical_data_nove_divadlo, 'July')
certain_date_data = get_data_certain_date(historical_data_nove_divadlo, 2018, 12, 24)
certain_date_time_data = get_data_certain_date_time(historical_data_nove_divadlo, 2021, 12, 10, 13, 40, 0)
weekday_time_data_1 = get_data_weekday_time(historical_data_nove_divadlo, 'Tuesday', ['18:00:00', '19:00:00'])
weekday_time_data_2 = get_data_weekday_time(historical_data_nove_divadlo, 'Saturday', ['06:00:00'])

# Processing queries
# if len(time_weekday_data_1) > 0:
#     weightened_avg = count_weighted_average(time_weekday_data_1)
#     average = count_average(time_weekday_data_1)
# else:
#     print('Empty data.')

# res = get_historical_daily_statistics(historical_data_nove_divadlo)
# res_2 = get_historical_time_daily_statistics(historical_data_nove_divadlo)
print()
