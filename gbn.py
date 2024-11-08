import json
from collections import defaultdict
import pprint

from gbn_utilits import *

time_zone = 1
number_of_days_for_gbn = 10
target_date = '2024-10-24'
print(f'Ценовая зона {time_zone}\n Дней ГБН {number_of_days_for_gbn}')
days_for_gbn = {}
days = {}
day_tweak_with_gbn = {}
tweaks = {}
gbns = {}



hours_range = range(8, 22) if time_zone == 1 else range(5, 18)
hours_range_for_tweak = range(16, 18) if time_zone == 1 else range(12, 14)

with open('templates/51070.json') as f:
    data = json.load(f)
    days_for_gbn = data
    # print(WORK_DAYS)

with open('templates/weekdays.json') as f:
    data = json.load(f)
    days = data
    # print(days)

workdays = {date: value for date, value in days_for_gbn.items() if date in days['work_days']} # рабочие дни для расчета гбн для подбора дат
weekdays = get_date_slice_from_gbn(workdays, target_date, 20)


sorted_dates = sorted(weekdays.keys(), reverse=True)
latest_date = sorted_dates[0]


for i in sorted_dates:
    list_len = len(sorted_dates)
    index = sorted_dates.index(i)
    if list_len - number_of_days_for_gbn > index:
        gbn = average_gbn_for_numb(hours_range, weekdays, sorted_dates[index:index + 20], number_of_days_for_gbn)
        gbns.update(gbn)

# pprint.pp(gbns)

for date in sorted_dates:
    if len(sorted_dates) - 10 > sorted_dates.index(date):
        tweaks[date] = tweak(hours_range_for_tweak, date, weekdays, gbns, days['work_days'])



tweaks_yest_workday = {
    date: 0 if date in days['mondays_or_first_day'] else tweak_value for date, tweak_value in tweaks.items()
}


gbns_with_tweak = get_gbns_with_tweak(gbns, tweaks, weekdays)
gbns_with_tweak_yest_workday = get_gbns_with_tweak(gbns, tweaks_yest_workday, weekdays)

rmse_without_tweak = get_rmse(weekdays, gbns, number_of_days_for_gbn, gbns)
rmse_with_tweak = get_rmse(weekdays, gbns_with_tweak, number_of_days_for_gbn, gbns)
rmse_with_tweak_yest_workday = get_rmse(weekdays, gbns_with_tweak_yest_workday, number_of_days_for_gbn, gbns)

dubl_rmse_without_tweak = round(rmse_without_tweak * 2, 4)
dubl_rmse_with_tweak = round(rmse_with_tweak * 2, 4)
dubl_rmse_with_tweak_yest_workday = round(rmse_with_tweak_yest_workday * 2, 4)

rrmse_without_tweak = round(rmse_without_tweak / average_for_numb(hours_range, weekdays, sorted_dates, target_date, number_of_days_for_gbn), 3)
rrmse_with_tweak = round(rmse_with_tweak / average_for_numb(hours_range, weekdays, sorted_dates, target_date, number_of_days_for_gbn), 3)
rrmse_with_tweak_yest_workday = round(rmse_with_tweak_yest_workday / average_for_numb(hours_range, weekdays, sorted_dates, target_date, number_of_days_for_gbn), 3)


# print(rrmse_with_tweak_yest_workday)


pprint.pp(weekdays)

