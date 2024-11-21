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
    delta_5 = round(((1.25 / 1.5 * (unsuccessful_discharge / total_events)) * 1.5 * max(0, distributed_volume)), 4)
    undersupply_1 = delta_5 if unsuccessful_discharge > 0 else 0
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
        fine_amount = undersupply - contractual_volume
        total_cost = round(-1 * fine_amount * reduction_hours / 4 * price, 2)
    else:
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