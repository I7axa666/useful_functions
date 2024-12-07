import csv

def calculate_total_cost(price, contractual_volume, availability_days, total_days, reduction_hours, successful_discharge, total_discharge, total_events):
    unsuccessful_discharge = total_discharge - successful_discharge
    # Проверка входных данных
    if total_events > 5:
        raise ValueError("Количество событий за месяц не может быть больше 5.")
    if successful_discharge + unsuccessful_discharge > total_events:
        raise ValueError("Сумма успешных и неуспешных разгрузок не может превышать общее количество событий.")
    if availability_days > total_days:
        raise ValueError("Количество дней готовности не может быть больше общего количества дней.")

    # Расчет распределенного объема на событие
    distributed_volume = (contractual_volume * (successful_discharge + unsuccessful_discharge)) / max(1, (successful_discharge + unsuccessful_discharge))
    # print(f'distributed_volume={distributed_volume}')

    # Расчет недопоставки
    # k_part = round(1.25 / 1.5 * (total_discharge / total_events), 4)
    k_part = round(1.25/1.5 * (total_discharge / total_events) ** (0.85 * (total_days - availability_days) / total_days) * (1 - 0.5 * (total_days - availability_days) / total_days), 4)
    delta_5 = round((k_part * 1.5 * max(0, distributed_volume)), 4)
    undersupply_1 = round((delta_5 * unsuccessful_discharge * reduction_hours) / max(1, (total_discharge * reduction_hours)), 4)
    # print(f'undersupply_1={undersupply_1}')

    delta_2_2 = 1.075 * contractual_volume
    undersupply_2 = round(delta_2_2 * (total_days - availability_days) / total_days, 4)
    # print(f'undersupply_2={undersupply_2}')

    undersupply = round((undersupply_1 + undersupply_2), 4)

    # Расчет фактически исполненного объема
    actual_volume = round(max(0, (distributed_volume - undersupply)), 4)
    # print(f'actual_volume={actual_volume}')

    # Расчет совокупной стоимости услуг
    if actual_volume == 0:
        if undersupply < contractual_volume:
            return 0
        fine_amount = undersupply - contractual_volume
        total_cost = round(-1 * fine_amount * reduction_hours / 4 * price, 2)
    else:
        if actual_volume < 0.05: actual_volume = 0
        total_cost = round(actual_volume * reduction_hours / 4 * price, 2)

    return total_cost


# Пример вызова функции
# total_cost = calculate_total_cost(
#     price=437402,
#     contractual_volume=6,
#     availability_days=10,
#     total_days=21,
#     reduction_hours=4,
#     successful_discharge=2,
#     total_discharge=2,
#     total_events=5
# )
#
# print(total_cost)

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
    # print(results)
    return results

# Пример вызова функции
data = financial_result_matrices(
    price=437402,
    contractual_volume=1,
    availability_days=0, # дни готовности
    unavailability_days=0, # дни неготовности
    total_days=21,
    reduction_hours=4,
    successful_discharge=0, # успешные разгрузки
    total_discharge=5, # количество направленных команд
    total_events=5
)

# pprint.pp(data)

column_headers = ["Разгрузки"]
first_values_list = next(iter(data[0].values()))
for value_dict in first_values_list:
    # Поскольку в каждом словаре только один элемент, извлекаем ключ
    column_headers.extend(value_dict.keys())
# print(column_headers)

with open("../New_Matrix.csv", mode="w", newline='', encoding="utf-8-sig") as file:
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

print("New_Matrix.csv is done")