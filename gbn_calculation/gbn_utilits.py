from datetime import datetime, timedelta
import json
import os
import statistics
import pprint

def get_hourly_consumption(file_name):
    # file_path = os.path.join('C:', os.sep, "Users", "pvsol", "Downloads", file_name)
    file_path = f"templates/{file_name}"
    with open(file_path) as f:
        days_for_gbn = json.load(f)
    return days_for_gbn

def get_work_week_days():
    # file_path = os.path.join('C:', os.sep, "Users", "pvsol", "Downloads", 'weekdays.json')
    file_path = r'C:/Users/psolovey.GSN07/Desktop/automation/useful_functions/templates/weekdays.json'
    with open(file_path) as f:
        days = json.load(f)
    return days

def find_nearest_date(dates_list, target_date, direction='next'):
    sorted_dates = sorted(dates_list, reverse=(direction == 'previous'))
    for date in sorted_dates:
        if (direction == 'next' and date > target_date) or (direction == 'previous' and date < target_date):
            return date
    return target_date if target_date in dates_list else None

def get_value_by_date_and_hour(data, date, hour):
    # Ensure that we only access entries if they are dictionaries
    return next((entry.get(hour, 0) for entry in data.get(date, []) if isinstance(entry, dict) and hour in entry), 0)

def calculate_average_gbn(hours_range, weekdays, sorted_dates, num_days=10):
    num_days = max(1, num_days)
    latest_date = sorted_dates[0]
    dates_range = sorted_dates[1:num_days + 1]
    averages = {
        hour: round(sum(entry.get(hour, 0) for date in dates_range for entry in weekdays[date]) / num_days, 4)
        for hour in hours_range
    }
    return {latest_date: [{hour: avg} for hour, avg in averages.items()]}

def calculate_overall_average(hours_range, weekdays, sorted_dates):
    dates_range = sorted_dates[:len(sorted_dates) - 10]
    total, count = 0, 0
    for hour in hours_range:
        hour_str = hour
        for date in dates_range:
            total += sum(entry.get(hour_str, 0) for entry in weekdays[date] if isinstance(entry, dict))
            count += sum(1 for entry in weekdays[date] if isinstance(entry, dict) and hour_str in entry)
    return round(total / count, 4) if count else 0

def tweak_values(hours_range, date, weekdays, gbns, days):
    previous_date = find_nearest_date(days, date, 'previous')
    adjustment = 0
    if previous_date in list(gbns.keys()):
        # for hour in hours_range:
            # day_week = get_value_by_date_and_hour(weekdays, previous_date, hour)
            # day_gbn = get_value_by_date_and_hour(gbns, previous_date, hour)
        adjustment = sum(
            get_value_by_date_and_hour(weekdays, previous_date, hour) - get_value_by_date_and_hour(gbns, previous_date, hour)
            for hour in hours_range
        )

    return round(adjustment / 2, 4)

def apply_gbns_with_tweaks(gbns, tweaks):
    gbns_with_tweak = {}
    gbns_days = list(gbns.keys())
    zero_tweak_day = gbns_days[-1]
    for day, hourly_values in gbns.items():
        adjusted_day = []
        for hourly_gbn in gbns.get(day, []):
            hour, value = next(iter(hourly_gbn.items()))
            if day == zero_tweak_day:
                adjusted_day.append({hour: round(value, 4)})
            else:
                tweak_factor = 1 if abs(tweaks[day] / value) <= 0.2 else 1.2 if tweaks[day] > 0 else 0.8
                if tweak_factor == 1:
                    adjusted_day.append({hour: round(value + tweaks[day], 4)})
                else:
                    adjusted_day.append({hour: round(value * tweak_factor, 4)})

        gbns_with_tweak[day] = adjusted_day
    return gbns_with_tweak

def compute_rmse(weekdays, gbns):
    range_days = sorted(list(gbns.keys()), reverse=True)
    total_difference, count = 0, 0

    for date in range_days:
        if date in weekdays and date in gbns:
            gbns_dict = {list(d.keys())[0]: list(d.values())[0] for d in gbns[date]}
            for hour_entry in weekdays[date]:
                if isinstance(hour_entry, dict):  # Ensure we only process dictionary entries
                    hour, actual_value = next(iter(hour_entry.items()))
                    predicted_value = gbns_dict.get(hour)
                    if predicted_value is not None:
                        total_difference += round((actual_value - predicted_value) ** 2, 4)
                        count += 1
    return round((total_difference / count) ** 0.5, 4) if count > 0 else None

def extract_date_slice(data, start_date_str, num_days):
    num_days += 10
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    sliced_data = {date: data[date] for date in sorted(data.keys(), reverse=True) if datetime.strptime(date, "%Y-%m-%d") <= start_date}
    return dict(list(sliced_data.items())[:num_days][::-1])

def date_verification(date):
    sorted_dates = sorted(get_work_week_days()['work_days'])
    target_date_obj = datetime.strptime(date, "%Y-%m-%d")
    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in sorted_dates]
    previous_date = None

    for date_obj in date_objects:
        if date_obj == target_date_obj:
            # Если нашли точное совпадение, возвращаем его
            return date
        elif date_obj < target_date_obj:
            # Обновляем предыдущую дату, если она меньше целевой
            previous_date = date_obj
        else:
            # Как только нашли дату больше целевой, прекращаем поиск
            break

        # Возвращаем предыдущую дату в формате "гггг-мм-дд" или None
    return previous_date.strftime("%Y-%m-%d") if previous_date else None

def data_preparation_for_gbn(data):
    workdays = get_work_week_days()['work_days']
    workdays_for_gbns = {date: data for date, data in data.items() if date in workdays}
    return workdays_for_gbns

def get_last_45_dates(data):
    # Получаем список всех ключей (дат) в словаре
    all_dates = list(data.keys())

    # Проверяем, есть ли в словаре хотя бы десять дат
    if len(all_dates) < 45:
        # Если меньше десяти, возвращаем пустой словарь или обрабатываем это как-то иначе
        return {}

    # Получаем последние десять дат
    last_ten_dates = all_dates[-45:]

    # Создаем новый словарь с последними десятью датами
    last_ten_data = {date: data[date] for date in last_ten_dates}

    return last_ten_data

def get_hours_ranges(time_zone):
    hours_range = range(8, 22) if time_zone == 1 else range(5, 18)
    hours_range_for_tweak = range(16, 18) if time_zone == 1 else range(12, 14)
    result = {
        'hours_range': hours_range,
        'hours_range_for_tweak': hours_range_for_tweak,
    }
    return result

# Функции для подготовки данных и подбор 20 максимально похожих по потреблению дней
def preprocess_data(consumption_data, time_zone):
    """Convert the input format to a uniform dictionary with hours as keys."""
    processed_data = {}
    hours_ranges = get_hours_ranges(time_zone)
    for day, hourly_values in consumption_data.items():
        # Merge the list of hourly dictionaries into a single dictionary
        hourly_data = {int(list(item.keys())[0]): list(item.values())[0] for item in hourly_values}
        # Fill in missing hours with 0 (if needed)
        complete_day_data = [hourly_data.get(hour, 0) for hour in hours_ranges]
        processed_data[day] = complete_day_data
    return processed_data

def initialize_result(days_for_gbn):
    """Initialize the result dictionary with large/small values for indicators."""
    large_value = float('inf')
    small_value = float('-inf')
    return {
        'min_double_rmse_no_tweak': {'indicator': large_value, 'days': {}, 'rmse_data': {}},
        'min_double_rmse_with_tweak': {'indicator': large_value, 'days': {}, 'rmse_data': {}},
        'min_double_rmse_with_tweak_yesterday': {'indicator': large_value, 'days': {}, 'rmse_data': {}},
        'max_rrmse_no_tweak': {'indicator': small_value, 'days': {}},
        'max_rrmse_with_tweak': {'indicator': small_value, 'days': {}},
        'max_rrmse_with_tweak_yesterday': {'indicator': small_value, 'days': {}},
        'days_for_gbn': days_for_gbn,
        'gbn_for_20_days': {},
    }


def update_result(result, rmse_data, weekdays):
    """Update the result dictionary based on RMSE and RRMSE values."""
    updated = False
    checks = [
        ('min_double_rmse_no_tweak', rmse_data['rmse_no_tweak'], lambda x, y: x < y),
        ('min_double_rmse_with_tweak', rmse_data['rmse_with_tweak'], lambda x, y: x < y),
        ('min_double_rmse_with_tweak_yesterday', rmse_data['rmse_with_tweak_yesterday'], lambda x, y: x < y),
        ('max_rrmse_no_tweak', rmse_data['rrmse_no_tweak'], lambda x, y: x > y),
        ('max_rrmse_with_tweak', rmse_data['rrmse_with_tweak'], lambda x, y: x > y),
        ('max_rrmse_with_tweak_yesterday', rmse_data['rrmse_with_tweak_yesterday'], lambda x, y: x > y),
    ]
    for key, value, comparator in checks:
        if comparator(value, result[key]['indicator']):
            updated = True
            result[key]['indicator'] = value
            result[key]['days'] = weekdays.copy()
            result[key]['rmse_data'] = rmse_data.copy()
    # print(f"Updated: {updated}")
    return updated


def find_date_with_max_deviation(data, hours_range):

    # Вычисляем медианные суммы значений элементов с 8 по 20 для всех дат
    sums = []
    for date, values in data.items():
        # Извлекаем значения элементов с 8 по 20, используя range
        selected_values = [list(values[i].values())[0] for i in hours_range]
        # Вычисляем сумму этих значений
        sums.append(sum(selected_values))

    # Вычисляем медиану сумм
    median_sum = statistics.median(sums)

    # Ищем дату с максимальным отклонением от медианы
    max_deviation = 0
    date_with_max_deviation = None

    for date, values in data.items():
        # Извлекаем значения элементов с 8 по 20, используя range
        selected_values = [list(values[i].values())[0] for i in hours_range]
        # Вычисляем сумму этих значений
        current_sum = sum(selected_values)
        # Вычисляем отклонение от медианы
        deviation = abs(current_sum - median_sum)

        # Обновляем максимальное отклонение и соответствующую дату
        if deviation > max_deviation:
            max_deviation = deviation
            date_with_max_deviation = date

    return date_with_max_deviation