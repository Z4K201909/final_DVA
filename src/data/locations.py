from time import sleep
from geopy.geocoders import Nominatim
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import numpy as np

def main(n_clusters:int=3, n_components:int=2, filepath:str='./data/processed/cleaned/metro_market_tracker_cleaned.csv'):
    # Load Data
    data = pd.read_csv(filepath)

    # Process Data
    data = data[data['property_type'] == 'All Residential']
    regions = data['region'].str.replace(' metro area', '').unique()

    geolocator = Nominatim(user_agent="marketLocations")

    latitudes = []
    longitudes = []

    for city in tqdm(regions, desc='Pulling lat/lon data...'):
        geo = geolocator.geocode(city, timeout=10)
        latitudes.append(geo.latitude)
        longitudes.append(geo.longitude)
        if np.random.uniform() < 0.5:
            sleep(2)

    locations = pd.DataFrame({'city':regions,'latitude': latitudes, 'longitude': longitudes})
    locations.to_csv('./data/processed/locations/locations.csv', index=False)

if __name__ == '__main__':
    main()