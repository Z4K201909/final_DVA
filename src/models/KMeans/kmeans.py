import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
import warnings


def main(n_clusters:int=3,
         n_components:int=2,
         data_filepath:str='./data/processed/cleaned/metro_market_tracker_cleaned.csv',
         locations_filepath:str='./data/processed/locations/locations.csv'):
    # Load Data
    data = pd.read_csv(data_filepath)
    locations = pd.read_csv(locations_filepath)

    # Process Data
    data = data[data['property_type'] == 'All Residential']
    dates = data['period_end'].unique()
    dates.sort()
    data = data[data['period_end'] == dates[-1]]
    numeric_data = data.select_dtypes(include=['float64'])
    regions = data['region'].str.replace(' metro area', '')

    # Perform PCA
    scaled_data = StandardScaler().fit_transform(numeric_data)
    pca = PCA(n_components=n_components)
    pca.fit(scaled_data.T)
    components = pca.components_

    # Perform K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=6242)
    kmeans.fit(components.T)
    labels = kmeans.labels_

    # Output Results
    clusters = pd.DataFrame({'city':regions, 'cluster':labels})
    clusters = pd.merge(clusters, locations, on='city', how='left')
    clusters.to_csv(f'./data/processed/clusters/kmeans_{n_clusters}.csv', index=False)

if __name__ == '__main__':
    warnings.filterwarnings("ignore", message=".*KMeans is known to have a memory leak on Windows with MKL.*")

    ks = [i for i in range(3, 11)]
    for k in tqdm(ks, desc='Generating models for varying values of k'):
        main(n_clusters=k)