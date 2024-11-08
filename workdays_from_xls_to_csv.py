import pandas as pd
import json
from datetime import datetime

# Загрузка данных из файла XLSX
file_path = 'templates/weekdays.xlsx' # Укажите путь к вашему файлу
df = pd.read_excel(file_path)

# Преобразование дат в формат ISO 8601 (гггг-мм-дд)
df['Рабочие'] = pd.to_datetime(df['Рабочие'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
df['Праздники и Выходные'] = pd.to_datetime(df['Праздники и Выходные'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
df['Понедельники и первые р.д. после праздников'] = pd.to_datetime(df['Понедельники и первые р.д. после праздников'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')

# Создание словаря с тремя ключами
data_dict = {
    "work_days": df['Рабочие'].dropna().tolist(),
    "holliday_weekends": df['Праздники и Выходные'].dropna().tolist(),
    "mondays_or_first_day": df['Понедельники и первые р.д. после праздников'].dropna().tolist()
}

# Определение имени выходного файла
output_file_name = datetime.now().strftime('%d_%m_%Y') + '.json'

# Запись данных в JSON файл
with open(output_file_name, 'w', encoding='utf-8') as json_file:
    json.dump(data_dict, json_file, ensure_ascii=False, indent=4)

print(f"Данные успешно сохранены в файл {output_file_name}")