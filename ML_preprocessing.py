import pandas as pd
from sqlalchemy import create_engine
import pickle

# database connection
DB_USER = 'root'
DB_PASSWORD = '5kytr335t4ff'
DB_HOST = 'localhost'
DB_NAME = 'experiment_data'

engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

columns_needed = [
    "id", "TheTime", "co2_pre", "co2_post", 
    "flow1_corrected_m3hr", "dp_cart", "t_pre", "t_post", "t_flow2",
    "mass_co2", "rate_co2_inlet", "rate_co2_mol_h", "mass_h2o", 
    "rate_h2o_in", "rate_h2o_g_h", "cumulative_mass_co2",
    "rh_inlet_abs", "rh_inlet_rh", "rh_inlet_t",
    "rh_pre_abs", "rh_pre_rh", "rh_pre_t",
    "rh_post_abs", "rh_post_rh", "rh_post_t",
    "h2o_post_licor","h2o_pre_licor","co2_post_licor",
    "co2_pre_licor","mass_co2_licor","mass_h2o_licor"
]

# read the data from the database (only the rows with sorbent_name starting with 'PUR' or 'NGK')
query = f"""
    SELECT {', '.join(columns_needed)}
    FROM ax500
    WHERE sorbent_name LIKE 'PUR%%' OR sorbent_name LIKE 'NGK%%'
"""
data = pd.read_sql(query, engine)

# deal with the time format
data["TheTime"] = pd.to_datetime(data["TheTime"])

# fill the missing values (NaN) with the previous value
data.fillna(method='ffill', inplace=True)

# save the processed data
with open("processed_data.pkl", "wb") as f:
    pickle.dump(data, f)

print("Successfully stored in processed_data.pkl")

print(data.info())
print(data.head())
