import streamlit as st

from part2.visualization import (
    load_clean_data2,
    get_summary,
    daily_emission_chart,
    weekly_emission_chart,
    monthly_emission_chart,
    origin_volume_chart,
    origin_chart,
    vehicle_chart,
    eco_chart
)

from part3.Traffic_ANOVA import (
    run_traffic_anova_test,
    plot_route_emission,
    plot_traffic_emission
)

from part4.PhanTichclustering import ( 
    analyze_correlation, 
    analyze_vehicle_type, 
    analyze_eco_saving, 
    clustering_data, 
    analyze_clusters, 
    find_inefficient_cluster, 
    find_heavy_truck_inefficient 
)

from part6.anomaly_analysis import ( 
    load_anomaly_data, 
    load_clean_data, 
    analyze_origin, 
    find_80_percent_origin, 
    analyze_traffic, 
    check_high_traffic, 
    analyze_heavy_truck 
)

# PART 2
# CONFIG

st.set_page_config(
    page_title="Green Logistics Dashboard",
    page_icon="🌱",
    layout="wide"
)


# TITLE

st.title(
    "Bảng điều khiển phát thải Carbon trong Logistics Xanh"
)

st.write(
    """
    Ứng dụng phân tích và trực quan hóa lượng phát thải CO2
    trong hoạt động logistics.
    """
)


# LOAD DATA

data = load_clean_data2(
    "data/data_clean.csv"
)


# SIDEBAR FILTER

st.sidebar.header(
    "Bộ lọc"
)


# Vehicle filter

vehicle_options = sorted(
    data["Vehicle_Type"]
    .dropna()
    .unique()
)

selected_vehicle = st.sidebar.multiselect(
    "Loại phương tiện",
    vehicle_options,
    default=vehicle_options
)


# Origin filter

origin_options = sorted(
    data["Origin_Facility"]
    .dropna()
    .unique()
)

selected_origin = st.sidebar.multiselect(
    "Trạm xuất phát",
    origin_options,
    default=origin_options
)


# FILTER DATA

filtered_data = data[
    data["Vehicle_Type"].isin(selected_vehicle)
    &
    data["Origin_Facility"].isin(selected_origin)
]


# Check empty data

if filtered_data.empty:

    st.warning(
        "Không có dữ liệu phù hợp với bộ lọc đã chọn."
    )

    st.stop()


# KPI

summary = get_summary(
    filtered_data
)


# Hàng 1
col1, col2, col3 = st.columns(3)

col1.metric(
    "Tổng lượng CO2",
    f"{summary['Total CO2']:,.2f} kg"
)

col2.metric(
    "Lượng CO2 trung bình/chuyến",
    f"{summary['Average CO2/trip']:,.2f} kg"
)

col3.metric(
    "Tổng quãng đường",
    f"{summary['Total Distance']:,.2f} km"
)


# Hàng 2
col4, col5 = st.columns(2)

col4.metric(
    "Tổng khối lượng hàng hóa",
    f"{summary['Total Package']:,.2f} kg"
)

col5.metric(
    "Tổng số chuyến",
    f"{summary['Total Trips']:,}"
)


# TIME TREND

st.header(
    "Xu hướng phát thải Carbon"
)


st.plotly_chart(
    daily_emission_chart(
        filtered_data
    ),
    use_container_width=True
)


col1, col2 = st.columns(2)


with col1:

    st.plotly_chart(
        weekly_emission_chart(
            filtered_data
        ),
        use_container_width=True
    )


with col2:

    st.plotly_chart(
        monthly_emission_chart(
            filtered_data
        ),
        use_container_width=True
    )


# ORIGIN FACILITY

st.header(
    "Phân tích trạm xuất phát"
)


col1, col2 = st.columns(2)


with col1:

    st.plotly_chart(
        origin_volume_chart(
            filtered_data
        ),
        use_container_width=True
    )


with col2:

    st.plotly_chart(
        origin_chart(
            filtered_data
        ),
        use_container_width=True
    )


st.divider()


# VEHICLE ANALYSIS

st.header(
    "Phân tích phương tiện"
)


col1, col2 = st.columns(2)


with col1:

    st.plotly_chart(
        vehicle_chart(
            filtered_data
        ),
        use_container_width=True
    )


with col2:

    st.plotly_chart(
        eco_chart(
            filtered_data
        ),
        use_container_width=True
    )

st.divider()

# PART 3

st.title("Phân tích tác động giao thông đến phát thải CO₂")


# 1. CO2 THEO GIAO THÔNG

st.subheader(
    "1. Phát thải CO₂ theo điều kiện giao thông"
)

plot_traffic_emission(
    filtered_data
)


# 2. CO2 THEO LOẠI TUYẾN

st.subheader(
    "2. Phát thải CO₂ theo loại tuyến"
)

plot_route_emission(
    filtered_data
)


# 3. ANOVA

st.subheader(
    "3. Kiểm định ANOVA"
)

anova_result = run_traffic_anova_test(
    filtered_data
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "F-statistic",
    f"{anova_result['f_statistic']:.4f}"
)

p = anova_result["p_value"]

if p < 0.001:
    p_display = "< 0.001"
else:
    p_display = f"{p:.4f}"

col2.metric(
    "p-value",
    p_display
)

col3.metric(
    "Alpha",
    anova_result['alpha']
)

st.info(
    anova_result['conclusion']
)

st.divider()

# PART 4

st.title(
    "Phân tích tương quan và phân cụm chuyến hàng"
)


# 1. PHÂN TÍCH TƯƠNG QUAN


st.subheader(
    "1. Tương quan giữa khoảng cách, khối lượng và phát thải CO₂"
)

correlation_result = analyze_correlation(
    filtered_data
)

st.dataframe(
    correlation_result,
    use_container_width=True
)



# 2. PHÂN TÍCH THEO LOẠI PHƯƠNG TIỆN


st.subheader(
    "2. Phân tích theo loại phương tiện"
)

vehicle_analysis = analyze_vehicle_type(
    filtered_data
)

st.dataframe(
    vehicle_analysis,
    use_container_width=True
)



# 3. XE XANH TIẾT KIỆM CO₂ Ở ĐÂU?


st.subheader(
    "3. Hiệu quả của phương tiện xanh"
)

eco_result = analyze_eco_saving(
    filtered_data
)

st.dataframe(
    eco_result,
    use_container_width=True
)



# 4. K-MEANS CLUSTERING


st.subheader(
    "4. Phân cụm các chuyến hàng"
)

clustered_data = clustering_data(
    filtered_data,
    n_clusters=3
)

cluster_result = analyze_clusters(
    clustered_data
)

st.dataframe(
    cluster_result,
    use_container_width=True
)



# 5. CLUSTER KÉM HIỆU QUẢ NHẤT


st.subheader(
    "5. Cụm chuyến hàng kém hiệu quả nhất"
)

inefficient_cluster = find_inefficient_cluster(
    clustered_data
)

st.metric(
    "Cluster kém hiệu quả nhất",
    f"Cluster {inefficient_cluster}"
)


inefficient_data = clustered_data[
    clustered_data["Cluster"] == inefficient_cluster
]


st.write(
    "Các chuyến hàng thuộc cụm này:"
)

st.dataframe(
    inefficient_data,
    use_container_width=True
)



# 6. HEAVY TRUCK: TẢI THẤP + ĐI XA + CO₂ CAO


st.subheader(
    "6. Heavy Truck chở nhẹ nhưng đi xa"
)

heavy_truck_result = find_heavy_truck_inefficient(
    filtered_data
)


if heavy_truck_result.empty:

    st.info(
        "Không tìm thấy chuyến Heavy Truck nào "
        "vừa có tải trọng thấp, vừa đi xa và phát thải cao."
    )

else:

    st.warning(
        f"Phát hiện {len(heavy_truck_result)} chuyến "
        "Heavy Truck có dấu hiệu kém hiệu quả."
    )

    st.dataframe(
        heavy_truck_result,
        use_container_width=True
    )

st.divider()

# PART 6


st.title("Phân tích dữ liệu dị biệt")

# Đọc dữ liệu
anomaly_data = load_anomaly_data(
    "data/anomaly_data.csv"
)

clean_data = load_clean_data(
    "data/data_clean.csv"
)



# CÂU HỎI 1
# 80% CA BẤT THƯỜNG ĐẾN TỪ ĐÂU?


st.subheader(
    "1. 80% các ca bất thường đến từ Trạm xuất phát nào?"
)

origin_result = analyze_origin(anomaly_data)

if origin_result.empty:

    st.warning("Không có dữ liệu bất thường.")

else:

    st.dataframe(
        origin_result,
        use_container_width=True
    )

    origin_80 = find_80_percent_origin(
        anomaly_data
    )

    st.write("### Nhóm trạm chiếm khoảng 80% ca bất thường")

    st.dataframe(
        origin_80,
        use_container_width=True
    )

    total_80 = origin_80["Percentage"].sum()

    st.metric(
        "Tỷ lệ ca bất thường",
        f"{total_80:.2f}%"
    )



# CÂU HỎI 2
# CÓ PHẢI TẤT CẢ ĐỀU HIGH TRAFFIC?


st.subheader(
    "2. Các ca bất thường có phải đều xảy ra khi High Traffic?"
)

traffic_result = analyze_traffic(
    anomaly_data
)

st.dataframe(
    traffic_result,
    use_container_width=True
)

all_high = check_high_traffic(
    anomaly_data
)

if all_high:

    st.success(
        "Có. Tất cả các ca bất thường đều xảy ra "
        "trong điều kiện High Traffic."
    )

else:

    st.warning(
        "Không. Các ca bất thường không chỉ xảy ra "
        "trong điều kiện High Traffic."
    )



# CÂU HỎI 3
# HEAVY TRUCK CÓ CHỞ QUÁ ÍT HÀNG?


st.subheader(
    "3. Heavy Truck có đang chở lượng hàng quá ít?"
)

truck_result = analyze_heavy_truck(
    anomaly_data,
    clean_data
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Heavy Truck bất thường",
        truck_result["heavy_truck_count"]
    )

with col2:
    st.metric(
        "Ngưỡng tải trọng thấp",
        f"{truck_result['threshold']:.2f} KG"
    )

with col3:
    st.metric(
        "Heavy Truck tải thấp",
        truck_result["low_load_count"]
    )


st.write(
    f"Tỷ lệ Heavy Truck tải thấp: "
    f"**{truck_result['low_load_percentage']:.2f}%**"
)


if truck_result["low_load_count"] > 0:

    st.write("### Các ca Heavy Truck tải trọng thấp")

    st.dataframe(
        truck_result["low_load"],
        use_container_width=True
    )

else:

    st.info(
        "Không phát hiện Heavy Truck bất thường "
        "có tải trọng thấp hơn ngưỡng Q1."
    )


# FOOTER

st.divider()

st.caption(
    "Bảng điều khiển phát thải Carbon trong Logistics Xanh | "
    "Mô-đun trực quan hóa dữ liệu"
)

