# AX500: Experimental Data Processing & Machine Learning

## Overview
This project is designed to handle experimental data processing, store it in a MySQL database, and apply machine learning models for anomaly detection. The repository is structured into two main categories:

1. **Import Scripts (`import_*.py`)** - Scripts related to data extraction, preprocessing, and database insertion.
2. **Machine Learning Scripts (`ML_*.py`)** - Scripts used for training and applying ML models for anomaly detection.

---
## **Installation & Setup**
### **1. Clone Repository**
```sh
git clone <your-repository-url>
cd <your-repository>
```

### **2. Install Dependencies**
Ensure you have Python and the required dependencies installed. If you encounter issues with missing dependencies, install them manually:
```sh
pip install pandas mysql-connector-python SQLAlchemy google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client cryptography
```

### **3. Database Deployment**
The database is currently only deployed on a local machine. Upon handing over the project, the database will be exported as an `.sql` file and stored in this repository. To set up the database on a new machine:

1. Install MySQL Server.
2. Clone this repository and navigate to the directory containing the `.sql` file.
3. Create a new database in MySQL:
   ```sql
   CREATE DATABASE experiment_data;
   ```
4. Import the existing database dump:
   ```sh
   mysql -u root -p experiment_data < experiment_data_dump.sql
   ```
   (Replace `experiment_data_dump.sql` with the actual filename.)

The latest AX500 database dump is available for download:

[Download ax500_database_dump.zip](https://github.com/fl00ra/ax500_logs/releases/download/dump-2024-02-24/ax500_database_dump.zip)**


Since the new setup is independent of the original machine, database credentials (`DB_USER`, `DB_PASSWORD`) in Python scripts can be removed or adjusted accordingly.

---
## **Script Descriptions**

### **Data Import Scripts (`import_*.py`)**
These scripts manage data retrieval, processing, and insertion into the MySQL database.

- **`import_check_totalrecord.py`** - Scans the logs directory, validates files, and counts total records.
- **`import_create_table.py`** - Creates a MySQL table based on the structure of a sample CSV file.
- **`import_data_api.py`** - Automatically uploads and updates new experimental data from Google Drive to the database. Since this involves API authentication, the credentials file (`.json`) is **not included** in the repository for security reasons. To set up API access:
  1. Create a Google Cloud Service Account.
  2. Enable Google Drive API.
  3. Download the credentials JSON file and place it in the repository folder.
  4. Update the script to reference your new credentials file.
- **`import_data_ax500_update.py`** - Reads CSV/XLSX files, preprocesses data, and inserts it into the `ax500` table.

### **Machine Learning Scripts (`ML_*.py`)**
These scripts apply machine learning models to detect anomalies in experimental data.

- **`ML_preprocessing.py`** - Extracts required columns from MySQL, processes missing values, and prepares data for modeling.
- 

---
## **Usage Instructions**

### **1. Import Data into MySQL**
Run the following command to import and update data:
```sh
python import_data_ax500_update.py
```
This script will scan the `logs` folder, clean the data, and insert it into the MySQL `ax500` table.

### **2. Automatically Upload & Update Experimental Data**
Run the following command to fetch new experimental data from Google Drive and update the database:
```sh
python import_data_api.py
```
Since this script requires Google API access, ensure your credentials JSON file is correctly set up.

### **3. Train Machine Learning Model**
Once data is imported, you can run:
```sh
python ML_prepare.py
```
This script fetches data from the MySQL database, processes missing values, and prepares it for anomaly detection.

---
## **Troubleshooting**
- **MySQL Connection Issues:** If you face authentication errors, check if MySQL is correctly installed and the database is imported.
- **Google API Authentication Issues:** Ensure your credentials JSON file is in place and the service account has access to the Google Drive folder.
- **Missing Dependencies:** Ensure all required packages are installed manually using `pip install` as mentioned above.
- **File Format Errors:** Make sure your CSV/XLSX files are correctly formatted before importing.

---
## **Contributing**
Feel free to fork this repository and submit pull requests for improvements, especially in ML model refinement or database optimization.

---
## **License**
This project is for internal use and follows company data policies.

