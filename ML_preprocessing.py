import pandas as pd
from sqlalchemy import create_engine
import pickle

# Database connection
DB_USER = 'root'
DB_PASSWORD = '5kytr335t4ff'
DB_HOST = 'localhost'
DB_NAME = 'experiment_data'

engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

# Required columns (from database)
columns_needed = [
    "id", "TheTime", "co2_pre", "co2_post",
    "flow1_corrected_m3hr", "dp_cart", "t_pre", "t_post", "t_flow2",
    "mass_co2", "rate_co2_inlet", "rate_co2_mol_h", "mass_h2o",
    "rate_h2o_in", "rate_h2o_g_h", "cumulative_mass_co2",
    "rh_inlet_abs", "rh_inlet_rh", "rh_inlet_t",
    "rh_pre_abs", "rh_pre_rh", "rh_pre_t",
    "rh_post_abs", "rh_post_rh", "rh_post_t",
    "h2o_post_licor", "h2o_pre_licor", "co2_post_licor",
    "co2_pre_licor", "mass_co2_licor", "mass_h2o_licor"
]

# Read data from database
query = f"SELECT {', '.join(columns_needed)} FROM ax500 WHERE sorbent_name LIKE 'PUR%%' OR sorbent_name LIKE 'NGK%%'"
data = pd.read_sql(query, engine)

# Convert time column to datetime
data["TheTime"] = pd.to_datetime(data["TheTime"])

# Fill missing values with forward fill and backward fill
data.ffill(inplace=True)  
data.bfill(inplace=True)  

# Compute new features (post - pre differences)
data["co2_diff"] = data["co2_post"] - data["co2_pre"]
data["t_diff"] = data["t_post"] - data["t_pre"]
data["rate_h2o_diff"] = data["rate_h2o_g_h"] - data["rate_h2o_in"]
data["rh_inlet_diff"] = data["rh_inlet_rh"] - data["rh_inlet_abs"]
data["rh_pre_diff"] = data["rh_pre_rh"] - data["rh_pre_abs"]
data["rh_post_diff"] = data["rh_post_rh"] - data["rh_post_abs"]
data["h2o_licor_diff"] = data["h2o_post_licor"] - data["h2o_pre_licor"]
data["co2_licor_diff"] = data["co2_post_licor"] - data["co2_pre_licor"]

# can use clip to limit the range of anormal values
# data["co2_diff"] = data["co2_diff"].clip(-800, 800)
# data["t_diff"] = data["t_diff"].clip(-50, 50)
# data["rate_h2o_diff"] = data["rate_h2o_diff"].clip(-10, 10)
# ...

data.ffill(inplace=True)  
data.bfill(inplace=True)
data.fillna(0, inplace=True)


features_to_check = [
    "co2_diff", "t_diff", "rate_h2o_diff", "rh_inlet_diff", "rh_pre_diff",
    "rh_post_diff", "h2o_licor_diff", "co2_licor_diff", "flow1_corrected_m3hr",
    "dp_cart", "mass_co2", "rate_co2_inlet", "rate_co2_mol_h", "mass_h2o",
    "cumulative_mass_co2"
]

for feature in features_to_check:
    Q1 = data[feature].quantile(0.25)
    Q3 = data[feature].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    data = data[(data[feature] >= lower_bound) & (data[feature] <= upper_bound)]


# Save processed data
with open("processed_data.pkl", "wb") as f:
    pickle.dump(data, f)

print("Processed data stored in processed_data.pkl")
