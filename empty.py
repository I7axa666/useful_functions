# import xml.etree.ElementTree as ET
# from datetime import datetime, timedelta
# import requests
# import xmltodict
# import pprint
#
#
# def get_price_dependent():
#     url = 'https://www.atsenergo.ru/market/stats.xml'
#     current_date = datetime.now()
#     first_date = current_date - timedelta(days=60)
#
#     params = {
#         'type': 'drall',
#         'date1': first_date.strftime('%Y%m%d'),
#         'date2': current_date.strftime('%Y%m%d')
#     }
#     data_list = []
#
#     response = requests.get(url, params=params, verify=False)
#     root = ET.fromstring(response.content)
#
#     headers = [cell.text.lower() for cell in root.find('columns')]
#
#     conversion_functions = {
#         "target_date": lambda x: datetime.strptime(x, '%d.%m.%Y'),
#         "dr_type": int,
#         "prev_workday_count": int,
#         "k_dr_effect_avg": float,
#         "dr_effect_avg": float,
#         "dr_effect_total": lambda x: float(x) if x else 'NaN'
#     }
#
#     for row in root.findall('row'):
#         row_data = {}
#         for i, cell in enumerate(row):
#
#             header = headers[i]
#             convert = conversion_functions.get(header, lambda x: x)
#             try:
#                 row_data[header] = convert(cell.text)
#             except ValueError:
#                 row_data[header] = 'NaN'
#         data_list.append(row_data)
#
#
#     return data_list
#
#
# if __name__ == '__main__':
#     print(get_price_dependent())
name = 'fkjdjf'
print(f"{name}")