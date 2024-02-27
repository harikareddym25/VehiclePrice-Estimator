-- The data flow describing how the input data gets translated into the database

-- Create or use the database 'your_database'
CREATE DATABASE IF NOT EXISTS your_database;
USE your_database;

-- Create the table 'your_tablename' with specified columns as per the historical vehicle data 
CREATE TABLE IF NOT EXISTS your_tablename(
    vin VARCHAR(50),
    year INT,
    make VARCHAR(255),
    model VARCHAR(255),
    trim VARCHAR(255),
    dealer_name VARCHAR(255),
    dealer_street VARCHAR(255),
    dealer_city VARCHAR(255),
    dealer_state VARCHAR(255),
    dealer_zip VARCHAR(20),
    listing_price DECIMAL(15, 2),
    listing_mileage INT,
    used VARCHAR(5),
    certified VARCHAR(5),
    style VARCHAR(255),
    driven_wheels VARCHAR(50),
    engine VARCHAR(255),
    fuel_type VARCHAR(50),
    exterior_color VARCHAR(255),
    interior_color VARCHAR(255),
    seller_website VARCHAR(255),
    first_seen_date DATE,
    last_seen_date DATE,
    dealer_vdp_last_seen_date DATE,
    listing_status VARCHAR(50)
);

-- Load data from the vehicle data into the table
LOAD DATA LOCAL INFILE 'path/to/vehicle data txt file'
INTO TABLE your_tablename
FIELDS TERMINATED BY '|'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(vin, year, make, model, trim, dealer_name, dealer_street, dealer_city, dealer_state, dealer_zip, @listing_price, @listing_mileage, used, certified, style, driven_wheels, engine, fuel_type, exterior_color, interior_color, seller_website, first_seen_date, last_seen_date, dealer_vdp_last_seen_date, listing_status)
SET listing_price = NULLIF(@listing_price, ''),
    listing_mileage = NULLIF(@listing_mileage, '');

-- Delete rows with NULL or 0 values in specific columns
DELETE FROM your_tablename
WHERE listing_mileage IS NULL
   OR listing_price IS NULL
   OR listing_price = 0;

-- Extract distinct years and save to a text file for suggestions purpose
SELECT DISTINCT CONCAT('{"year": ', year, '}') AS year_object
FROM your_database.your_tablename
INTO OUTFILE 'path/to/your/years.txt file'
LINES TERMINATED BY '\n';

-- Extract distinct makes and save to a text file for suggestions purpose
SELECT DISTINCT CONCAT('{"make": ', make, '}') AS make_object
FROM your_database.your_tablename
INTO OUTFILE 'path/to/your/makes.txt file'
LINES TERMINATED BY '\n';

-- Extract distinct models and save to a text file for suggestions purpose
SELECT DISTINCT CONCAT('{"model": ', model, '}') AS model_object
FROM your_database.your_tablename
INTO OUTFILE 'path/to/your/models.txt file'
LINES TERMINATED BY '\n';
