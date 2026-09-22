import streamlit as st
import plotly.express as px

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

from part7.solution import (
    generate_solutions,
    calculate_priority_summary
)



# PART 2 - TỔNG QUAN & TRỰC QUAN HÓA


# Cấu hình trang
st.set_page_config(
    page_title="Green Logistics Dashboard",
    page_icon="🌱",
    layout="wide"
)


# Tiêu đề dashboard
st.title(
    "Bảng điều khiển phát thải Carbon trong Logistics Xanh"
)

st.write(
    """
    Ứng dụng phân tích và trực quan hóa lượng phát thải CO₂
    trong hoạt động logistics.
    """
)


# Đọc dữ liệu
data = load_clean_data2(
    "data/data_clean.csv"
)

anomaly_data = load_anomaly_data(
    "data/anomaly_data.csv"
)
clean_data = load_clean_data(
    "data/data_clean.csv"
)



def create_filtered_data(data):
    st.sidebar.header("Bộ lọc")


    # Bộ lọc phương tiện
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


    # Bộ lọc trạm xuất phát
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


    # Lọc dữ liệu theo lựa chọn
    filtered_data = data[
        data["Vehicle_Type"].isin(selected_vehicle)
        &
        data["Origin_Facility"].isin(selected_origin)
    ]

    return filtered_data



menu = st.sidebar.radio(
    "MENU",
    [
        "🏠 Trang chủ",
        "📊 Tổng quan dữ liệu",
        "🚦 Phân tích giao thông & kiểm định ANOVA",
        "🔍 Phân tích tương quan và phân cụm",
        "❌ Phân tích bất thường",
        "🍀 Đề xuất giải pháp Logistics Xanh"
    ]
)



if menu == "🏠 Trang chủ":
    st.header("🏠 Trang chủ")
    st.write("Chào mừng đến với Bảng điều khiển Logistics Xanh!")



elif menu == "📊 Tổng quan dữ liệu":

    st.divider()

    st.header("📊 Tổng quan dữ liệu")

    filtered_data = create_filtered_data(data)


    # Kiểm tra dữ liệu sau khi lọc
    if filtered_data.empty:

        st.warning(
            "Không có dữ liệu phù hợp với bộ lọc đã chọn."
        )

        st.stop()


    # Chỉ số tổng quan (KPI)
    summary = get_summary(
        filtered_data
    )


    # Hàng KPI 1
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Tổng lượng CO₂",
        f"{summary['Total CO2']:,.2f} kg"
    )

    col2.metric(
        "Lượng CO₂ trung bình/chuyến",
        f"{summary['Average CO2/trip']:,.2f} kg"
    )

    col3.metric(
        "Tổng quãng đường",
        f"{summary['Total Distance']:,.2f} km"
    )


    # Hàng KPI 2
    col4, col5 = st.columns(2)

    col4.metric(
        "Tổng khối lượng hàng hóa",
        f"{summary['Total Package']:,.2f} kg"
    )

    col5.metric(
        "Tổng số chuyến",
        f"{summary['Total Trips']:,}"
    )


    # Xu hướng phát thải theo thời gian
    st.subheader("Xu hướng phát thải CO₂ theo thời gian")

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


    # Phân tích theo trạm xuất phát
    st.subheader("Phân tích theo trạm xuất phát")

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


    # Phân tích theo phương tiện

    st.subheader("Phân tích theo phương tiện")

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



elif menu == "🚦 Phân tích giao thông & kiểm định ANOVA":


    # PART 3 - PHÂN TÍCH GIAO THÔNG & KIỂM ĐỊNH ANOVA

    st.divider()

    st.header("🚦 Phân tích giao thông & kiểm định ANOVA")

    st.caption("Đánh giá tác động của điều kiện giao thông và loại tuyến đến phát thải CO₂.")

    filtered_data = create_filtered_data(data)


    # Kiểm tra dữ liệu sau khi lọc
    if filtered_data.empty:

        st.warning(
            "Không có dữ liệu phù hợp với bộ lọc đã chọn."
        )

        st.stop()


    # 1. Phát thải CO₂ theo điều kiện giao thông

    st.subheader(
        "1. Phát thải CO₂ theo điều kiện giao thông"
    )

    plot_traffic_emission(
        filtered_data
    )


    # 2. Phát thải CO₂ theo loại tuyến

    st.subheader(
        "2. Phát thải CO₂ theo loại tuyến"
    )

    plot_route_emission(
        filtered_data
    )


    # 3. Kiểm định ANOVA

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



elif menu == "🔍 Phân tích tương quan và phân cụm":


    # PART 4 - TƯƠNG QUAN & PHÂN CỤM

    st.divider()

    filtered_data = create_filtered_data(data)


    # Kiểm tra dữ liệu sau khi lọc
    if filtered_data.empty:

        st.warning(
            "Không có dữ liệu phù hợp với bộ lọc đã chọn."
        )

        st.stop()

    st.header("🔍 Phân tích tương quan và phân cụm")
    st.caption("Phân tích mối quan hệ giữa khoảng cách, khối lượng, phát thải và đặc điểm các nhóm chuyến hàng.")


    # 1. Phân tích tương quan

    st.subheader("1. Tương quan giữa khoảng cách, khối lượng và phát thải CO₂")

    correlation_result = analyze_correlation(
    filtered_data
    )

    fig = px.imshow(
        correlation_result,
        text_auto=".2f",
        aspect="auto",
        title="Ma trận tương quan"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    with st.expander("Xem bảng hệ số tương quan"):
        st.dataframe(
            correlation_result,
            use_container_width=True
        )


    # 2. Phân tích theo loại phương tiện

    st.subheader("2. Phân tích theo loại phương tiện")

    vehicle_analysis = analyze_vehicle_type(
        filtered_data
    )

    fig = px.bar(
        vehicle_analysis,
        x="Vehicle_Type",
        y="Carbon_Emission_kgCO2e",
        title="Phát thải CO₂ trung bình theo loại phương tiện",
        labels={
            "Vehicle_Type": "Loại phương tiện",
            "Carbon_Emission_kgCO2e": "CO₂ trung bình (kgCO₂e)"
        },
        text_auto=".2f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    with st.expander("Xem số liệu chi tiết"):
        st.dataframe(
            vehicle_analysis,
            use_container_width=True
        )


    # 3. So sánh hiệu quả phương tiện xanh

    st.subheader("3. Hiệu quả của phương tiện xanh")

    eco_result = analyze_eco_saving(
        filtered_data
    )

    selected_distance = st.selectbox(
        "Khoảng cách",
        eco_result["Distance_Range"].dropna().unique()
    )

    eco_chart_data = eco_result[
        eco_result["Distance_Range"] == selected_distance
    ].copy()

    plot_data = eco_chart_data.melt(
        id_vars=["Weight_Range"],
        value_vars=["Normal_CO2", "Eco_CO2"],
        var_name="Vehicle_Category",
        value_name="CO2"
    )

    fig = px.bar(
        plot_data,
        x="Weight_Range",
        y="CO2",
        color="Vehicle_Category",
        barmode="group",
        title=f"So sánh CO₂ theo tải trọng - {selected_distance}",
        labels={
            "Weight_Range": "Khối lượng hàng",
            "CO2": "CO₂ trung bình (kgCO₂e)",
            "Vehicle_Category": "Loại phương tiện"
        },
        text_auto=".2f"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # 4. Phân cụm K-Means

    st.subheader("4. Phân cụm các chuyến hàng")

    clustered_data = clustering_data(
        filtered_data,
        n_clusters=3
    )

    fig = px.scatter(
        clustered_data,
        x="Distance_KM",
        y="Carbon_Emission_kgCO2e",
        color="Cluster",
        size="Package_Weight_KG",
        hover_data=[
            "Vehicle_Type",
            "Package_Weight_KG"
        ],
        title="Phân cụm các chuyến hàng bằng K-Means",
        labels={
            "Distance_KM": "Khoảng cách (KM)",
            "Carbon_Emission_kgCO2e": "Phát thải CO₂ (kgCO₂e)",
            "Cluster": "Cluster",
            "Package_Weight_KG": "Khối lượng (KG)"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # 5. Xác định Cluster kém hiệu quả nhất

    st.subheader("5. Cụm chuyến hàng kém hiệu quả nhất")

    inefficient_Cluster = find_inefficient_cluster(
        clustered_data
    )

    st.metric(
        "Cụm kém hiệu quả nhất",
        f"Cụm {inefficient_Cluster}"
    )


    # Dữ liệu thuộc Cluster kém hiệu quả
    inefficient_data = clustered_data[
        clustered_data["Cluster"] == inefficient_Cluster
    ]


    # So sánh CO₂ trung bình giữa các Cluster
    cluster_compare = (
        clustered_data
        .groupby("Cluster")
        [
            [
                "Distance_KM",
                "Package_Weight_KG",
                "Carbon_Emission_kgCO2e"
            ]
        ]
        .mean()
        .reset_index()
    )


    fig = px.bar(
        cluster_compare,
        x="Cluster",
        y="Carbon_Emission_kgCO2e",
        title="Phát thải CO₂ trung bình của từng phân cụm",
        text_auto=".2f",
        labels={
            "Cluster": "Cluster",
            "Carbon_Emission_kgCO2e": "CO₂ trung bình"
        }
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # Thống kê chi tiết Cluster kém hiệu quả
    with st.expander(
        "Xem thống kê của những phân cụm kém hiệu quả"
    ):

        inefficient_summary = (
            inefficient_data[
                [
                    "Distance_KM",
                    "Package_Weight_KG",
                    "Carbon_Emission_kgCO2e"
                ]
            ]
            .mean()
            .to_frame()
            .T
        )

        st.dataframe(
            inefficient_summary,
            use_container_width=True
        )


    # Danh sách chuyến hàng thuộc Cluster
    with st.expander(
        "Xem các chuyến hàng thuộc phân cụm này"
    ):

        st.dataframe(
            inefficient_data,
            use_container_width=True
        )


    # 6. Heavy Truck: tải thấp, đi xa và phát thải cao

    st.subheader("6. Heavy Truck chở nhẹ nhưng đi xa")

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

        heavy_truck = filtered_data[
            filtered_data["Vehicle_Type"].str.lower() == "heavy truck"
        ].copy()

        heavy_truck["Inefficient"] = heavy_truck.index.isin(
            heavy_truck_result.index
        )

        fig = px.scatter(
            heavy_truck,
            x="Distance_KM",
            y="Carbon_Emission_kgCO2e",
            size="Package_Weight_KG",
            color="Inefficient",
            hover_data=[
                "Package_Weight_KG",
                "Vehicle_Type"
            ],
            title="Heavy Truck: phát hiện các chuyến có dấu hiệu kém hiệu quả"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            heavy_truck_result,
            use_container_width=True
        )



elif menu == "❌ Phân tích bất thường":


    # PART 6 - PHÂN TÍCH BẤT THƯỜNG

    st.divider()

    st.header("❌ Phân tích bất thường")
    st.caption("Khám phá các ca bất thường theo trạm xuất phát, giao thông và phương tiện.")

    
    # Kiểm tra dữ liệu bất thường
    if anomaly_data.empty:

        st.warning(
            "Không có dữ liệu bất thường để phân tích."
        )

        st.stop()


    
    # Tổng quan dữ liệu bất thường
    
    st.subheader("Tổng quan dữ liệu bất thường")


    # Tổng số ca bất thường
    total_anomaly = len(anomaly_data)


    # Số ca bất thường trong điều kiện High Traffic
    high_traffic_count = len(
        anomaly_data[
            anomaly_data["Traffic_Conditions"] == "High"
        ]
    )


    # Số ca bất thường liên quan đến Heavy Truck
    heavy_truck_count = len(
        anomaly_data[
            anomaly_data["Vehicle_Type"] == "Heavy Truck"
        ]
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Tổng số ca bất thường",
            total_anomaly
        )

    with col2:

        st.metric(
            "High Traffic",
            high_traffic_count
        )

    with col3:

        st.metric(
            "Heavy Truck",
            heavy_truck_count
        )

    
    # Phân tích 1 - Trạm xuất phát
    # Xác định nhóm trạm chiếm khoảng 80% ca bất thường 

    st.subheader("1. Phân bố ca bất thường theo trạm xuất phát")

    origin_result = analyze_origin(
        anomaly_data
    )

    if origin_result.empty:

        st.warning(
            "Không có dữ liệu bất thường theo trạm xuất phát."
        )

    else:

        
        # Bảng dữ liệu
        st.write("**Số ca bất thường theo trạm xuất phát**")

        st.dataframe(
            origin_result,
            use_container_width=True
        )

        
        # Biểu đồ cột
        st.write("**Biểu đồ phân bố ca bất thường**")

        origin_chart_data = (
            origin_result
            .set_index("Origin_Facility")
        )

        st.bar_chart(
            origin_chart_data["Count"]
        )

        
        # Phân tích nhóm trạm chiếm khoảng 80%   
        origin_80 = find_80_percent_origin(
            anomaly_data
        )

        st.write("**Nhóm trạm chiếm khoảng 80% ca bất thường**")

        st.dataframe(
            origin_80,
            use_container_width=True
        )

        total_80 = origin_80[
            "Percentage"
        ].sum()

        st.metric(
            "Tỷ lệ ca bất thường",
            f"{total_80:.2f}%"
        )

        
        # Biểu đồ Pareto
        st.write("**Phân tích Pareto theo trạm xuất phát**")

        pareto_data = (
            origin_result[
                [
                    "Origin_Facility",
                    "Count"
                ]
            ]
            .sort_values(
                "Count",
                ascending=False
            )
            .copy()
        )

        pareto_data[
            "Cumulative_Percentage"
        ] = (
            pareto_data["Count"].cumsum()
            / pareto_data["Count"].sum()
            * 100
        )

        import plotly.graph_objects as go

        fig_pareto = go.Figure()

 
        # Cột số lượng ca bất thường
        fig_pareto.add_trace(
            go.Bar(
                x=pareto_data["Origin_Facility"],
                y=pareto_data["Count"],
                name="Số ca bất thường"
            )
        )

  
        # Đường phần trăm tích lũy
        fig_pareto.add_trace(
            go.Scatter(
                x=pareto_data["Origin_Facility"],
                y=pareto_data[
                    "Cumulative_Percentage"
                ],
                name="% tích lũy",
                mode="lines+markers",
                yaxis="y2"
            )
        )


        # Đường tham chiếu 80%
        fig_pareto.add_hline(
            y=80,
            line_dash="dash",
            annotation_text="80%",
            yref="y2"
        )

        fig_pareto.update_layout(
            xaxis_title="Trạm xuất phát",
            yaxis_title="Số ca bất thường",
            yaxis2=dict(
                title="% tích lũy",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            legend=dict(
                orientation="h"
            ),
            height=500
        )

        st.plotly_chart(
            fig_pareto,
            use_container_width=True
        )

    
    # Phân tích 2 - Điều kiện giao thông
    # Kiểm tra các ca bất thường trong điều kiện High Traffic 

    st.subheader("2. Phân bố ca bất thường theo điều kiện giao thông")

    traffic_result = analyze_traffic(
        anomaly_data
    )

    if traffic_result.empty:

        st.warning(
            "Không có dữ liệu về điều kiện giao thông."
        )

    else:

        
        # Bảng dữ liệu

        st.write("**Phân bố ca bất thường theo điều kiện giao thông**")

        st.dataframe(
            traffic_result,
            use_container_width=True
        )

   
        # Biểu đồ cột        

        traffic_chart_data = (
            traffic_result
            .set_index("Traffic_Condition")
        )

        st.bar_chart(
            traffic_chart_data["Count"]
        )

        
        # CHECK HIGH TRAFFIC
        
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


    # Phân tích 3 - Heavy Truck và tải trọng
    # Kiểm tra Heavy Truck có tải trọng thấp
    
    st.subheader("3. Heavy Truck và tải trọng thấp")

    truck_result = analyze_heavy_truck(
        anomaly_data,
        clean_data
    )

    
    # Các chỉ số
    
    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Heavy Truck bất thường",
            truck_result[
                "heavy_truck_count"
            ]
        )

    with col2:

        st.metric(
            "Ngưỡng tải trọng thấp",
            f"{truck_result['threshold']:.2f} KG"
        )

    with col3:

        st.metric(
            "Heavy Truck tải thấp",
            truck_result[
                "low_load_count"
            ]
        )


    st.write(
        f"Tỷ lệ Heavy Truck tải thấp: "
        f"**{truck_result['low_load_percentage']:.2f}%**"
    )

 
    # Phân bố tải trọng Heavy Truck
    
    heavy_truck_data = anomaly_data[
        anomaly_data["Vehicle_Type"]
        == "Heavy Truck"
    ].copy()


    if not heavy_truck_data.empty:

        st.write("**Phân bố tải trọng Heavy Truck**")

        import plotly.express as px

        fig_weight = px.histogram(
            heavy_truck_data,
            x="Package_Weight_KG",
            nbins=20,
            title=(
                "Phân bố tải trọng của Heavy Truck "
                "trong các ca bất thường"
            ),
            labels={
                "Package_Weight_KG":
                    "Khối lượng hàng (KG)",
                "count":
                    "Số ca"
            }
        )


        # Đường tham chiếu ngưỡng Q1
        fig_weight.add_vline(
            x=truck_result["threshold"],
            line_dash="dash",
            annotation_text=(
                f"Ngưỡng thấp = "
                f"{truck_result['threshold']:.2f} KG"
            )
        )

        fig_weight.update_layout(
            height=500
        )

        st.plotly_chart(
            fig_weight,
            use_container_width=True
        )

  
    # Các ca Heavy Truck có tải trọng thấp
    
    if truck_result[
        "low_load_count"
    ] > 0:

        st.write("**Các ca Heavy Truck tải trọng thấp**")

        st.dataframe(
            truck_result["low_load"],
            use_container_width=True
        )

    else:

        st.info(
            "Không phát hiện Heavy Truck bất thường "
            "có tải trọng thấp hơn ngưỡng Q1."
        )

   
    # Phân tích bổ sung
    # Quan hệ giữa tải trọng và phát thải
    
    st.subheader("4. Quan hệ giữa tải trọng và phát thải")

    st.write(
        "Biểu đồ giúp phát hiện các trường hợp "
        "tải trọng thấp nhưng lượng phát thải cao."
    )

    scatter_data = anomaly_data[
        [
            "Package_Weight_KG",
            "Carbon_Emission_kgCO2e"
        ]
    ].dropna()

    if not scatter_data.empty:

        fig_scatter = px.scatter(
            scatter_data,
            x="Package_Weight_KG",
            y="Carbon_Emission_kgCO2e",
            title=(
                "Tải trọng và phát thải "
                "của các ca bất thường"
            ),
            labels={
                "Package_Weight_KG":
                    "Khối lượng hàng (KG)",
                "Carbon_Emission_kgCO2e":
                    "Phát thải CO₂ (kgCO₂e)"
            },
            opacity=0.7
        )

        fig_scatter.update_layout(
            height=550
        )

        st.plotly_chart(
            fig_scatter,
            use_container_width=True
        )


    # Tóm tắt kết quả phân tích
    
    st.divider()

    st.subheader("Tóm tắt phân tích bất thường")

    st.write(
        f"""
        - Tổng số ca bất thường: **{total_anomaly}**
        - Số ca xảy ra trong High Traffic: **{high_traffic_count}**
        - Số ca liên quan đến Heavy Truck: **{heavy_truck_count}**
        - Ngưỡng tải trọng thấp của Heavy Truck:
          **{truck_result['threshold']:.2f} KG**
        - Heavy Truck tải thấp:
          **{truck_result['low_load_count']} ca**
        """
    )



elif menu == "🍀 Đề xuất giải pháp Logistics Xanh":


    # PART 7 - ĐỀ XUẤT GIẢI PHÁP

    st.divider()

    st.header("🍀 Đề xuất giải pháp Logistics Xanh")

    solution_result = generate_solutions(
        clean_data,
        anomaly_data
    )

    if solution_result.empty:

        st.info(
            "Không phát hiện vấn đề cần đề xuất giải pháp."
        )

    else:

        summary = calculate_priority_summary(
            solution_result
        )


        # Chỉ số tổng quan (KPI)
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Tổng số giải pháp",
            summary["Total"]
        )

        col2.metric(
            "Giải pháp ưu tiên cao",
            summary["High"]
        )

        col3.metric(
            "Giải pháp ưu tiên trung bình",
            summary["Medium"]
        )


        # Hiển thị chi tiết từng giải pháp
        for i, row in solution_result.iterrows():

            if row["Priority"] == "Cao":

                st.error(
                    f"🔴 {i + 1}. {row['Problem']}"
                )

            else:

                st.warning(
                    f"🟡 {i + 1}. {row['Problem']}"
                )

            st.write(
                f"**Dữ liệu phát hiện:** {row['Evidence']}"
            )

            st.write(
                f"**Giải pháp đề xuất:** {row['Solution']}"
            )

            st.write(
                f"**Mức độ ưu tiên:** {row['Priority']}"
            )

            st.divider()

    solution_result = generate_solutions(
        clean_data,
        anomaly_data
    )

    solution_display = solution_result.copy()
    solution_display.insert(
        0,
        "",
        range(1, len(solution_display) + 1)
    )

    st.dataframe(
        solution_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "": st.column_config.NumberColumn(
                "",
                width="small"
            ),
            "Problem": st.column_config.TextColumn(
                "Vấn đề",
                width="large"
            ),
            "Evidence": st.column_config.TextColumn(
                "Dữ liệu phát hiện",
                width="large"
            ),
            "Solution": st.column_config.TextColumn(
                "Giải pháp đề xuất",
                width="large"
            ),
            "Priority": st.column_config.TextColumn(
                "Mức độ ưu tiên",
                width="small"
            )
        }
    )

# Chân trang

st.divider()

st.caption(
    "Bảng điều khiển phát thải Carbon trong Logistics Xanh | "
    "Mô-đun trực quan hóa dữ liệu"
)

