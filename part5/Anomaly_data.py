import numpy as np
import pandas as pd
from scipy import stats

from part1.data_cleaning import clean_data, feature_engineering, load_data

def detect_outliers_zscore(data, column, threshold=3):
    z_scores = stats.zscore(data[column])
    return data[np.abs(z_scores) > threshold]

def detect_outliers_iqr(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    return data[data[column] > upper_bound]

def get_anomaly_dataset(data):
    anomalies_z = detect_outliers_zscore(
        data, column="Carbon_Emission_kgCO2e", threshold=3
    )
    anomalies_iqr = detect_outliers_iqr(data, column="CO2_per_km")
    anomaly_data = pd.concat([anomalies_z, anomalies_iqr]).drop_duplicates()
    return anomaly_data

def export_anomaly_report(anomaly_data, output_path="data/anomaly_data.csv"):
    anomaly_data.to_csv(output_path, index=False)
    print(f"Done: {len(anomaly_data)} -> '{output_path}'")

def run_part5(data):
    anomaly_data = get_anomaly_dataset(data)
    export_anomaly_report(anomaly_data)

if __name__ == "__main__":
    run_part5()

