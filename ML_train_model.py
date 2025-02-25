import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

with open("processed_data.pkl", "rb") as f:
    data = pickle.load(f)

features_used = [
    "co2_diff",  # CO₂ removal efficiency
    "t_diff",  # Temperature change
    "rate_h2o_diff",  # Water input-output rate difference
    "rh_inlet_diff", "rh_pre_diff", "rh_post_diff",  # Humidity differences
    "h2o_licor_diff", "co2_licor_diff",  # Licor-measured H₂O & CO₂ changes
    "flow1_corrected_m3hr", "dp_cart",  # Flow rate & pressure
    "mass_co2", "rate_co2_inlet", "rate_co2_mol_h", "mass_h2o",  # Other stable process variables
    "cumulative_mass_co2", "mass_co2_licor", "mass_h2o_licor"
]

# Data scaling
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data[features_used])

# Train the Isolation Forest model
#model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)  # Set contamination to 5%
model = IsolationForest(n_estimators=100, contamination=0.005, random_state=42) 
model.fit(data_scaled)

# Predict anomalies (1 for normal, -1 for anomaly)
data["anomaly"] = model.predict(data_scaled)

# Get the anomaly score (the lower, the more abnormal)
data["anomaly_score"] = model.decision_function(data_scaled)

# Filter out the anomalies
anomalies = data[data["anomaly"] == -1]

# Get the top 5% most abnormal anomalies
top_anomalies = anomalies.nsmallest(int(len(anomalies) * 0.05), "anomaly_score")

# Export anomalies data
anomalies.to_excel("anomalies_data.xlsx", index=False)

# Save the model results for visualization
with open("model_results.pkl", "wb") as f:
    pickle.dump(data, f)

print("Successfully stored anomalies in anomalies_data.xlsx")
