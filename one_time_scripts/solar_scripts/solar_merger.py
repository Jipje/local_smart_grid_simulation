import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz
from sklearn.metrics import mean_squared_error

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=utc)


if __name__ == '__main__':
    # solar_power_mw_df = pd.read_csv('../../data/solar_data/solar_power/cleaned_solar_production.csv', parse_dates=[0], date_parser=date_parser)
    # solar_power_mw_df.index = pd.to_datetime(solar_power_mw_df['time'], errors='coerce', utc=True)
    # solar_power_mw_df = solar_power_mw_df.drop('time', axis=1)
    # print(solar_power_mw_df)

    # solar_forecast_df = pd.read_csv('../../data/solar_data/solar_power/cleaned_solar_forecast.csv', parse_dates=[0], date_parser=date_parser)
    # solar_forecast_df.index = pd.to_datetime(solar_forecast_df['time'], errors='coerce', utc=True)
    # solar_forecast_df = solar_forecast_df.drop('time', axis=1)
    # solar_forecast_df = solar_forecast_df.dropna()
    # solar_forecast_df.columns = ['solar_mw_forecast']
    # print(solar_forecast_df)

    radiation_df = pd.read_csv('../../data/solar_data/radiation_with_forecast/cleaned_radiation_forecast_and_values.csv', parse_dates=[0], date_parser=date_parser)
    radiation_df.index = pd.to_datetime(radiation_df['time'], errors='coerce', utc=True)
    radiation_df = radiation_df.drop('time', axis=1)
    # print(radiation_df)

    # radiation_df = radiation_df.resample('15T').pad()
    # res_df = solar_power_mw_df.merge(solar_forecast_df, how='inner', left_index=True, right_index=True)
    # res_df = res_df.merge(radiation_df, how='inner', left_index=True, right_index=True)
    # print(res_df)

    radiation_df['APE_d_1'] = abs((radiation_df['radiation'] - radiation_df['radiation_d_1']) / radiation_df['radiation'])
    radiation_df['APE_d_3'] = abs((radiation_df['radiation'] - radiation_df['radiation_d_3']) / radiation_df['radiation'])
    radiation_df['APE_d_5'] = abs((radiation_df['radiation'] - radiation_df['radiation_d_5']) / radiation_df['radiation'])
    # print(radiation_df)
    print('MAPE d-1')
    print(radiation_df['APE_d_1'].mean())
    print('MAPE d-3')
    print(radiation_df['APE_d_3'].mean())
    print('MAPE d-5')
    print(radiation_df['APE_d_5'].mean())

    print('-----------------------------------')

    radiation_df['sAPE_d_1'] = abs((radiation_df['radiation_d_1'] - radiation_df['radiation'])) / (radiation_df['radiation'] + radiation_df['radiation_d_1']) / 2
    radiation_df['sAPE_d_3'] = abs((radiation_df['radiation_d_3'] - radiation_df['radiation'])) / (radiation_df['radiation'] + radiation_df['radiation_d_3']) / 2
    radiation_df['sAPE_d_5'] = abs((radiation_df['radiation_d_5'] - radiation_df['radiation'])) / (radiation_df['radiation'] + radiation_df['radiation_d_5']) / 2
    # print(radiation_df)
    print('sMAPE d-1')
    print(radiation_df['sAPE_d_1'].mean())
    print('sMAPE d-3')
    print(radiation_df['sAPE_d_3'].mean())
    print('sMAPE d-5')
    print(radiation_df['sAPE_d_5'].mean())

    print('-----------------------------------')

    # print(radiation_df)
    print('RMSE d-1')
    print(mean_squared_error(radiation_df['radiation'], radiation_df['radiation_d_1'], squared=False))
    print('RMSE d-3')
    print(mean_squared_error(radiation_df['radiation'], radiation_df['radiation_d_3'], squared=False))
    print('RMSE d-5')
    print(mean_squared_error(radiation_df['radiation'], radiation_df['radiation_d_5'], squared=False))

    radiation_df = radiation_df.resample('15T').pad()
    start_of_set = dt.datetime(2021, 8, 10, tzinfo=utc)
    end_of_set = dt.datetime(2021, 8, 12, tzinfo=utc)
    radiation_df = radiation_df[start_of_set:end_of_set]

    plt.plot(radiation_df.index, radiation_df['radiation'], label='Measured radiation')
    plt.plot(radiation_df.index, radiation_df['radiation_d_1'], label='Radiation forecast d-1')
    plt.plot(radiation_df.index, radiation_df['radiation_d_3'], label='Radiation forecast d-3')
    plt.plot(radiation_df.index, radiation_df['radiation_d_5'], label='Radiation forecast d-5')
    plt.ylabel('Solar radiation (W/m2)')
    plt.xlabel('Time (UTC)')
    plt.title('Solar radiation measured and forecast')
    plt.legend()
    plt.show()
