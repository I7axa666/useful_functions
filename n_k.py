import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os

# Читаем XML файл
parser = ET.XMLParser(encoding="utf-8")
tree = ET.parse(os.path.join("C:", os.sep, "Users", "psolovey.GSN07", "Downloads", "1234.xml"), parser)
root = tree.getroot()

headers = [cell.text for cell in root.find('row')]

# Задаем начальные параметры
data = []
max_effect = 0
best_N = 0
best_K = 0
average_for_N = 0

# Конвертируем данные под нужный тип
conversion_functions = {
    "Дата": lambda x: datetime.strptime(x, '%d.%m.%Y'),
    "ЦЗСП": int,
    "Параметр N": int,
    "Параметр K": float,
    "Средний эффект за предшествующие рабочие дни, руб": float,
    "Эффект от ЦЗСП, руб": lambda x: float(x) if x else 'NaN'
}

# Собираем список дней с полученными параметрами
for row in root.findall('row')[1:]:
    row_data = {}
    for i, cell in enumerate(row):
        header = headers[i]
        convert = conversion_functions.get(header, lambda x: x)
        try:
            row_data[header] = convert(cell.text)
        except ValueError:
            row_data[header] = 'NaN'
    data.append(row_data)

# Убираем выходные дни
data_workday = [row for row in data if row.get('Эффект от ЦЗСП, руб') != 'NaN']

# Добавляем один день в конец для расчета параметров на будущую дату
data_workday.append({
    'Дата': data[-1]['Дата'] + timedelta(days=1),
    'ЦЗСП': 0, 'Параметр N': 0,
    'Параметр K': 0.0,
    'Средний эффект за предшествующие рабочие дни, руб': 1.0,
    'Эффект от ЦЗСП, руб': 1.0
})

# Вычисляем крайнюю дату для начала расчетов
first_date = data[-1]['Дата'] - timedelta(days=29)
index_of_first_date = next((i for i, row in enumerate(data_workday) if row.get("Дата") >= first_date), None)

if index_of_first_date is not None:
    work_data = data_workday[index_of_first_date-10:]
else:
    work_data = []

# Рассчитываем среднее значение "Эффект от ЦЗСП, руб" за предыдущие N дней

for N in range(3, 11):
    for K in [round(x * -0.01, 2) for x in range(-300, -99)]:
        events = []
        for i in range(10, len(work_data)):
            previous_values = [work_data[j]["Эффект от ЦЗСП, руб"] for j in range(i-N, i)]
            average = round(sum(previous_values) / N, 2)

            if work_data[i]["Эффект от ЦЗСП, руб"] > average * K:
                events.append(work_data[i]["Эффект от ЦЗСП, руб"])

        if len(events) > 5:
            events = events[:5]

        total_effect = sum(events)

        # Пропуск обновления, если total_effect равен 0
        if total_effect == 0:
            continue

        if total_effect > max_effect or (total_effect == max_effect and (N > best_N or (N == best_N and K < best_K))):
            max_effect = total_effect
            best_N = N
            best_K = K

previous_values = [work_data[j]["Эффект от ЦЗСП, руб"] for j in range(len(work_data)-best_N-1, len(work_data)-1)]
average_for_N = round(sum(previous_values) / best_N, 2)

# print(work_data[len(work_data) - 1])

        # print(f"N = {N}, K = {K}, Total Effect = {total_effect}")

print(f"Лучшие параметры: N = {best_N}, K = {best_K}")
print(f"Средний эффект за {N}: {average_for_N}")
print(f"Порог: {round(average_for_N * best_K, 0)}")