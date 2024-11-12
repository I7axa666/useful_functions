import pprint
from gbn_utilits import *

# Data Loading
days_for_gbn = get_hourly_consumption('templates/51070.json')


# Initialization
data = {
    'time_zone': 1,
    'target_date': '2024-10-31',
    'number_of_days_for_gbn': 10,
    'days':  get_work_week_days(),
    'days_for_gbn': days_for_gbn
}

pprint.pp(get_rmse_rrmse(data))


