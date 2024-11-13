# import pandas as pd
# import json
# import os
#
# # Load the data from the XLSX file
# file_path = os.path.join("C:", os.sep, "Users", "psolovey.GSN07", "Downloads", "51070.xlsx")
# df = pd.read_excel(file_path)
#
# # Convert 'дата' to ISO 8601 format and 'интервал'/'потребление' to numeric types
# df['дата'] = pd.to_datetime(df['дата'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
# df['интервал'] = df['интервал'].astype(int)
# df['потребление'] = df['потребление'].astype(float)
#
# # Sort by date (not necessary unless needed for output order)
# df.sort_values(by='дата', inplace=True)
#
# # Reshape data into JSON-ready format
# # Group by 'дата' and convert each group to a dictionary
# data_dict = (
#     df.groupby('дата')[['интервал', 'потребление']]  # Select only 'интервал' and 'потребление'
#     .apply(lambda x: x.set_index('интервал')['потребление'].to_dict())  # Convert each group to dict
#     .to_dict()
# )
#
# # Output file path
# output_file_name = 'templates/51070.json'
#
# # Save to JSON
# with open(output_file_name, 'w', encoding='utf-8') as json_file:
#     json.dump(data_dict, json_file, ensure_ascii=False, indent=4)
#
# print(f"Data successfully saved to {output_file_name}")

import json
import os
import pandas as pd
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