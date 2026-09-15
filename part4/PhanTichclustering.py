import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def analyze_correlation(data):
    columns = [
        "Distance_KM",
        "Package_Weight_KG",
        "Carbon_Emission_kgCO2e"
    ]

    return data[columns].corr()


def analyze_vehicle_type(data):
    columns = [
        "Distance_KM",
        "Package_Weight_KG",
        "Carbon_Emission_kgCO2e"
    ]

    return data.groupby("Vehicle_Type")[columns].mean().reset_index()


def analyze_eco_friendly(data):
    data = data.copy()

    data["Distance_Range"] = pd.cut(
        data["Distance_KM"],
        bins=[0, 50, 100, 200, float("inf")],
        labels=[
            "0-50 KM",
            "50-100 KM",
            "100-200 KM",
            "Over 200 KM"
        ]
    )

    data["Weight_Range"] = pd.cut(
        data["Package_Weight_KG"],
        bins=[0, 5, 10, 20, float("inf")],
        labels=[
            "0-5 KG",
            "5-10 KG",
            "10-20 KG",
            "Over 20 KG"
        ]
    )

    return data.groupby(
        [
            "Distance_Range",
            "Weight_Range",
            "Is_Eco_Friendly"
        ],
        observed=True
    )["Carbon_Emission_kgCO2e"].mean().reset_index()


def analyze_eco_saving(data):
    data = data.copy()

    data["Distance_Range"] = pd.cut(
        data["Distance_KM"],
        bins=[0, 50, 100, 200, float("inf")],
        labels=[
            "0-50 KM",
            "50-100 KM",
            "100-200 KM",
            "Over 200 KM"
        ]
    )

    data["Weight_Range"] = pd.cut(
        data["Package_Weight_KG"],
        bins=[0, 5, 10, 20, float("inf")],
        labels=[
            "0-5 KG",
            "5-10 KG",
            "10-20 KG",
            "Over 20 KG"
        ]
    )

    result = data.groupby(
        [
            "Distance_Range",
            "Weight_Range",
            "Is_Eco_Friendly"
        ],
        observed=True
    )["Carbon_Emission_kgCO2e"].mean().unstack(
        "Is_Eco_Friendly"
    )

    result = result.rename(
        columns={
            False: "Normal_CO2",
            True: "Eco_CO2"
        }
    )

    if "Normal_CO2" not in result.columns:
        result["Normal_CO2"] = pd.NA

    if "Eco_CO2" not in result.columns:
        result["Eco_CO2"] = pd.NA

    result["CO2_Saving"] = (
        result["Normal_CO2"] - result["Eco_CO2"]
    )

    result["Saving_Percent"] = (
        result["CO2_Saving"]
        / result["Normal_CO2"]
        * 100
    )

    return result.reset_index()


def clustering_data(data, n_clusters=3):
    columns = [
        "Distance_KM",
        "Package_Weight_KG",
        "Carbon_Emission_kgCO2e"
    ]

    X = data[columns].dropna()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    clusters = kmeans.fit_predict(X_scaled)

    result = data.loc[X.index].copy()
    result["Cluster"] = clusters

    return result


def analyze_clusters(data):
    columns = [
        "Distance_KM",
        "Package_Weight_KG",
        "Carbon_Emission_kgCO2e"
    ]

    return data.groupby("Cluster")[columns].mean().reset_index()


def find_inefficient_cluster(data):
    cluster_mean = analyze_clusters(data).set_index("Cluster")

    distance_score = (
        cluster_mean["Distance_KM"]
        / cluster_mean["Distance_KM"].max()
    )

    weight_score = (
        1
        - (
            cluster_mean["Package_Weight_KG"]
            / cluster_mean["Package_Weight_KG"].max()
        )
    )

    emission_score = (
        cluster_mean["Carbon_Emission_kgCO2e"]
        / cluster_mean["Carbon_Emission_kgCO2e"].max()
    )

    score = (
        distance_score
        + weight_score
        + emission_score
    )

    return score.idxmax()


def find_heavy_truck_inefficient(data):
    heavy_truck = data[
        data["Vehicle_Type"].str.lower() == "heavy truck"
    ].copy()

    if heavy_truck.empty:
        return heavy_truck

    weight_threshold = heavy_truck[
        "Package_Weight_KG"
    ].quantile(0.25)

    distance_threshold = heavy_truck[
        "Distance_KM"
    ].quantile(0.75)

    emission_threshold = heavy_truck[
        "Carbon_Emission_kgCO2e"
    ].quantile(0.75)

    result = heavy_truck[
        (heavy_truck["Package_Weight_KG"] <= weight_threshold)
        &
        (heavy_truck["Distance_KM"] >= distance_threshold)
        &
        (
            heavy_truck["Carbon_Emission_kgCO2e"]
            >= emission_threshold
        )
    ].copy()

    return result.sort_values(
        "Carbon_Emission_kgCO2e",
        ascending=False
    )

