import json
import os
import pprint
def get_work_week_days():
    # file_path = os.path.join('C:', os.sep, "Users", "pvsol", "Downloads", 'weekdays.json')
    print(os.getcwd())
    file_path = 'templates/weekdays.json'

    with open(file_path) as f:
        days = json.load(f)
    return days

if __name__ == '__main__':
    pprint.pp(get_work_week_days())