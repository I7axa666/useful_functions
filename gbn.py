import pprint
from get_best_rrmse import *
from gbn_utilits import get_hourly_consumption

# Data Loading
days_for_gbn = get_hourly_consumption('templates/51070_31.json')
time_zone = 1

pprint.pp(get_best_rmse(days_for_gbn, time_zone))

# get_best_rmse(days_for_gbn, time_zone)

