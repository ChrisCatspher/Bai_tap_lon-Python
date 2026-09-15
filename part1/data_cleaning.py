import pandas as pd


def load_data(file_path):
    """Đọc dữ liệu từ file CSV."""
    return pd.read_csv(file_path)


def check_missing(data):
    """Kiểm tra số lượng giá trị thiếu."""
    return data.isnull().sum()


def clean_data(data):
    """Làm sạch dữ liệu không hợp lệ."""

    # Chuyển Date sang kiểu datetime
    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    # Xóa các dòng bị thiếu dữ liệu quan trọng
    data = data.dropna(
        subset=[
            "Date",
            "Distance_KM",
            "Package_Weight_KG",
            "Carbon_Emission_kgCO2e"
        ]
    )

    # Xóa các dòng có giá trị không hợp lệ
    data = data[
        (data["Distance_KM"] > 0)
        & (data["Package_Weight_KG"] > 0)
        & (data["Carbon_Emission_kgCO2e"] >= 0)
    ]

    # Đánh lại index sau khi xóa dòng
    data = data.reset_index(drop=True)

    return data


def feature_engineering(data):
    """Tạo CO2 trên mỗi km và mỗi kg hàng."""
    data["CO2_per_km"] = (
        data["Carbon_Emission_kgCO2e"] / data["Distance_KM"]
    )
    data["CO2_per_kg"] = (
        data["Carbon_Emission_kgCO2e"] / data["Package_Weight_KG"]
    )
    return data


def check_outliers(data, column):
    """Phát hiện outlier bằng phương pháp IQR."""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    return data[(data[column] < lower) | (data[column] > upper)]


def check_vehicle_emission(data):
    """Kiểm tra phát thải theo loại phương tiện."""
    return data.groupby("Vehicle_Type")[
        "Carbon_Emission_kgCO2e"
    ].agg(["count", "mean", "max"])
