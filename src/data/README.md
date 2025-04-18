# Data
Currently, there is only a single file in the data module

## data_cleaner.py
The data_cleaner.py file contains a single  (```DataCleaner```) 
that, as the name applies, is used to clean data.

### ```DataCleaner```
```DataCleaner``` contains two methods, the first is ```clean_data()```.
This method cleans the data by performing the following sequence of 
events. 
1. Create a copy of the provided pd.DataFrame
2. Sort the data by 'period_begin'
3. Remove any columns that do not provide added value to the dataset
   1. This is done by looking at which columns only have a single unique
   value in the entire DataFrame and adding that column to a list of columns
   to drop. 
4. Group data by the 'region' and 'property_type'.
5. Replace 'na' values by first using a forward fill and then backward fill. 
   1. This is a standard process for how stock data is cleaned without accidentally
   causing leakage of info from future data into past data. 
6. Once all 'na' values are filled, any remaining 'na' values are dropped. 
    1. This is done because the only remaining 'na' values are those where all the values
   in a group are 'na' and therefore are not useful for this project. 

The second method contained in this class is the ```save_data()``` method. 
This function simply wraps a ```pandas.DataFrame.to_csv()``` function with 
some prefilled information for where to save data and how to name the file. 
