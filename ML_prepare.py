import pandas as pd
from sqlalchemy import create_engine

DB_USER = 'root'
DB_PASSWORD = '5kytr335t4ff'
DB_HOST = 'localhost'
DB_NAME = 'experiment_data'

engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')

columns_needed = [
    "id", "TheTime", "time_seconds", "time_minutes", "co2_pre", "co2_post", 
    "flow1_corrected_m3hr", "dp_cart", "t_pre", "t_post", "t_flow2",
    "mass_co2", "rate_co2_inlet", "rate_co2_mol_h", "mass_h2o", 
    "rate_h2o_in", "rate_h2o_g_h", "cumulative_mass_co2",
    "rh_inlet_abs", "rh_inlet_rh", "rh_inlet_t",
    "rh_pre_abs", "rh_pre_rh", "rh_pre_t",
    "rh_post_abs", "rh_post_rh", "rh_post_t"
]

query = f"SELECT {', '.join(columns_needed)} FROM ax500"
df = pd.read_sql(query, engine)

print(df.info())
print(df.head())
