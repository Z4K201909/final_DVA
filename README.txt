===============================
1. Project Description
===============================
This tool provides a web dashboard that allows a user to quickly review market clusters and
ARIMA forecast plots for cities all across the US. Upon loading the dashboard, the user will
have the option to select from multiple different clustering techniques to compare how
different cities within the USA compare. Cities that are in similar clusters will have the
same corresponding colored point on the map. Additionally, the user will be able to select
any city from a dropdown list to view its historical market data as well as a prediction of
its future market value. If multiple cities are selected, then the plot will show a comparison
of historical market data for both cities. 

===============================
2. Project Setup Instructions
===============================
This project can be run locally or via the hosted web application. The simplest method is to
go to the following site and immediately view the application.

https://dva-final-project-main.onrender.com/

If there are any issues with the hosted application, the following set of instructions will
guide you through the setup and running of the application locally on your machine.

Before running these instructions, ensure the following:
- Ensure Python 3.7+ is installed
- If using conda, install Miniconda or Anaconda first

This directory contains all the files needed to run the Python application, including:
- requirements.txt      (for pip installations)
- environment.yml       (for conda environments)
- source code and scripts

Please follow ONE of the two setup methods below depending on whether you're using
Conda or pip (virtual environments).

---------------------------------------------------
Option 1: Using Conda (Recommended)
---------------------------------------------------

1. Open a terminal (macOS/Linux) or command prompt (Windows).

2. Navigate to the folder where you extracted this zip:
   Example:
   > cd path/to/unzipped-folder

3. Create a new conda environment from the environment.yml file:
   > conda env create -f environment.yml

4. Activate the environment:
   > conda activate DVA

5. Run the application:
   > python main.py

---------------------------------------------------
Option 2: Using pip and virtualenv
---------------------------------------------------

1. Open a terminal (macOS/Linux) or command prompt (Windows).

2. Navigate to the folder where you extracted this zip:
   Example:
   > cd path/to/unzipped-folder

3. (Optional) Create a virtual environment:
   > python -m venv venv

4. If you created a virtual environment, activate it:
   On macOS/Linux:
   > source venv/bin/activate

   On Windows:
   > venv\Scripts\activate

5. Install required packages:
   > pip install -r requirements.txt


===============================
3. Project Details
===============================
The project is purely created in Python to minimize the number of tools and languages needed
to develop the dashboard with the results and data stored as CSV files for quick access by 
the dashboard. The project is broken out into 3 main subsections, data processing, model
building, and dashboard configuration. 


---------------------------------------------------
3.1 Data Processing
---------------------------------------------------
The data processing code is stored in the src\data directory. In this directory, there are 3 
python files, data_cleaner.py, data_splitter.py, and locations.py. 

---------------------------------------------------
3.1.1 Data Processing - data_cleaner.py
---------------------------------------------------
The data_cleaner.py file contains a DataCleaner class that is used for processing the raw data 
from Redfin with two primary methods, 'clean_data' and 'save_data'. The 'clean_data' method 
cleans the data by performing the following sequence of events. 

1. Create a copy of the provided pd.DataFrame

2. Sort the data by 'period_begin'

3. Remove any columns that do not provide added value to the dataset
   - This is done by looking at which columns only have a single unique
     value in the entire DataFrame and adding that column to a list of columns
     to drop. 

4. Group data by the 'region' and 'property_type'.

5. Replace 'na' values by first using a forward fill and then backward fill. 
   - This is a standard process for how stock data is cleaned without accidentally
     causing leakage of info from future data into past data.
 
6. Once all 'na' values are filled, any remaining 'na' values are dropped. 
    - This is done because the only remaining 'na' values are those where all the values
      in a group are 'na' and therefore are not useful for this project. 

The 'save_data' method simply wraps a pandas.DataFrame.to_csv() function with 
some prefilled information for where to save data and how to name the file

To clean the raw data, all the user has to do is run the command 'python src\data\data_cleaner.py' 
from the project's root directory. If new data needs to be cleaned or a different file needs to be 
cleaned, then all the user has to do is edit the file path variable towards the end of the python 
file below the 'if __name__ == "__main__":' line. 

---------------------------------------------------
3.1.2 Data Processing - data_splitter.py
---------------------------------------------------
The data_splitter.py file contains a DataSplitter class that is used for splitting the
processed data from the data_cleaner.py file into individual files for each city/metro area. 
The intent for this is to break large combined data file into small and easier to process 
chunks. This also allows for all the model functions to written in a more general format without
any specific details about the cities. This is achieved by simply finding all the unique
values for the 'region' column in the processed data file and then for each unique value
filter the initial data frame by the region value and saving the results to a new csv file. 

To split data that has already been cleaned, all the user has to do is run the command 
'python src\data\data_splitter.py' from the project's root directory.

---------------------------------------------------
3.1.3 Data Processing - locations.py
---------------------------------------------------
The locations.py file serves as a programmatic way to generate all the necessary latitude
and longitude coordinates for each city in the data set, so that it can be referenced while
plotting the cluster data. This is done by taking the all the unique regional names from the
cleaned data set and then looping through the list of cities and then using the geopy module
to get each location's longitude and latitude. After all the locations are processed, the
results are stored in a CSV file for later reference by the cluster models to append to their 
data sets. 

To generate a new list of locations, the user needs to run the command 'python src\data\locations.py'
from the project's root directory. 



---------------------------------------------------
3.2 Model Building
---------------------------------------------------
There are several types of models that need to be built to support the dashboard's functionality. 
There are the ARIMA, KMeans, and DTW models with each model having its own subdirectory and
corresponding python file. The goal is to generate a CSV file for each model so that the dashboard
can simply load the results rather than having to build and generate models in real time. 
Additionally, there is a model_builder.py file that's used for generating the many combinations of
ARIMA models necessary for each city, but was written with the flexibility to be used to generate
more models for each city if more model types were desired in the future. 

---------------------------------------------------
3.2.1 Model Building - Clustering
---------------------------------------------------
There are two clustering models that were created for the dashboard. Each model has it's own
python file (dtw.py and kmeans.py) and can be run in a similar method. All the user has to do 
is run the command 'python src\models\Kmeans\kmeans.py' or 'python src\models\DTW\dtw.py' and 
it will generate a range of clustering models for the dashboard to use. However, after model 
evaluation was performed, only the best model from each method was selected to be used with 
the dashboard. 

---------------------------------------------------
3.2.2 Model Building - ARIMA
---------------------------------------------------
The arima.py file contains a class for generating ARIMA models. It's designed in a way that 
allows for multiple different types of ARIMA models to be built using different ARIMA modules. 
The reason for this is that it wasn't clear which module would work the best for building
the dashboard and some modules have different ARIMA functions to choose from. By allowing
a string value to select which module to use, it provided a lot of flexibility during the 
development cycle. Ultimately, the dashboard ended up using several ARIMA functions to provide
the final result to the end user. 

If the user wants to just generate all the ARIMA models for all the different cities in the
cleaned data set, they simply have to use the command 'python src\models\ARIMA\arima.py'.
However, if they want to generate only the recommended ARIMA models for each city, then they 
can run the command 'python src\models\ARIMA\arima.py --optimize' or 
'python src\models\ARIMA\arima.py -o'. 



---------------------------------------------------
3.3 Dashboard Configuration
---------------------------------------------------
The dashboard configuration is all contained withing the main.py file. This file serves as the
main file for running the entire application as well. In this file, there are multiple functions
to load all the models and data used to set up the Dash application for the dashboard.

To run the application, all the user needs to do is run 'python main.py' from the project's
root directory. 
