import itertools
from gbn_utilits import data_preparation_for_gbn, get_rmse_rrmse

def initialize_result():
    """Initialize the result dictionary with large/small values for indicators."""
    large_value = float('inf')
    small_value = float('-inf')
    return {
        'min_double_rmse_no_tweak': {'indicator': large_value, 'days': {}},
        'min_double_rmse_with_tweak': {'indicator': large_value, 'days': {}},
        'min_double_rmse_with_tweak_yesterday': {'indicator': large_value, 'days': {}},
        'max_rrmse_no_tweak': {'indicator': small_value, 'days': {}},
        'max_rrmse_with_tweak': {'indicator': small_value, 'days': {}},
        'max_rrmse_with_tweak_yesterday': {'indicator': small_value, 'days': {}},
    }

def generate_combinations(days_list, window=45):
    """Generate 45-day combinations sliding through the list if it's longer than 45."""
    if len(days_list) > window:
        return [days_list[i:i + window] for i in range(len(days_list) - window + 1)]
    return [days_list]

def update_result(result, rmse_data, weekdays):
    """Update the result dictionary based on RMSE and RRMSE values."""
    checks = [
        ('min_double_rmse_no_tweak', rmse_data['doubled_rmse_no_tweak'], lambda x, y: x < y),
        ('min_double_rmse_with_tweak', rmse_data['doubled_rmse_with_tweak'], lambda x, y: x < y),
        ('min_double_rmse_with_tweak_yesterday', rmse_data['doubled_rmse_with_tweak_yesterday'], lambda x, y: x < y),
        ('max_rrmse_no_tweak', rmse_data['rrmse_no_tweak'], lambda x, y: x > y),
        ('max_rrmse_with_tweak', rmse_data['rrmse_with_tweak'], lambda x, y: x > y),
        ('max_rrmse_with_tweak_yesterday', rmse_data['rrmse_with_tweak_yesterday'], lambda x, y: x > y),
    ]
    for key, value, comparator in checks:
        if comparator(value, result[key]['indicator']):
            result[key]['indicator'] = value
            result[key]['days'] = weekdays.copy()

def get_best_rmse(days_for_gbn, time_zone):
    result = initialize_result()
    days_list = sorted(days_for_gbn.keys())
    combinations_list = generate_combinations(days_list)

    for combination in combinations_list:
        combination_dict = {date: days_for_gbn[date] for date in combination}
        workdays = data_preparation_for_gbn(combination_dict)
        workdays_list = list(workdays.keys())

        # Generate and process all 20-day combinations
        for weekday_combination in itertools.combinations(workdays_list, 20):
            weekdays = {date: days_for_gbn[date] for date in weekday_combination}
            rmse_data = get_rmse_rrmse(weekdays, time_zone)
            update_result(result, rmse_data, weekdays)

    return result
