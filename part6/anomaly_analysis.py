import pandas as pd



# 1. ĐỌC DỮ LIỆU


def load_anomaly_data(file_path: str) -> pd.DataFrame:
    """Đọc dữ liệu dị biệt của Người 5."""
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()
    return data


def load_clean_data(file_path: str) -> pd.DataFrame:
    """Đọc dữ liệu sạch để xác định ngưỡng tải trọng."""
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()
    return data



# 2. PHÂN TÍCH ORIGIN - 80%


def analyze_origin(data: pd.DataFrame) -> pd.DataFrame:
    """
    Dùng groupby() để đếm số ca bất thường
    theo Origin_Facility và tính tỷ lệ tích lũy.
    """

    total = len(data)

    if total == 0:
        return pd.DataFrame()

    result = (
        data.groupby("Origin_Facility")
        .size()
        .reset_index(name="Count")
        .sort_values("Count", ascending=False)
    )

    result["Percentage"] = (
        result["Count"] / total * 100
    )

    result["Cumulative_Percentage"] = (
        result["Percentage"].cumsum()
    )

    return result


def find_80_percent_origin(data: pd.DataFrame) -> pd.DataFrame:
    """
    Tìm các Origin_Facility nằm trong nhóm chiếm
    khoảng 80% tổng số ca bất thường.
    """

    result = analyze_origin(data)

    if result.empty:
        return result

    # Lấy các trạm cho đến khi tỷ lệ tích lũy đạt 80%
    result_80 = result[
        result["Cumulative_Percentage"] <= 80
    ].copy()

    # Nếu chưa có trạm nào đạt điều kiện,
    # lấy thêm trạm đầu tiên vượt 80%.
    if result_80.empty:
        result_80 = result.head(1)

    elif result_80["Cumulative_Percentage"].iloc[-1] < 80:
        next_index = len(result_80)

        if next_index < len(result):
            result_80 = result.head(next_index + 1)

    return result_80



# 3. PHÂN TÍCH TRAFFIC


def analyze_traffic(data: pd.DataFrame) -> pd.DataFrame:
    """
    Dùng value_counts() để thống kê điều kiện giao thông
    của các ca bất thường.
    """

    result = (
        data["Traffic_Conditions"]
        .value_counts()
        .reset_index()
    )

    result.columns = [
        "Traffic_Condition",
        "Count"
    ]

    total = len(data)

    if total > 0:
        result["Percentage"] = (
            result["Count"] / total * 100
        )
    else:
        result["Percentage"] = 0

    return result


def check_high_traffic(data: pd.DataFrame) -> bool:
    """
    Kiểm tra tất cả ca bất thường có phải High Traffic không.
    """

    if data.empty:
        return False

    return (
        data["Traffic_Conditions"] == "High"
    ).all()



# 4. PHÂN TÍCH HEAVY TRUCK


def analyze_heavy_truck(
    anomaly_data: pd.DataFrame,
    clean_data: pd.DataFrame
) -> dict:
    """
    Kiểm tra Heavy Truck có chở lượng hàng quá ít
    hay không.

    Ngưỡng tải trọng thấp được xác định bằng Q1
    của toàn bộ Heavy Truck trong dữ liệu sạch.
    """

    heavy_truck_clean = clean_data[
        clean_data["Vehicle_Type"] == "Heavy Truck"
    ]

    heavy_truck_anomaly = anomaly_data[
        anomaly_data["Vehicle_Type"] == "Heavy Truck"
    ].copy()

    if heavy_truck_clean.empty:
        return {
            "threshold": 0,
            "heavy_truck": heavy_truck_anomaly,
            "low_load": pd.DataFrame(),
            "heavy_truck_count": len(heavy_truck_anomaly),
            "low_load_count": 0,
            "low_load_percentage": 0
        }

    # Q1 = 25th percentile
    threshold = heavy_truck_clean[
        "Package_Weight_KG"
    ].quantile(0.25)

    # Heavy Truck có tải trọng thấp
    low_load = heavy_truck_anomaly[
        heavy_truck_anomaly["Package_Weight_KG"] < threshold
    ]

    heavy_truck_count = len(heavy_truck_anomaly)

    if heavy_truck_count > 0:
        low_load_percentage = (
            len(low_load)
            / heavy_truck_count
            * 100
        )
    else:
        low_load_percentage = 0

    return {
        "threshold": threshold,
        "heavy_truck": heavy_truck_anomaly,
        "low_load": low_load,
        "heavy_truck_count": heavy_truck_count,
        "low_load_count": len(low_load),
        "low_load_percentage": low_load_percentage
    }

