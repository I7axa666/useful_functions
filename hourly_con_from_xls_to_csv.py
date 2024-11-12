import pandas as pd
import json
import os
from datetime import datetime, date

# Загрузка данных из файла XLSX
file_path = os.path.join("C:", os.sep, "Users", "psolovey.GSN07", "Downloads", "51070.xlsx") # Укажите путь к вашему файлу
df = pd.read_excel(file_path)

# Преобразование столбца "дата" в формат ISO 8601 (гггг-мм-дд)
df['дата'] = pd.to_datetime(df['дата'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')

# Преобразование "интервал" в целое число и "потребление" в float
df['интервал'] = df['интервал'].astype(int)
df['потребление'] = df['потребление'].astype(float)

# Сортировка данных по дате
df.sort_values(by='дата', inplace=True)


# Группировка данных по дате
grouped = df.groupby('дата')

# Создание структуры JSON
data_dict = {}
for date, group in grouped:
    intervals = []
    for _, row in group.iterrows():
        interval_data = {
            int(row['интервал']): row['потребление'],
        }
        # print(interval_data)
        intervals.append(interval_data)
    data_dict[date] = intervals

# Определение имени выходного файла
output_file_name = f'templates/51070.json'

# Запись данных в JSON файл
with open(output_file_name, 'w', encoding='utf-8') as json_file:
    json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

print(f"Данные успешно сохранены в файл {output_file_name}")