import pandas as pd
import plotly.express as px


# LOAD DATA

def load_clean_data2(path):
    """
    Load cleaned data from CSV file
    and convert Date to datetime format.
    """

    data = pd.read_csv(path)

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    )

    return data


# KPI SUMMARY

def get_summary(data):
    """
    Calculate basic KPI indicators.
    """

    summary = {
        "Total CO2":
            round(
                data["Carbon_Emission_kgCO2e"].sum(),
                2
            ),

        "Average CO2/trip":
            round(
                data["Carbon_Emission_kgCO2e"].mean(),
                2
            ),

        "Total Distance":
            round(
                data["Distance_KM"].sum(),
                2
            ),

        "Total Package":
            round(
                data["Package_Weight_KG"].sum(),
                2
            ),

        "Total Trips":
            len(data)
    }

    return summary


# 1. DAILY CO2 TREND

def daily_emission_chart(data):
    """
    Display total CO2 emission by day.
    """

    daily = (
        data
        .groupby("Date")["Carbon_Emission_kgCO2e"]
        .sum()
        .reset_index()
        .sort_values("Date")
    )

    fig = px.line(
        daily,
        x="Date",
        y="Carbon_Emission_kgCO2e",
        title="Xu hướng phát thải Carbon hằng ngày",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Thời gian",
        yaxis_title="CO2 Emission (kgCO2e)"
    )

    return fig


# 2. WEEKLY CO2 TREND

def weekly_emission_chart(data):
    """
    Display total CO2 emission by week.
    """

    weekly = (
        data
        .set_index("Date")
        ["Carbon_Emission_kgCO2e"]
        .resample("W")
        .sum()
        .reset_index()
    )

    fig = px.bar(
        weekly,
        x="Date",
        y="Carbon_Emission_kgCO2e",
        title="Xu hướng phát thải Carbon theo tuần"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Tuần",
        yaxis_title="CO2 Emission (kgCO2e)"
    )

    return fig


# 3. MONTHLY CO2 TREND

def monthly_emission_chart(data):
    """
    Display total CO2 emission by month.
    """

    monthly = (
        data
        .set_index("Date")
        ["Carbon_Emission_kgCO2e"]
        .resample("ME")
        .sum()
        .reset_index()
    )

    fig = px.line(
        monthly,
        x="Date",
        y="Carbon_Emission_kgCO2e",
        title="Xu hướng phát thải Carbon theo tháng",
        markers=True
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Tháng",
        yaxis_title="CO2 Emission (kgCO2e)"
    )

    return fig


# 4. TRIPS BY ORIGIN FACILITY

def origin_volume_chart(data):
    """
    Display number of trips from each origin facility.
    """

    origin_volume = (
        data["Origin_Facility"]
        .value_counts()
        .reset_index()
    )

    origin_volume.columns = [
        "Origin_Facility",
        "Trip_Count"
    ]

    origin_volume = origin_volume.sort_values(
        "Trip_Count",
        ascending=False
    )

    fig = px.bar(
        origin_volume,
        x="Origin_Facility",
        y="Trip_Count",
        title="Số lượng chuyến bởi trạm xuất phát",
        text_auto=True
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Trạm xuất phát",
        yaxis_title="Số lượng chuyến"
    )

    return fig


# 5. CO2 BY ORIGIN FACILITY

def origin_chart(data):
    """
    Display total CO2 emission by origin facility.
    """

    origin = (
        data
        .groupby("Origin_Facility")
        ["Carbon_Emission_kgCO2e"]
        .sum()
        .reset_index()
        .sort_values(
            "Carbon_Emission_kgCO2e",
            ascending=False
        )
    )

    fig = px.bar(
        origin,
        x="Origin_Facility",
        y="Carbon_Emission_kgCO2e",
        title="Phát thải Carbon từ trạm xuất phát",
        text_auto=True
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Trạm xuất phát",
        yaxis_title="CO2 Emission (kgCO2e)"
    )

    return fig


# 6. VEHICLE DISTRIBUTION

def vehicle_chart(data):
    """
    Display the distribution of vehicle types.
    """

    vehicle = (
        data["Vehicle_Type"]
        .value_counts()
        .reset_index()
    )

    vehicle.columns = [
        "Vehicle_Type",
        "Count"
    ]

    fig = px.pie(
        vehicle,
        names="Vehicle_Type",
        values="Count",
        title="Sự phân bố phương tiện"
    )

    fig.update_layout(
        template="plotly_white"
    )

    return fig


# 7. ECO VS NON-ECO

def eco_chart(data):
    """
    Compare average CO2 emission
    between eco-friendly and non-eco-friendly vehicles.
    """

    eco = (
        data
        .groupby("Is_Eco_Friendly")
        ["Carbon_Emission_kgCO2e"]
        .mean()
        .reset_index()
    )

    eco["Is_Eco_Friendly"] = eco[
        "Is_Eco_Friendly"
    ].map({
        0: "Non-Eco Friendly",
        1: "Eco Friendly"
    })

    fig = px.bar(
        eco,
        x="Is_Eco_Friendly",
        y="Carbon_Emission_kgCO2e",
        title="Trung bình CO2: Eco vs Non-Eco Vehicle",
        text_auto=True
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Loại phương tiện",
        yaxis_title="Trung bình CO2 (kgCO2e)"
    )

    return fig