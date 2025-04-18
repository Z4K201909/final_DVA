import os
import pandas as pd
import numpy as np

from tslearn.utils import to_time_series_dataset
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMeanVariance, TimeSeriesScalerMinMax

def main(data_filepath:str = './data/processed/regional',
          locations_filepath:str = './data/processed/locations/locations.csv'):
    
    city_data = load_data(data_filepath)

    all_data = []
    time_series_yoy_data = []
    time_series_data_raw = []
    city_label = []
    for city, df in city_data.items():
        df["city"] = city  # Keep track of city
        all_data.append(df)
        if df['median_sale_price'].notna().any():
            city_label.append(city)
            time_series_yoy_data.append(df['median_sale_price_yoy'])
            time_series_data_raw.append(df['median_sale_price'])

    housing_df = pd.concat(all_data)
    time_series_yoy_dataset = to_time_series_dataset(time_series_yoy_data)

    scaler = TimeSeriesScalerMinMax()
    time_series_dataset_scaled = scaler.fit_transform(time_series_yoy_dataset)

    k_values = range(2, 10)  # Typically start at 2 and go up to 10 or more
    # Store inertia values
    inertia_values = []
    label_df = pd.DataFrame()
    label_df['city'] = city_label

    for k in k_values:
        model = TimeSeriesKMeans(n_clusters=k, metric="dtw", random_state=0)
        labels = model.fit_predict(time_series_dataset_scaled)
        inertia_values.append(model.inertia_)
        label_df[f"{k}"] = labels
        labels = model.fit_predict(time_series_dataset_scaled)

    
    label_df['city'] = label_df['city'].apply(format_single_filename)
    label_df['city'] = city_label
    location_df = pd.read_csv(locations_filepath)

    for k in k_values:
        df = location_df.copy()
        df.insert(1,'cluster',label_df[f"{k}"])
        df.to_csv(f"./data/processed/clusters/DTW_{k}.csv", index=False)

    return

# Helper Functions
def load_data(data_dir):
    all_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    city_data = {}

    for file in all_files:
        city_name = file.replace("_metro.csv", "")
        df = pd.read_csv(os.path.join(data_dir, file), parse_dates=["period_begin"])
        df = df[df["property_type"] == "Single Family Residential"]  # Focus on single-family homes
        city_data[city_name] = df
    return city_data

#Create time Lagged features from select features
def create_lagged_features(df, lags=3):
    for lag in range(1, lags + 1):
        df[f"median_sale_price_lag{lag}"] = df["median_sale_price"].shift(lag)
        df[f"inventory_lag{lag}"] = df["inventory"].shift(lag)
        df[f"sold_above_list_lag{lag}"] = df["sold_above_list"].shift(lag)
    return df.dropna()

def format_single_filename(filename):
    base = filename.replace('_metroarea.csv', '').replace('metroarea.csv', '').replace('.csv', '')
    if '_' in base:
        parts = base.rsplit('_', 1)
        city = parts[0].replace('_', ' ')
        state = parts[1]
        return f"{city}, {state}"
    else:
        return base

if __name__ == '__main__':
    main()