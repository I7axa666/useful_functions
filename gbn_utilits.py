from collections import defaultdict
import pprint
from datetime import datetime, timedelta

def find_date_or_next(dates_list, target_date):
    # Сортируем список дат в порядке убывания
    sorted_dates = sorted(dates_list, reverse=False)

    # Проверяем, есть ли целевая дата в списке
    if target_date in sorted_dates:
        return target_date

    # Ищем следующую более старшую дату
    for date in sorted_dates:
        if date > target_date:
            return date

    # Если ни целевой, ни более старшей даты нет, возвращаем None
    return None

def find_date_or_prevous(dates_list, target_date):
    # Сортируем список дат в порядке убывания
    sorted_dates = sorted(dates_list, reverse=True)

    # Проверяем, есть ли целевая дата в списке
    if target_date in sorted_dates:
        return target_date

    # Ищем следующую более старшую дату
    for date in sorted_dates:
        if date < target_date:
            return date

    # Если ни целевой, ни более старшей даты нет, возвращаем None
    return None

def get_value_by_date_and_hour(data, date, hour):
    # Проверяем, есть ли указанная дата в данных
    if date in data:
        # Проходим по списку значений для указанной даты
        for entry in data[date]:
            # Проверяем, есть ли указанный час в текущем словаре
            if hour in entry:
                return entry[hour]
    # Если дата или час не найдены, возвращаем None
    return 0
def average_gbn_for_numb(hours_range, weekdays, sorted_dates, numb=0):

    # Выбор предшествующих 10 дней
    latest_date = sorted_dates[0]
    numb_int = 10 if numb == 0 else numb
    previous_10_days = sorted_dates[1:numb_int + 1]

    # Инициализация словаря для хранения средних значений
    averages = defaultdict(list)
    for hour in hours_range:
        hour_str = str(hour)
        total = 0
        count = 0
        for date in previous_10_days:
            for entry in weekdays[date]:
                if hour_str in entry:
                    total += entry[hour_str]
                    count += 1
        if count > 0:
            averages[hour_str] = round(total / count, 4)

    # Формирование результата
    result = {latest_date: [{hour: avg} for hour, avg in averages.items()]}

    return result


def average_for_numb(hours_range, weekdays, sorted_dates, date='', numb=0):
    numb_int = 10 if numb == 0 else numb
    date_str = sorted_dates[0] if date == '' else date
    previous_10_days = sorted_dates[sorted_dates.index(date_str):numb_int]
    total = 0
    count = 0

    for hour in hours_range:
        hour_str = str(hour)

        for date in previous_10_days:
            for entry in weekdays[date]:
                if hour_str in entry:
                    total += entry[hour_str]
                    count += 1

    # Формирование результата
    result = round(total / count, 4)

    return result

def get_value_by_date_and_hour(data, date, hour):
    # Проверяем, есть ли указанная дата в данных
    if date in data:
        # Проходим по списку значений для указанной даты
        for entry in data[date]:
            # Проверяем, есть ли указанный час в текущем словаре
            if hour in entry:
                return entry[hour]
    # Если дата или час не найдены, возвращаем None
    return 0

def tweak(hours_range_for_tweak, date, weekdays, gbns, days):
    sorted(days)
    result = 0
    current_date_obj = datetime.strptime(date, '%Y-%m-%d')
    previous_date_obj = current_date_obj - timedelta(days=1)
    futer_date_obj = current_date_obj + timedelta(days=1)

    previous_date_str = find_date_or_prevous(days, previous_date_obj.strftime('%Y-%m-%d'))
    # futer_date_obj_str = find_date_or_prevous(days, futer_date_obj.strftime('%Y-%m-%d'))

    for hour in hours_range_for_tweak:
        hour_str = str(hour)
        result += get_value_by_date_and_hour(weekdays, previous_date_str, hour_str) - get_value_by_date_and_hour(gbns, previous_date_str, hour_str)


    return round(result / 2, 4)

def get_gbns_with_tweak(gbns, tweaks, weekdays):
    gbns_with_tweak = {}
    for day, hourly_consumption in weekdays.items():
        # Инициализируем список для каждого дня только один раз
        gbn_list_with_tweak = []
        if day in gbns.keys():

            # total_day_consumption = sum(consumption for hour in hourly_consumption for consumption in hour.values())

            for hourly_gbn in gbns[day]:

                if tweaks[day] / abs(list(hourly_gbn.values())[0]) > 0.2:
                    for hour in hourly_gbn.keys():
                        if tweaks[day] > 0:
                            value = round(get_value_by_date_and_hour(gbns, day, hour) * 1.2, 4)
                        else:
                            value = round(get_value_by_date_and_hour(gbns, day, hour) * 0.8, 4)

                    gbn_list_with_tweak.append({hour: value})

                else:

                    for hour in hourly_gbn.keys():
                        # Добавляем данные только если они уникальны или соответствуют условиям
                        value = round(get_value_by_date_and_hour(gbns, day, hour) + tweaks[day], 4)
                        gbn_list_with_tweak.append({hour: value})

                        # print(day, hour, get_value_by_date_and_hour(gbns, day, hour), tweaks[day])

            gbns_with_tweak[day] = gbn_list_with_tweak

    return gbns_with_tweak


def get_rmse(weekdays, gbns, num_days, reference_obj, start_date=''):
    # Преобразуем строку даты в объект даты
    # start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    # pprint.pp(gbns)
    total_difference = 0
    count = 0
    days = sorted(list(gbns.keys()), reverse=True)
    start_date_str = days[0] if start_date == '' else start_date
    start_index = int(days.index(start_date_str))
    # pprint.pp(gbns)
    range_days = days[start_index:start_index + num_days]
    first_day = days[start_index + num_days - 1]
    gbns[first_day] = reference_obj[first_day]
    # print(first_day)
    # Проходим по указанному количеству дней
    for current_date in range_days:
        # current_date = (start_date - timedelta(days=i)).strftime("%Y-%m-%d")

        if current_date in weekdays and current_date in gbns:
            # Создаем словарь для быстрого доступа к значениям второго объекта
            gbns_dict = {list(d.keys())[0]: list(d.values())[0] for d in gbns[current_date]}

            # Проходим по каждому часу в первом объекте
            for entry in weekdays[current_date]:
                hour, value1 = list(entry.items())[0]
                if hour in gbns_dict:
                    # Вычисляем разницу и добавляем к общей сумме
                    value2 = gbns_dict[hour]
                    total_difference += (value1 - value2) ** 2
                    count += 1

    # Возвращаем среднее значение разницы
    return round((total_difference / count) ** 0.5, 4) if count > 0 else None

def get_date_slice_from_gbn(data, start_date_str, num_days):
    # Преобразуем строку даты в объект даты
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    result = {}

    # Сортируем даты в объекте в порядке убывания
    sorted_dates = sorted(data.keys(), reverse=True)

    # Проходим по отсортированным датам
    for date_str in sorted_dates:
        current_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Проверяем, входит ли текущая дата в диапазон
        if current_date <= start_date:
            result[date_str] = data[date_str]
            num_days -= 1

        # Если достигли нужного количества дней, выходим из цикла
        if num_days == 0:
            break

    # Сортируем результат по возрастанию дат
    sorted_result = dict(sorted(result.items(), key=lambda x: x[0]))

    return sorted_result