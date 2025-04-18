'''
data_splitter.py

This module contains a class that handles the splitting of Redfin market data.

Classes:
    DataCleaner: a class to handle the splitting of Redfin market data.
'''

from halo import Halo
import os
import pandas as pd
from time import time
from tqdm import tqdm



class DataSplitter:
    '''
    A class to handle the splitting of Redfin market data.

    Attributes:
        None

    Methods:
        split_data: Splits a provided Pandas DataFrame by a specified column's values and save to a CSV file
    '''

    def __init__(self):
        pass

    def split_data(self, data: pd.DataFrame, column: str, filepath: str = './data/processed/', overwrite_files:bool=False) -> None:
        '''
        Splits a provided Pandas DataFrame by a specified column's values.

        Args:
            data (pd.DataFrame): The data that needs to be cleaned
            column (str): The name of the column that needs to be split
            filepath (str): The path to the CSV file

        Returns:
            data_cleaned (pd.DataFrame): A cleaned Pandas DataFrame
        '''
        data_copy = data.copy()

        if column not in data_copy.columns:
            print('Error: Column not found')
            return None
        elif not os.path.isdir(filepath):
            print(f"Directory '{filepath}' not found")
            response = input("Would you like to create this directory? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                os.mkdir(filepath)
            else:
                print('Aborting. No such directory.')
                return None
        else:
            columns_values = data_copy[column].unique()
            failures = []
            for column_value in tqdm(columns_values, desc='Saving split data'):
                split_data = data_copy[data_copy[column] == column_value]
                filename = column_value.replace('/', '').replace(' ', '').replace(',', '_')
                if os.path.exists(os.path.join(filepath, filename)):
                    if overwrite_files:
                        try:
                            split_data.to_csv(f'{filepath}/{filename}.csv')
                        except:
                            failures.append(column_value)
                else:
                    try:
                        split_data.to_csv(f'{filepath}/{filename}.csv')
                    except:
                        failures.append(column_value)

            failure_count = len(failures)

            if failure_count > 0:
                print(f'Failed to save {failure_count} cities.')
                if failure_count < 15:
                    print(failures)
                print("Failures can be found at './resources/logs/data_splitting_failures.txt'")
                with open('./resources/logs/data_splitting_failures.txt', 'w') as failures_file:
                    for failure in failures:
                        failures_file.write(f"{failure}\n")


if __name__ == '__main__':
    '''
    If run as main, then this file will execute the code below to split the specified data.
    '''
    start = time()

    # Load Data
    with Halo(text='Loading data...', spinner='dots'):
        data = pd.read_csv('./data/processed/cleaned/metro_market_tracker_cleaned.csv')
    print(f'Data loaded ({time() - start:.2f}s)')

    # Clean Data
    splitter = DataSplitter()
    filepath = './data/processed/regional'
    splitter.split_data(data, column='region', filepath=filepath)
    print(f'Data split and saved ({time() - start:.2f}s)')
    print(f"Data stored at '{filepath}'.")