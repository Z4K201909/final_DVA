'''
data_cleaner.py

This module contains a class that handles the cleaning of Redfin market data.

Classes:
    DataCleaner: a class to handle the cleaning of Redfin market data.
'''

from datetime import datetime
from halo import Halo
import pandas as pd
from time import time


class DataCleaner:
    '''
    A class to handle the cleaning of Redfin market data.

    Attributes:
        None

    Methods:
        clean_data: Cleans a provided Pandas DataFrame
        save_data: Saves the cleaned data to a CSV file
    '''

    def __init__(self):
        pass


    def clean_data(self, data:pd.DataFrame) -> pd.DataFrame:
        '''
        Cleans a provided DataFrame.

        Args:
            data (pd.DataFrame): The data that needs to be cleaned

        Returns:
            data_cleaned (pd.DataFrame): A cleaned Pandas DataFrame
        '''
        data_copy = data.copy()

        # Sort Data by period_begin
        data_copy.sort_values(by='period_begin', ascending=True, inplace=True)

        # Clean Up Columns with no added value
        columns_to_drop = []
        for column in data_copy.columns:
            unique_vals = data_copy[column].unique()
            if len(unique_vals) <= 1:
                columns_to_drop.append(column)
        data_reduced = data_copy.drop(columns_to_drop, axis=1)

        # Clean up na values
        data_grouped = data_reduced.groupby(['region', 'property_type'])
        data_cleaned = data_grouped.apply(lambda x: x.ffill().bfill().dropna(), include_groups=True).reset_index(drop=True)

        return data_cleaned


    def save_data(self, data:pd.DataFrame, filepath:str='./data/processed/cleaned',
                  filename=f'data_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}') -> None:
        '''
        Saves a DataFrame to a CSV file

        Args:
            data (pd.DataFrame): The data that needs to be saved
            filepath (str): The directory where the data will be saved
            filename (str): Name of the file

        Returns:
            None
        '''

        data.to_csv(f'{filepath}/{filename}.csv')


if __name__ == '__main__':
    '''
    If run as main, then this file will execute the code below to clean the specified data.
    
    Cleaning and saving data will each take 7-10 mins to run on the city_market_tracker.tsv file. 
    '''

    # Load Data
    start = time()
    with Halo(text='Loading data...', spinner='dots'):
        data = pd.read_csv('./data/raw/redfin_metro_market_tracker.tsv', sep='\t')
    print(f'Data Loaded ({time()-start:.2f}s)')

    # Clean Data
    start = time()
    cleaner = DataCleaner()
    with Halo(text='Cleaning data...', spinner='dots'):
        clean_data = cleaner.clean_data(data)
    print(f'Data Cleaned ({time() - start:.2f}s)')

    # Save Data
    start = time()
    with Halo(text='Saving data...', spinner='dots'):
        cleaner.save_data(clean_data, filename='metro_market_tracker_cleaned')
    print(f'Data Saved ({time() - start:.2f}s)')

