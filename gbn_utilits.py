from datetime import datetime, timedelta
import itertools
import json
import pprint

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
        str(hour): round(sum(entry.get(str(hour), 0) for date in dates_range for entry in weekdays[date]) / num_days, 4)
        for hour in hours_range
    }
    return {latest_date: [{hour: avg} for hour, avg in averages.items()]}

def calculate_overall_average(hours_range, weekdays, sorted_dates):
    dates_range = sorted_dates[:len(sorted_dates) - 10]
    total, count = 0, 0
    for hour in hours_range:
        hour_str = str(hour)
        for date in dates_range:
            total += sum(entry.get(hour_str, 0) for entry in weekdays[date] if isinstance(entry, dict))
            count += sum(1 for entry in weekdays[date] if isinstance(entry, dict) and hour_str in entry)
    return round(total / count, 4) if count else 0

def tweak_values(hours_range, date, weekdays, gbns, days):
    previous_date = find_nearest_date(days, date, 'previous')
    adjustment = 0
    if previous_date in list(gbns.keys()):
        adjustment = sum(
            get_value_by_date_and_hour(weekdays, previous_date, str(hour)) - get_value_by_date_and_hour(gbns, previous_date, str(hour))
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

def get_best_rmse(days_for_gbn, time_zone):

    result = {
        'min_double_rmse_no_tweak': {
            'indicator': 1000000,
            'days': {}
        },
        'min_double_rmse_with_tweak': {
            'indicator': 1000000,
            'days': {}
        },
        'min_double_rmse_with_tweak_yesterday': {
            'indicator': 1000000,
            'days': {}
        },
        'max_rrmse_no_tweak': {
            'indicator': 0,
            'days': {}
        },
        'max_rrmse_with_tweak': {
            'indicator': 0,
            'days': {}
        },
        'max_rrmse_with_tweak_yesterday': {
            'indicator': 0,
            'days': {}
        },
    }
    list_days_for_gbn = sorted(list(days_for_gbn.keys()))
    i = 0
    combinations_list = []
    if len(list_days_for_gbn) > 44:
        while i < len(list_days_for_gbn) - 44:
            combinations_list.append(list_days_for_gbn[i:i + 45])
            i += 1
    else:
        combinations_list.append(list_days_for_gbn)

    for combinaton in combinations_list:
        combination_dict = {date: value for date, value in days_for_gbn.items() if date in combinaton}
        workdays = data_preparation_for_gbn(combination_dict)
        workdays_list = list(workdays.keys())
        # Генерируем все возможные комбинации из 20 дней
        total_combinations = itertools.combinations(workdays_list, 20)

        # Перебираем комбинации и обрабатываем их по мере генерации
        for i, combination in enumerate(total_combinations, 1):

            weekdays = {date: value for date, value in days_for_gbn.items() if date in list(combination)}
            rmse_data = get_rmse_rrmse(weekdays, time_zone)

            if rmse_data['doubled_rmse_no_tweak'] < result['min_double_rmse_no_tweak']['indicator']:
                result['min_double_rmse_no_tweak']['indicator'] = rmse_data['doubled_rmse_no_tweak']
                result['min_double_rmse_no_tweak']['days'] = weekdays

            if rmse_data['doubled_rmse_with_tweak'] < result['min_double_rmse_with_tweak']['indicator']:
                result['min_double_rmse_with_tweak']['indicator'] = rmse_data['doubled_rmse_with_tweak']
                result['min_double_rmse_with_tweak']['days'] = weekdays

            if rmse_data['doubled_rmse_with_tweak_yesterday'] < result['min_double_rmse_with_tweak_yesterday']['indicator']:
                result['min_double_rmse_with_tweak_yesterday']['indicator'] = rmse_data['doubled_rmse_with_tweak_yesterday']
                result['min_double_rmse_with_tweak_yesterday']['days'] = weekdays

            if rmse_data['rrmse_no_tweak'] > result['max_rrmse_no_tweak']['indicator']:
                result['max_rrmse_no_tweak']['indicator'] = rmse_data['rrmse_no_tweak']
                result['max_rrmse_no_tweak']['days'] = weekdays

            if rmse_data['rrmse_with_tweak'] > result['max_rrmse_with_tweak']['indicator']:
                result['max_rrmse_with_tweak']['indicator'] = rmse_data['rrmse_with_tweak']
                result['max_rrmse_with_tweak']['days'] = weekdays

            if rmse_data['rrmse_with_tweak_yesterday'] > result['max_rrmse_with_tweak_yesterday']['indicator']:
                result['max_rrmse_with_tweak_yesterday']['indicator'] = rmse_data['rrmse_with_tweak_yesterday']
                result['max_rrmse_with_tweak_yesterday']['days'] = weekdays

    return result
def get_work_week_days():
    with open('templates/weekdays.json') as f:
        days = json.load(f)
    return days

def get_hourly_consumption(path):
    with open(path) as f:
        days_for_gbn = json.load(f)
    return days_for_gbn

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


def get_rmse_rrmse(weekdays, time_zone):
    hours_ranges = get_hours_ranges(time_zone)
    number_of_days_for_gbn = 10
    days = get_work_week_days()
    gbns = {}

    # Processed Data Preparation
    sorted_dates = sorted(weekdays.keys(), reverse=True)
    # pprint.pp(weekdays)
    # Calculations
    for i, date in enumerate(sorted_dates):
        if i + number_of_days_for_gbn < len(sorted_dates):
            gbns.update(calculate_average_gbn(hours_ranges['hours_range'], weekdays, sorted_dates[i:i + 20], number_of_days_for_gbn))

    tweaks = {date: tweak_values(hours_ranges['hours_range_for_tweak'], date, weekdays, gbns, days['work_days']) for date in
              sorted_dates if sorted_dates.index(date) < len(sorted_dates) - 10}
    tweaks_yesterday = {date: 0 if date in days['mondays_or_first_day'] else tweak for date, tweak in tweaks.items()}
    # pprint.pp(tweaks_yesterday)
    # Results with and without tweak adjustments
    gbns_with_tweak = apply_gbns_with_tweaks(gbns, tweaks)
    gbns_with_tweak_yesterday = apply_gbns_with_tweaks(gbns, tweaks_yesterday)
    # pprint.pp(gbns_with_tweak)
    # RMSE Calculations
    rmse_no_tweak = compute_rmse(weekdays, gbns)
    rmse_with_tweak = compute_rmse(weekdays, gbns_with_tweak)
    rmse_with_tweak_yesterday = compute_rmse(weekdays, gbns_with_tweak_yesterday)
    # pprint.pp(rmse_no_tweak)
    # Additional Metrics
    doubled_rmse_no_tweak = round(rmse_no_tweak * 2, 4)
    doubled_rmse_with_tweak = round(rmse_with_tweak * 2, 4)
    doubled_rmse_with_tweak_yesterday = round(rmse_with_tweak_yesterday * 2, 4)

    rrmse_no_tweak = round(rmse_no_tweak / calculate_overall_average(hours_ranges['hours_range'], weekdays, sorted_dates), 3)
    rrmse_with_tweak = round(
        rmse_with_tweak / calculate_overall_average(hours_ranges['hours_range'], weekdays, sorted_dates), 3)
    rrmse_with_tweak_yesterday = round(
        rmse_with_tweak_yesterday / calculate_overall_average(hours_ranges['hours_range'], weekdays, sorted_dates), 3)

    return {
        'doubled_rmse_no_tweak': doubled_rmse_no_tweak,
        'rrmse_no_tweak': rrmse_no_tweak,
        'doubled_rmse_with_tweak': doubled_rmse_with_tweak,
        'rrmse_with_tweak': rrmse_with_tweak,
        'doubled_rmse_with_tweak_yesterday': doubled_rmse_with_tweak_yesterday,
        'rrmse_with_tweak_yesterday': rrmse_with_tweak_yesterday,
    }

def data_preparation_for_gbn(data):
    workdays = get_work_week_days()['work_days']
    workdays_for_gbns = {date: data for date, data in data.items() if date in workdays}
    return workdays_for_gbns

def get_hours_ranges(time_zone):
    hours_range = range(8, 22) if time_zone == 1 else range(5, 18)
    hours_range_for_tweak = range(16, 18) if time_zone == 1 else range(12, 14)
    result = {
        'hours_range': hours_range,
        'hours_range_for_tweak': hours_range_for_tweak,
    }
    return result