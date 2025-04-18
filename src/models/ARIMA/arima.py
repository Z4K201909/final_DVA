import numpy as np
import pandas as pd
from pmdarima import ARIMA as pmd_arima
from pmdarima import auto_arima
from statsmodels.tsa.arima.model import ARIMA as stats_arima
import matplotlib.pyplot as plt 
import warnings

class ARIMA:
    def __init__(self, data, dates, module:str='pmdarima',seasonal:bool=False, trace:bool=True, error_action:str='ignore', suppress_warnings:bool=True, 
    order:tuple=(0, 1, 0)):
        self.module = module
        self.data = data
        self.dates = dates

        if suppress_warnings:
            warnings.filterwarnings("ignore", message=".*force_all_finite.*")

        if self.module == 'pmdarima':
            self.model = pmd_arima(order=order, suppress_warnings=suppress_warnings)
        if self.module == 'auto_arima':
            self.model = auto_arima(data, start_p=0, max_p=3, start_q=0, max_q=3, d=None, stepwise=True)
            self.order = self.model.order
        elif self.module == 'statsmodels':
            self.model = stats_arima(self.data, order=order)
        else:
            print("Invalid Module provided. Did you mean 'pmdarima' or 'statsmodels'?")
    

    def fit(self, y:np.ndarray | pd.Series) -> None:
        if self.module == 'statsmodels':
            self.model.fit(y)
        else: 
            self.model.fit(y)


    def predict(self, n_periods:int=6, return_conf_int:bool=True) -> pd.DataFrame:
        if self.module == 'statsmodels':
            self.prediction = self.model.predict(steps=n_periods)
            results = {'prediction': self.prediction_dates.tolist()}
            
        else: 
            # self.model.predict(n_periods=n_periods, return_conf_int=return_conf_int)
            self.prediction, self.confidence_interval = self.model.predict(n_periods=n_periods, return_conf_int=True)
            self.prediction_dates = pd.date_range(start=self.dates[-1] + pd.DateOffset(months=1), periods=n_periods, freq='MS')

            results = {'date': self.prediction_dates.tolist(), 'prediction': self.prediction.tolist(), 'confidence_interval': self.confidence_interval.tolist()}

        result_df = pd.DataFrame(results)
        return result_df

    def plot(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.dates, self.data, label='Historical Data', color='black')
        plt.plot(self.prediction_dates, self.prediction, label='Forecast', color='green')
        plt.fill_between(self.prediction_dates, self.confidence_interval[:, 0], self.confidence_interval[:, 1], color='lightgreen', alpha=0.3)
        plt.title('ARIMA Forecast')
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.legend()
        plt.show()

if __name__ == '__main__':
    data = pd.read_csv('./data/processed/regional/Austin_TX.csv')
    data = data[data['property_type']=='All Residential']
    dates = pd.to_datetime(data['period_begin'].unique())
    x = data['median_sale_price']

    arima_model = ARIMA(x, dates)
    arima_model.fit(x)
    arima_model.predict(n_periods=48)
    arima_model.plot()