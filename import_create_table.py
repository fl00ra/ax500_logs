
import pandas as pd
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '5kytr335t4ff',
    'database': 'experiment_data'
}

csv_file = 'C:\\Users\\flora\\datareview\\data\\A110_02-01_2_020125\\A110_02-01_2_020125_1438_1.csv'
data = pd.read_csv(csv_file)

columns = data.columns
dtype_mapping = {
    'int64': 'INT',
    'float64': 'FLOAT',
    'object': 'VARCHAR(255)',
    'datetime64[ns]': 'DATETIME'
}

table_name = 'ax500'
create_table_query = f"CREATE TABLE {table_name} ("
for col in columns:
    dtype = dtype_mapping[str(data[col].dtype)]
    create_table_query += f"`{col}` {dtype}, "
create_table_query = create_table_query.rstrip(', ') + ');'

try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(create_table_query)
    print(f"Table '{table_name}' created successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
