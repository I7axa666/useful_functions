import json
import os
import pandas as pd
from datetime import datetime, date

def convert_xlsx_to_json_for_forecast(xls_file_name):
    # Загрузка данных из файла XLSX
    file_path = os.path.join("C:", os.sep, "Users", "psolovey.GSN07", "Downloads", xls_file_name) # Укажите путь к вашему файлу
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
    data_list = []
    for date, group in grouped:
        for _, row in group.iterrows():
            value_dict = {
                "date": date,
                "hour": int(row['интервал']),
                "consumption": row['потребление'],
            }
            # print(interval_data)
            data_list.append(value_dict)

    # Определение имени выходного файла
    output_file_name = os.path.join('Z:', os.sep, 'Рабочий стол', 'pdfProject', 'templates', '51070_for_forecast.json')

    # Запись данных в JSON файл
    with open(output_file_name, 'w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)

    print(f"Данные успешно сохранены в файл {output_file_name}")
    # return data_list

if __name__ == '__main__':
    xlsx_file_name = '51070_accermann_21_24.xlsx'
    convert_xlsx_to_json_for_forecast(xlsx_file_name)