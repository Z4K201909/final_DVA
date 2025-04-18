import sys
from halo import Halo
import os
import pandas as pd
from ARIMA import arima

class ModelBuilder:
    def __init__(self, model='arima', orders:list[tuple]=[(1,1,1)], n_periods=24) -> None:
        self.model = model
        self.orders = orders
        self.n_periods = n_periods

    def build_models(self, data_directory:str='./data/processed/regional', model_directory:str='./data/processed/arima', feature:str='median_sale_price'):
        feature_directory = os.path.join(model_directory, feature)
        if not os.path.exists(feature_directory):
            print(f'Creating models directory ({feature_directory})')
            os.makedirs(feature_directory)

        for root, dirs, files in os.walk(data_directory):
            for file in files:
                if file.endswith('.csv'):
                    file_name = file.split('.')[0]
                    data = pd.read_csv(os.path.join(root, file))
                    data = data[data['property_type'] == 'All Residential']
                    dates = pd.to_datetime(data['period_begin'].unique())
                    feature_data = data[feature]
                    if self.model == 'arima':
                        for order in self.orders:
                            try:
                                arima_model = arima.ARIMA(data=feature_data, dates=dates, order=order)
                                arima_model.fit(feature_data)
                                prediction = arima_model.predict(n_periods=self.n_periods)
                                prediction.to_csv(f'{feature_directory}/{file_name}_{feature}_{order}.csv', index=False)
                            except Exception as e:
                                print(f'Issue with processing {file} with order: {order}')
                                print(f'Error: {e}')
                    elif self.model == 'auto_arima':
                        try:
                            arima_model = arima.ARIMA(data=feature_data, dates=dates, module='auto_arima')
                            order = arima_model.order
                            prediction = arima_model.predict(n_periods=self.n_periods)
                            prediction.to_csv(f'{feature_directory}/{file_name}_{feature}_{order}_recommended.csv', index=False)
                        except Exception as e:
                            print(f'Issue with processing {file}')
                            print(f'Error: {e}')
                    else:
                        print('Invalid model selected.')
                        break




if __name__ == '__main__':
    columns_of_interest = [
        'median_sale_price',
        'median_list_price',
        'median_ppsf',
        'median_list_ppsf'
    ]

    if sys.argv[1] == '--optimize' or sys.argv[1] == '-o':
        print('Finding optimal arima_models...')
        # Build Models for all possible orders
        builder = ModelBuilder(model='auto_arima')
        for column in columns_of_interest:
            with Halo(text=f'Building models for {column}...', spinner='dots'):
                builder.build_models(data_directory='./data/processed/regional',
                                     model_directory='./data/processed/arima', feature=column)
    else:
        P = 4
        D = 4
        Q = 4

        orders = [(p, d, q) for p in range(P) for d in range(D) for q in range(Q)]

        # Build Models for all possible orders
        builder = ModelBuilder(orders=orders)
        for column in columns_of_interest:
            with Halo(text=f'Building models for {column}...', spinner='dots'):
                builder.build_models(data_directory='./data/processed/regional', model_directory='./data/processed/arima', feature=column)
