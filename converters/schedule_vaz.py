import xml.etree.ElementTree as ET
from openpyxl import Workbook
import os

# Читаем XML файл
parser = ET.XMLParser(encoding="utf-8")
tree = ET.parse(os.path.join("C:", os.sep, "Users", "psolovey.GSN07", "Downloads", "BSP_VOLGABRZ_PVOLGABR_20241030.xml"), parser)
root = tree.getroot()

high_values = []
target_date_element = root.find('.//target-date')
date_value = target_date_element.get('value')
formatted_date = f"{date_value[6:8]}.{date_value[4:6]}.{date_value[0:4]}"
for hour in root.findall('.//hour'):
    for interval in hour.findall('.//interval'):
        high_value = interval.find('high-value')
        if high_value is not None:
            high_values.append(int(high_value.text) * 1000)

wb = Workbook()
ws = wb.active

# Записываем значения в первый столбец
for index, value in enumerate(high_values, start=1):
    ws.cell(row=index, column=1, value=value)

# Сохраняем файл
wb.save(os.path.join("C:", os.sep, "Users", "psolovey.GSN07", "Downloads", "schedule_vaz.xlsx"))

print(high_values)

