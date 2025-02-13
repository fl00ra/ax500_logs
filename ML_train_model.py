import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# read the processed data
with open("processed_data.pkl", "rb") as f:
    data = pickle.load(f)

# select numeric columns (excluding id and TheTime)
numeric_cols = [col for col in data.columns if col not in ["id", "TheTime"]]

# data scaling
scaler = StandardScaler()
data_scaled = scaler.fit_transform(data[numeric_cols])

# train the isolation forest model
model = IsolationForest(n_estimators=100, contamination='auto', random_state=42)
model.fit(data_scaled)

# predict anomalies (1 for normal, -1 for anomaly)
data["anomaly"] = model.predict(data_scaled)

# get the anomaly score (the lower, the more abnormal)
data["anomaly_score"] = model.decision_function(data_scaled)

# filter out the anomalies
anomalies = data[data["anomaly"] == -1]

# get the top 5% anomalies
top_anomalies = anomalies.nsmallest(int(len(data) * 0.05), "anomaly_score")

# export the anomalies data
# data.to_excel("anomalies data.xlsx", index=False)
anomalies.to_excel("anomalies_data.xlsx", index=False)

# save the model results
with open("model_results.pkl", "wb") as f:
    pickle.dump(data, f)

print("Successfully stored in anomalies data.xlsx")







