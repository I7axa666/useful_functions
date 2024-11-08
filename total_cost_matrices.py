import pprint
import csv
from total_cost import calculate_total_cost

def financial_result_matrices(price, contractual_volume, availability_days, total_days, reduction_hours, total_events, successful_discharge, total_discharge, unavailability_days):
    results = []

    # Перебираем количество успешных разрядов
    for successful in range(successful_discharge, total_discharge + 1):
        # Перебираем общее количество разрядов
        for total in range(successful_discharge, total_discharge + 1):
            # Пропускаем итерацию, если успешных разрядов больше, чем общих
            if successful > total:
                continue

            # Формируем ключ для текущей комбинации успешных/общих разрядов
            key = f"{successful}/{total}"
            costs = []

            # Перебираем количество доступных дней
            for available_days in range(availability_days, total_days + 1 - unavailability_days):
                # Проверяем условия для расчета стоимости
                if available_days < availability_days - successful_discharge + total or available_days > total_days - total_events + total:
                    total_cost = "-"
                else:
                    # Вычисляем общую стоимость
                    total_cost = round(calculate_total_cost(
                        price=price,
                        contractual_volume=contractual_volume,
                        availability_days=available_days,
                        total_days=total_days,
                        reduction_hours=reduction_hours,
                        successful_discharge=successful,
                        total_discharge=total,
                        total_events=total_events
                    ), 0)
                # Добавляем результат в список
                costs.append({available_days: total_cost})

            # Добавляем текущий результат в общий список
            results.append({key: costs})

    return results

# Пример вызова функции
data = financial_result_matrices(
    price=437402,
    contractual_volume=6,
    availability_days=1, # дни готовности
    unavailability_days=2, # дни неготовности
    total_days=21,
    reduction_hours=4,
    successful_discharge=0, # успешные разгрузки
    total_discharge=3, # количество оставшихся событий
    total_events=5
)

# pprint.pp(data)

column_headers = ["Разгрузки"]
first_values_list = next(iter(data[0].values()))
for value_dict in first_values_list:
    # Поскольку в каждом словаре только один элемент, извлекаем ключ
    column_headers.extend(value_dict.keys())
# print(column_headers)

with open("New_File.csv", mode="w", newline='', encoding="utf-8-sig") as file:
    writer = csv.writer(file, delimiter=';') # Используем точку с запятой как разделитель

    # Записываем заголовки
    writer.writerow(column_headers)

    # Проходим по каждому элементу в списке
    for entry in data:
        for key, values in entry.items():
            # Создаем строку, начиная с ключа первого уровня
            row = [f"'{key}"]
            # Добавляем значения, заменяя '-' на пустую строку
            for value_dict in values:
                for _, value in value_dict.items():
                    row.append(int(value) if value != '-' else '')
            # Записываем строку в CSV
            writer.writerow(row)

print("New_File.csv is done")