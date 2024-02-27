#import necessary libraries
from flask import Flask, render_template, request
from sklearn.linear_model import LinearRegression
import numpy as np
import mysql.connector
import atexit
import json

#start the flask app
app = Flask(__name__)

# Database Configuration
db_config = {
    'host': 'your_host',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'your_database'
}

# Connecting to Database Configuration
connection = mysql.connector.connect(**db_config)

#Jinja filter to check if any of the entries are empty
def is_not_empty(value):
    return value != ''

app.jinja_env.filters['is_not_empty'] = is_not_empty

#Jinja filter to round the estimated market price to nearest hundreds
def custom_round(value, precision=-1):
    return round(value, precision)

app.jinja_env.filters['round'] = custom_round

'''
Function to fetch data from database attempting to reconnect if not connected using try and except block
Includes query for selecting required columns based on year,make and model
Excludes models with listing price not mentioned in database
'''
def fetch_data_from_database(year, make, model):
    try:
        if not connection.is_connected():
            connection.ping(reconnect=True)

        with connection.cursor(dictionary=True) as cursor:
            query = f"SELECT vin, year, make, model, listing_mileage, listing_price, trim, dealer_city, dealer_state FROM your_tablename WHERE year={year} AND make='{make}' AND model='{model}';"
            cursor.execute(query)
            data = cursor.fetchall()
        return data

    except mysql.connector.Error as e:
        print(f"Error fetching data from database: {e}")
        return None

#Function to perform linear regression based on the data(listing_price,listing_mileage) collected for given year,make and model
def perform_linear_regression(data):
    X = np.array([item['listing_mileage'] for item in data]).reshape(-1, 1)
    y = np.array([item['listing_price'] for item in data])

    model = LinearRegression()
    model.fit(X, y)

    calculated_slope = model.coef_[0]
    calculated_intercept = model.intercept_

    return calculated_slope, calculated_intercept

# Function to read JSON objects from a file and extract a specific key
def read_json_file(file_path, key):
    try:
        with open(file_path, 'r') as file:
            # Load JSON objects from each line of the file
            json_objects = [json.loads(line) for line in file]
            # Extract the specified key from each JSON object
            values = [obj[key] for obj in json_objects]
        return values
    except Exception as e:
        print(f"Error reading {key} from file: {e}")
        return []

# Function for suggestions using data from text files
@app.route('/')
def index():
    try:
        makes = read_json_file('static/txtfiles/makes.txt', 'make')
        models = read_json_file('static/txtfiles/models.txt', 'model')
        years = read_json_file('static/txtfiles/years.txt', 'year')

        return render_template('index.html', makes=makes, models=models, year_options=years)
    except Exception as e:
        print(f"Error fetching suggestions from text files: {e}")
        return render_template('error.html', message='Error fetching suggestions from text files')

'''
Function to search and perform linear regression for searched data and given mileage, if present returns predicted price of corresponding mileage,
else returns predicted price corresponding to average mileage
'''
@app.route('/search', methods=['POST'])
def search():
    year = request.form.get('year')
    make = request.form.get('make')
    model = request.form.get('model')
    mileage_input = request.form.get('mileage')

    try:
        # Fetch data from the database based on user input
        data = fetch_data_from_database(year, make, model)
      
        # Check if no records are found
        if not data:
            return render_template('results.html', no_records=True, message='No Records Found!')

        # Perform linear regression only if there are records
        calculated_slope, calculated_intercept = perform_linear_regression(data)

        predicted_price = 0

        # Check if optional mileage input is provided and if present calculate cost using provided mileage else calculate cost for average mileage
        if mileage_input:
            try:
                mileage = float(mileage_input)
                predicted_price = calculated_slope * mileage + calculated_intercept
            except ValueError:
                return render_template('error.html', message='Invalid input for mileage')
        else:
            average_mileage = np.mean([item['listing_mileage'] for item in data])
            predicted_price = calculated_slope * average_mileage + calculated_intercept

        return render_template('results.html', data=data, predicted_price=predicted_price, year=year, make=make, model=model)
   
    # Render the results template with the data
    except mysql.connector.Error as e:
        print(f"Error in search: {e}")
        return render_template('error.html', message='Error in search')

# Close the connection
atexit.register(lambda: connection.close())

if __name__ == '__main__':
    app.run(debug=True)
