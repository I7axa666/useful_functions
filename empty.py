from datetime import datetime, timedelta


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


# Пример использования
data = {
    "2024-10-24": [{'14': 2652.4227}, {'15': 2660.49}],
    "2024-10-23": [{'15': 2668.4161}, {'16': 2636.284}],
    "2024-10-22": [{'15': 2633.1873}, {'16': 2620.3796}],
    "2024-10-20": [{'15': 2633.1873}, {'16': 2620.3796}],
    "2024-10-17": [{'15': 2633.1873}, {'16': 2620.3796}],
    "2024-10-15": [{'15': 2633.1873}, {'16': 2620.3796}]
}

date_slice = get_date_slice(data, "2024-10-23", 5)
print(date_slice)