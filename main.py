import subprocess
import sys
from part1.data_cleaning import (
    load_data,
    clean_data,
    feature_engineering,
)
from part5.Anomaly_data import (
    run_part5,
)

def run_dashboard():
    subprocess.run([
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "dashboard_app.py"
    ])


def main():

    print("===== GREEN LOGISTICS =====")
    #part1
    data = load_data("data/data.csv")

    data = clean_data(data)

    data = feature_engineering(data)

    data.to_csv("data/data_clean.csv", index=False)

    #part3

    #part4

    #part5
    run_part5(data)

    run_dashboard()

if __name__ == "__main__":
    main()