import numpy as np
import os
import json
import pprint


from gbn_utilits import get_hours_ranges, get_work_week_days, calculate_average_gbn, tweak_values, \
    apply_gbns_with_tweaks, compute_rmse, calculate_overall_average, preprocess_data, data_preparation_for_gbn, \
    initialize_result, update_result, find_date_with_max_deviation, get_last_45_dates


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
            gbns.update(calculate_average_gbn(hours_ranges['hours_range'], weekdays, sorted_dates[i:i + 20],
                                              number_of_days_for_gbn))

    tweaks = {date: tweak_values(hours_ranges['hours_range_for_tweak'], date, weekdays, gbns, days['work_days']) for
              date in
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

    rrmse_no_tweak = round(
        rmse_no_tweak / calculate_overall_average(hours_ranges['hours_range'], weekdays, sorted_dates), 3)
    rrmse_with_tweak = round(
        rmse_with_tweak / calculate_overall_average(hours_ranges['hours_range'], weekdays, sorted_dates), 3)
    rrmse_with_tweak_yesterday = round(
        rmse_with_tweak_yesterday / calculate_overall_average(hours_ranges['hours_range'], weekdays, sorted_dates), 3)

    return {
        'rmse_no_tweak': rmse_no_tweak,
        'doubled_rmse_no_tweak': doubled_rmse_no_tweak,
        'rrmse_no_tweak': rrmse_no_tweak,
        'rmse_with_tweak': rmse_with_tweak,
        'doubled_rmse_with_tweak': doubled_rmse_with_tweak,
        'rrmse_with_tweak': rrmse_with_tweak,
        'rmse_with_tweak_yesterday': rmse_with_tweak_yesterday,
        'doubled_rmse_with_tweak_yesterday': doubled_rmse_with_tweak_yesterday,
        'rrmse_with_tweak_yesterday': rrmse_with_tweak_yesterday,
    }


def find_most_similar_days(consumption_data, time_zone):
    """
    Identify the most 'central' pattern (minimizing absolute differences)
    and find the 20 closest days to it.
    """
    # Preprocess the data
    processed_data = preprocess_data(consumption_data, time_zone)

    # Convert the dictionary into a numpy array
    days = list(processed_data.keys())
    hourly_data = np.array([processed_data[day] for day in days])  # Shape: (num_days, 24)

    # Compute the central pattern (mean hourly consumption across all days)
    central_pattern = np.mean(hourly_data, axis=0)

    # Calculate the absolute difference for each day
    differences = np.abs(hourly_data - central_pattern)
    total_differences = np.sum(differences, axis=1)

    # Find indices of the 20 closest days
    closest_indices = np.argsort(total_differences)[:20]
    closest_days = [days[idx] for idx in closest_indices]

    return {key: val for key, val in consumption_data.items() if key in closest_days}


def get_best_rmse(days_for_gbn, time_zone=1):
    workdays = data_preparation_for_gbn(get_last_45_dates(days_for_gbn))
    result = initialize_result(get_last_45_dates(days_for_gbn))
    workdays_len = len(workdays)

    while workdays_len > 20:
        intermediate_result = initialize_result(days_for_gbn)

        result_updated = False
        rmse_data = get_rmse_rrmse(workdays, time_zone)
        update_result(intermediate_result, rmse_data, workdays)

        for key in workdays.keys():
            workdays_copy = workdays.copy()
            workdays_copy.pop(key)
            rmse_data = get_rmse_rrmse(workdays_copy, time_zone)
            # print(rmse_data['rmse_no_tweak'], rmse_data['rmse_with_tweak'], rmse_data['rmse_with_tweak_yesterday'])
            res_up = update_result(result, rmse_data, workdays_copy)
            if res_up:
                result_updated = True
            update_result(intermediate_result, rmse_data, workdays_copy)

            # print(min(rmse_data['rmse_no_tweak'], rmse_data['rmse_with_tweak'], rmse_data['rmse_with_tweak_yesterday']), key)

        if result_updated:
            min_rmse_dict = {
                'min_double_rmse_no_tweak': result['min_double_rmse_no_tweak']['indicator'],
                'min_double_rmse_with_tweak': result['min_double_rmse_with_tweak']['indicator'],
                'min_double_rmse_with_tweak_yesterday': result['min_double_rmse_with_tweak_yesterday']['indicator'],
            }

            min_rmse_key = min(min_rmse_dict, key=min_rmse_dict.get)
            workdays = intermediate_result[min_rmse_key]['days']
        else:
            min_rmse_dict = {
                'min_double_rmse_no_tweak': intermediate_result['min_double_rmse_no_tweak']['indicator'],
                'min_double_rmse_with_tweak': intermediate_result['min_double_rmse_with_tweak']['indicator'],
                'min_double_rmse_with_tweak_yesterday': intermediate_result['min_double_rmse_with_tweak_yesterday']['indicator'],
            }
            min_rmse_key = min(min_rmse_dict, key=min_rmse_dict.get)
            workdays = intermediate_result[min_rmse_key]['days']

            if workdays: # Проверяем, что workdays не пустой
                first_date = next(iter(workdays))
                workdays.pop(first_date)

        workdays_len -= 1

    len_rmse_days = [
        len(result['min_double_rmse_no_tweak']['days']),
        len(result['min_double_rmse_with_tweak']['days']),
        len(result['min_double_rmse_with_tweak_yesterday']['days']),
    ]

    if 20 not in len_rmse_days:
        gbn_for_20_days = find_most_similar_days(workdays, time_zone)
        rmse_for_20 = {}
        rmse_dict = get_rmse_rrmse(gbn_for_20_days, time_zone)
        rmse_for_20['indicator'] = rmse_dict[min(rmse_dict, key=rmse_dict.get)]
        rmse_for_20['rmse_data'] = rmse_dict
        rmse_for_20['days'] = gbn_for_20_days
        result['gbn_for_20_days'] = rmse_for_20

        return result

    return result

def get_best_rmse_with_max_deviation(days_for_gbn, time_zone=1):
    workdays = data_preparation_for_gbn(get_last_45_dates(days_for_gbn))
    hours_range = get_hours_ranges(time_zone)['hours_range']
    result = initialize_result(days_for_gbn)
    workdays_len = len(workdays)

    while workdays_len > 20:
        intermediate_result = initialize_result(days_for_gbn)

        result_updated = False
        rmse_data = get_rmse_rrmse(workdays, time_zone)
        update_result(intermediate_result, rmse_data, workdays)

        for key in workdays.keys():
            workdays_copy = workdays.copy()
            workdays_copy.pop(key)
            rmse_data = get_rmse_rrmse(workdays_copy, time_zone)
            # print(rmse_data['rmse_no_tweak'], rmse_data['rmse_with_tweak'], rmse_data['rmse_with_tweak_yesterday'])
            res_up = update_result(result, rmse_data, workdays_copy)
            if res_up:
                result_updated = True
            update_result(intermediate_result, rmse_data, workdays_copy)

            # print(min(rmse_data['rmse_no_tweak'], rmse_data['rmse_with_tweak'], rmse_data['rmse_with_tweak_yesterday']), key)

        if result_updated:
            min_rmse_dict = {
                'min_double_rmse_no_tweak': result['min_double_rmse_no_tweak']['indicator'],
                'min_double_rmse_with_tweak': result['min_double_rmse_with_tweak']['indicator'],
                'min_double_rmse_with_tweak_yesterday': result['min_double_rmse_with_tweak_yesterday']['indicator'],
            }

            min_rmse_key = min(min_rmse_dict, key=min_rmse_dict.get)
            workdays = intermediate_result[min_rmse_key]['days']
        else:
            min_rmse_dict = {
                'min_double_rmse_no_tweak': intermediate_result['min_double_rmse_no_tweak']['indicator'],
                'min_double_rmse_with_tweak': intermediate_result['min_double_rmse_with_tweak']['indicator'],
                'min_double_rmse_with_tweak_yesterday': intermediate_result['min_double_rmse_with_tweak_yesterday'][
                    'indicator'],
            }
            min_rmse_key = min(min_rmse_dict, key=min_rmse_dict.get)
            workdays = intermediate_result[min_rmse_key]['days']

            if workdays:  # Проверяем, что workdays не пустой
                workdays.pop(find_date_with_max_deviation(workdays, hours_range))

        workdays_len -= 1

    len_rmse_days = [
        len(result['min_double_rmse_no_tweak']['days']),
        len(result['min_double_rmse_with_tweak']['days']),
        len(result['min_double_rmse_with_tweak_yesterday']['days']),
    ]

    if 20 not in len_rmse_days:
        gbn_for_20_days = find_most_similar_days(workdays, time_zone)
        rmse_for_20 = {}
        rmse_dict = get_rmse_rrmse(gbn_for_20_days, time_zone)
        rmse_for_20['indicator'] = rmse_dict[min(rmse_dict, key=rmse_dict.get)]
        rmse_for_20['rmse_data'] = rmse_dict
        rmse_for_20['days'] = gbn_for_20_days
        result['gbn_for_20_days'] = rmse_for_20

        return result

    return result

