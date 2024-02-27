=== README ===

This folder contains text files that are used for suggestions in the Vehicle Price Estimator application.

- `years.txt`: Contains distinct years retrieved from the database in JSON object format.
- `makes.txt`: Contains distinct makes retrieved from the database in JSON object format.
- `models.txt`: Contains distinct models retrieved from the database in JSON object format.

The data in these files is represented as JSON objects for easy parsing and integration into the application.

Example JSON object format:
- For `years.txt`: {"year": 2022}
- For `makes.txt`: {"make": "Toyota"}
- For `models.txt`: {"model": "Camry"}

These files are generated based on the data stored in the corresponding columns of the database table.
