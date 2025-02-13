import pickle
import pandas as pd
import matplotlib.pyplot as plt

# read the model results
with open("model_results.pkl", "rb") as f:
    data = pickle.load(f)

# only keep the anomalies
anomalies = data[data["anomaly"] == -1]

# time series visualization (CO2 inlet and outlet concentrations)
plt.figure(figsize=(12, 6))
plt.plot(data["TheTime"], data["co2_pre"], label="CO₂ Pre (normal)", alpha=0.5)
plt.plot(data["TheTime"], data["co2_post"], label="CO₂ Post (normal)", alpha=0.5)
plt.scatter(anomalies["TheTime"], anomalies["co2_pre"], color="red", label="abnormal", marker="x")
plt.scatter(anomalies["TheTime"], anomalies["co2_post"], color="red", marker="x")
plt.xlabel("TheTime")
plt.ylabel("CO₂ Concentration")
plt.title("Abnormal detection of CO2 inlet and outlet concentrations")
plt.legend()
plt.xticks(rotation=45)
plt.show()

# flow vs CO2 change (scatter plot)
plt.figure(figsize=(8, 6))
plt.scatter(data["co2_pre"], data["flow1_corrected_m3hr"], label="normal", alpha=0.5)
plt.scatter(anomalies["co2_pre"], anomalies["flow1_corrected_m3hr"], color="red", label="abnormal", marker="x")
plt.xlabel("CO₂ Pre")
plt.ylabel("flow (m³/hr)")
plt.title("flow vs CO₂ inlet concentration anomaly detection")
plt.legend()
plt.show()

# anomaly score distribution
plt.figure(figsize=(8, 4))
plt.hist(data["anomaly_score"], bins=50, color="blue", alpha=0.7, label="all data")
plt.hist(anomalies["anomaly_score"], bins=50, color="red", alpha=0.7, label="anomalies")
plt.xlabel("Isolation Forest anomaly score")
plt.ylabel("Frequency")
plt.title("Anomaly score distribution")
plt.legend()
plt.show()
