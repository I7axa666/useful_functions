import itertools
import concurrent.futures
from useful_functions.gbn_utilits import data_preparation_for_gbn, initialize_result, update_result
from gbn_calculation.get_rmse import get_rmse_rrmse

def generate_combinations(days_list, window=45):
    """Generate 45-day combinations sliding through the list if it's longer than 45."""
    if len(days_list) > window:
        return [days_list[i:i + window] for i in range(len(days_list) - window + 1)]
    return [days_list]


def get_best_rmse(days_for_gbn, time_zone, value):
    result = initialize_result()
    days_list = sorted(days_for_gbn.keys())
    combinations_list = generate_combinations(days_list)

    for combination in combinations_list:
        combination_dict = {date: days_for_gbn[date] for date in combination}
        workdays = data_preparation_for_gbn(combination_dict)
        workdays_list = list(workdays.keys())
        # Подсчитываем общее количество комбинаций
        total_count = 0
        # count = 0
        # for _ in itertools.combinations(workdays_list, 20):
        #     total_count += 1
        # Generate and process all 20-day combinations
        for weekday_combination in itertools.combinations(workdays_list, 20):
            total_count += 1
            print(total_count)
            # count += 1
            # if count % 1000 == 0 or count == total_count:
            #     print(f"Progress: {count / total_count * 100:.2f}%")
            weekdays = {date: days_for_gbn[date] for date in weekday_combination}
            rmse_data = get_rmse_rrmse(weekdays, time_zone)
            update_result(result, rmse_data, weekdays)
            if result['min_double_rmse_no_tweak']['indicator'] < value:
                return result

    return result


def process_combination(weekday_combination, days_for_gbn, time_zone, result, value):
    weekdays = {date: days_for_gbn[date] for date in weekday_combination}
    rmse_data = get_rmse_rrmse(weekdays, time_zone)
    update_result(result, rmse_data, weekdays)
    return result['min_double_rmse_no_tweak']['indicator'] < value

def get_best_rmse_parallel(days_for_gbn, time_zone, value):
    result = initialize_result()
    days_list = sorted(days_for_gbn.keys())
    combinations_list = generate_combinations(days_list)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for combination in combinations_list:
            combination_dict = {date: days_for_gbn[date] for date in combination}
            workdays = data_preparation_for_gbn(combination_dict)
            workdays_list = list(workdays.keys())

            for weekday_combination in itertools.combinations(workdays_list, 20):
                futures.append(executor.submit(process_combination, weekday_combination, days_for_gbn, time_zone, result, value))

        for future in concurrent.futures.as_completed(futures):
            if future.result():
                return result

    return result