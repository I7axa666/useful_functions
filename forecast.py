import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime
import os
import seaborn as sns
from pyod.models.iforest import IForest
from prophet import Prophet
from sklearn.metrics import mean_absolute_percentage_error

print(datetime.now())

def load_and_preprocess(xls_file_name):
    # Загрузка данных из JSON файла
    json_file = os.path.join('Z:', os.sep, 'Рабочий стол', 'pdfProject', 'templates', xls_file_name)
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Преобразование в DataFrame
    df = pd.DataFrame(data)

    # Создание временного индекса
    df['datetime'] = pd.to_datetime(df['date']) + pd.to_timedelta(df['hour'], unit='h')
    df.set_index('datetime', inplace=True)

    # Удаление ненужных столбцов
    df.drop(columns=['date', 'hour'], inplace=True)

    return df

def visualize_and_detect_anomalies(df):
    df['consumption'].interpolate(method='linear', inplace=True)
    # Визуализация временного ряда
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=df, x=df.index, y='consumption')
    plt.title('Потребление электроэнергии')
    plt.xlabel('Дата')
    plt.ylabel('Потребление')
    plt.show()

    # Выявление аномалий
    model = IForest()
    df['anomaly'] = model.fit_predict(df[['consumption']])

    # Визуализация аномалий
    anomalies = df[df['anomaly'] == 1]
    plt.figure(figsize=(14, 7))
    sns.lineplot(data=df, x=df.index, y='consumption', label='Потребление')
    plt.scatter(anomalies.index, anomalies['consumption'], color='red', label='Аномалии')
    plt.title('Аномалии в потреблении')
    plt.xlabel('Дата')
    plt.ylabel('Потребление')
    plt.legend()
    plt.show()

    return df

def forecast_consumption(df):
    # Подготовка данных для Prophet
    df_prophet = df.reset_index().rename(columns={'datetime': 'ds', 'consumption': 'y'})

    # Инициализация и обучение модели
    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)

    # Прогноз на 3 дня
    future = model.make_future_dataframe(periods=72, freq='H')
    forecast = model.predict(future)

    # Визуализация прогноза
    model.plot(forecast)
    plt.title('Прогноз потребления на 3 дня')
    plt.xlabel('Дата')
    plt.ylabel('Потребление')
    plt.show()

    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def evaluate_forecast(df, forecast):
    # Объединение фактических и прогнозных данных
    merged = pd.merge(df, forecast, left_index=True, right_on='ds', how='inner')

    # Вычисление MAPE
    mape = mean_absolute_percentage_error(merged['consumption'], merged['yhat'])
    print(f'MAPE: {mape * 100:.2f}%')

    return mape


# print(load_and_preprocess('51070_for_forecast.json'))

print(datetime.now())

if __name__ == '__main__':
    df = load_and_preprocess('51070_for_forecast.json')
    df2 = visualize_and_detect_anomalies(df)
    forecast = forecast_consumption(df2)
    mape = evaluate_forecast(df, forecast)
    print(mape)