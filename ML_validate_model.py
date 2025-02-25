import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import LocalOutlierFactor
import seaborn as sns


# Load model results
with open("model_results.pkl", "rb") as f:
    data = pickle.load(f)

# Only keep anomalies
anomalies = data[data["anomaly"] == -1]

#sample_size = min(2000, len(data))  # Limit the number of points to plot
#data_sampled = data.sample(sample_size, random_state=42)
data_sampled = data.sample(frac=0.05, random_state=42)
anomalies_sampled = anomalies.sample(min(500, len(anomalies)), random_state=42)  # Limit the number of anomalies to plot


plt.figure(figsize=(8, 4))
sns.boxplot(data["co2_diff"])
plt.title("Boxplot of CO₂ Difference (Post - Pre)")
plt.show()

plt.figure(figsize=(8, 4))
plt.hist(data["anomaly_score"], bins=50, color="blue", alpha=0.7, label="all data")
plt.hist(anomalies["anomaly_score"], bins=30, color="red", alpha=0.7, label="anomalies")
plt.xlabel("Isolation Forest Anomaly Score")
plt.ylabel("Frequency")
plt.title("Anomaly Score Distribution")
plt.legend()
plt.show()

# use LOF to compare with Isolation Forest

features_used = ["co2_diff", "t_diff", "rate_h2o_diff", "rh_post_diff", "h2o_licor_diff"]

# # compute LOF
# lof = LocalOutlierFactor(n_neighbors=20, contamination=0.05)
# lof_preds = lof.fit_predict(data[features_used])

# # compute LF & LOF overlap
# overlap = sum((lof_preds == -1) & (data["anomaly"] == -1)) / sum(data["anomaly"] == -1)
# print(f"Overlap between LOF and Isolation Forest: {overlap:.2%}")

# plt.figure(figsize=(8, 6))
# plt.scatter(data_sampled["co2_diff"], data_sampled["t_diff"], label="Normal", alpha=0.3, s=10, color="blue")
# plt.scatter(anomalies_sampled["co2_diff"], anomalies_sampled["t_diff"], color="red", label="Anomalies", marker="x", s=20)
# plt.xlabel("CO₂ Difference (Post - Pre)")
# plt.ylabel("Temperature Difference (Post - Pre)")
# plt.title("LOF vs Isolation Forest Anomalies")
# plt.legend()
# plt.show()

# time series anomaly detection
time_sample_size = min(5000, len(data))  # limit the number of points to plot
data_time_sampled = data.sample(time_sample_size, random_state=42)

# time series plot
plt.figure(figsize=(12, 6))
plt.plot(data_time_sampled["TheTime"], data_time_sampled["co2_diff"], label="CO₂ Difference (normal)", alpha=0.3, color="blue")
plt.scatter(anomalies_sampled["TheTime"], anomalies_sampled["co2_diff"], color="red", label="Anomalies", marker="x", s=20)
plt.xlabel("Time")
plt.ylabel("CO₂ Difference (Post - Pre)")
plt.title("Time Series Anomaly Detection")
plt.legend()
plt.xticks(rotation=45)
plt.show()
