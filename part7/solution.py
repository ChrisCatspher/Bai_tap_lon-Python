import pandas as pd


def generate_solutions(clean_data, anomaly_data):
    """
    Phân tích dữ liệu và tự động đề xuất giải pháp
    dựa trên các chỉ số bất thường và hiệu quả vận hành.
    """

    solutions = []


    # 1. PHÂN TÍCH HEAVY TRUCK

    heavy_truck = clean_data[
        clean_data["Vehicle_Type"] == "Heavy Truck"
    ].copy()

    if not heavy_truck.empty:

        load_q1 = heavy_truck["Package_Weight_KG"].quantile(0.25)

        low_load = heavy_truck[
            heavy_truck["Package_Weight_KG"] < load_q1
        ]

        heavy_avg_co2 = heavy_truck[
            "Carbon_Emission_kgCO2e"
        ].mean()

        if len(low_load) > 0:

            solutions.append({
                "Problem": "Heavy Truck có nhiều chuyến tải trọng thấp",
                "Evidence": (
                    f"{len(low_load)} chuyến có tải trọng dưới Q1 "
                    f"({load_q1:.2f} kg). "
                    f"CO2 trung bình Heavy Truck = "
                    f"{heavy_avg_co2:.2f} kg/chuyến."
                ),
                "Solution": (
                    "Tăng tỷ lệ lấp đầy Heavy Truck bằng cách ghép "
                    "các đơn hàng cùng hướng, gom đơn trước khi điều xe "
                    "và hạn chế sử dụng Heavy Truck cho các chuyến có "
                    "tải trọng thấp."
                ),
                "Priority": "Cao"
            })


    # 2. PHÂN TÍCH TRAFFIC

    traffic_avg = (
        clean_data
        .groupby("Traffic_Conditions")
        ["Carbon_Emission_kgCO2e"]
        .mean()
    )

    low_traffic = traffic_avg.get("Low", 0)
    high_traffic = traffic_avg.get("High", 0)
    severe_traffic = traffic_avg.get(
        "Severe Congestion", 0
    )

    if low_traffic > 0:

        high_increase = (
            (high_traffic - low_traffic)
            / low_traffic
            * 100
        )

        severe_increase = (
            (severe_traffic - low_traffic)
            / low_traffic
            * 100
        )

        if high_increase > 20:

            solutions.append({
                "Problem": "Phát thải tăng khi giao thông xấu",
                "Evidence": (
                    f"CO2 trung bình High Traffic tăng "
                    f"{high_increase:.2f}% so với Low Traffic."
                ),
                "Solution": (
                    "Điều chỉnh thời gian giao hàng để tránh "
                    "khung giờ giao thông cao điểm, đồng thời "
                    "ưu tiên các tuyến có điều kiện giao thông tốt hơn."
                ),
                "Priority": "Cao"
            })

        if severe_increase > 20:

            solutions.append({
                "Problem": "Severe Congestion có phát thải cao",
                "Evidence": (
                    f"CO2 trung bình Severe Congestion tăng "
                    f"{severe_increase:.2f}% so với Low Traffic."
                ),
                "Solution": (
                    "Hạn chế lập kế hoạch Heavy Truck vào thời điểm "
                    "Severe Congestion; sử dụng route planning để "
                    "chọn tuyến ít ùn tắc hơn."
                ),
                "Priority": "Cao"
            })


    # 3. PHÂN TÍCH ECO VS NON-ECO

    eco_avg = (
        clean_data
        .groupby("Is_Eco_Friendly")
        ["Carbon_Emission_kgCO2e"]
        .mean()
    )

    eco_co2 = eco_avg.get(1, 0)
    non_eco_co2 = eco_avg.get(0, 0)

    if eco_co2 > 0 and non_eco_co2 > 0:

        reduction = (
            (non_eco_co2 - eco_co2)
            / non_eco_co2
            * 100
        )

        if reduction > 20:

            solutions.append({
                "Problem": "Phương tiện Non-Eco có phát thải cao",
                "Evidence": (
                    f"CO2 trung bình Eco = {eco_co2:.2f} kg, "
                    f"Non-Eco = {non_eco_co2:.2f} kg. "
                    f"Chênh lệch khoảng {reduction:.2f}%."
                ),
                "Solution": (
                    "Ưu tiên phương tiện Eco Friendly cho các "
                    "tuyến và khoảng cách phù hợp; từng bước "
                    "thay thế các chuyến Non-Eco có mức phát thải cao."
                ),
                "Priority": "Cao"
            })


    # 4. PHÂN TÍCH ANOMALY THEO ORIGIN

    if not anomaly_data.empty:

        origin_count = (
            anomaly_data["Origin_Facility"]
            .value_counts()
        )

        total_anomaly = len(anomaly_data)

        top_origin = origin_count.head(3)

        top_count = top_origin.sum()

        top_percentage = (
            top_count
            / total_anomaly
            * 100
        )

        if top_percentage >= 50:

            origin_names = ", ".join(
                top_origin.index.tolist()
            )

            solutions.append({
                "Problem": "Ca bất thường tập trung ở một số trạm",
                "Evidence": (
                    f"{top_percentage:.2f}% ca bất thường "
                    f"tập trung tại {origin_names}."
                ),
                "Solution": (
                    "Ưu tiên kiểm tra quy trình điều phối, "
                    "tải trọng và lựa chọn phương tiện tại "
                    "các trạm có nhiều anomaly trước khi mở rộng "
                    "biện pháp cải thiện sang các trạm khác."
                ),
                "Priority": "Cao"
            })


    # 5. PHÂN TÍCH ROUTE

    route_avg = (
        clean_data
        .groupby("Route_Type")
        ["Carbon_Emission_kgCO2e"]
        .mean()
        .sort_values(ascending=False)
    )

    if not route_avg.empty:

        highest_route = route_avg.index[0]
        highest_route_co2 = route_avg.iloc[0]

        solutions.append({
            "Problem": "Một loại tuyến có mức phát thải trung bình cao",
            "Evidence": (
                f"Tuyến {highest_route} có CO2 trung bình "
                f"{highest_route_co2:.2f} kg/chuyến."
            ),
            "Solution": (
                "Ưu tiên tối ưu tuyến có phát thải cao bằng cách "
                "gom đơn hàng, tối ưu lộ trình và lựa chọn phương tiện "
                "phù hợp với tải trọng và khoảng cách."
            ),
            "Priority": "Trung bình"
        })


    # 6. GIÁM SÁT ANOMALY

    if len(anomaly_data) > 0:

        anomaly_rate = (
            len(anomaly_data)
            / len(clean_data)
            * 100
        )

        solutions.append({
            "Problem": "Xuất hiện nhiều chuyến có dấu hiệu bất thường",
            "Evidence": (
                f"Có {len(anomaly_data)} ca bất thường "
                f"trên {len(clean_data)} chuyến "
                f"({anomaly_rate:.2f}%)."
            ),
            "Solution": (
                "Thiết lập quy trình giám sát anomaly định kỳ "
                "bằng Z-score và IQR để phát hiện sớm các chuyến "
                "có phát thải hoặc hiệu suất bất thường."
            ),
            "Priority": "Trung bình"
        })


    return pd.DataFrame(solutions)


def calculate_priority_summary(solution_df):

    if solution_df.empty:
        return {}

    return {
        "High": int(
            (solution_df["Priority"] == "Cao").sum()
        ),
        "Medium": int(
            (solution_df["Priority"] == "Trung bình").sum()
        ),
        "Total": len(solution_df)
    }