import pandas as pd
import streamlit as st
from scipy import stats


def load_clean_data3(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    return df


def analyze_traffic_impact(df: pd.DataFrame) -> dict:
    """Tính toán mức tăng phát thải theo điều kiện giao thông."""
    traffic_avg = df.groupby('Traffic_Conditions')[
        'Carbon_Emission_kgCO2e'
    ].mean()

    low_val = traffic_avg.get('Low', 0)
    normal_val = traffic_avg.get('Normal', 0)
    high_val = traffic_avg.get('High', 0)
    severe_val = traffic_avg.get('Severe Congestion', 0)

    pct_normal = ((normal_val - low_val) / low_val) * 100 if low_val != 0 else 0
    pct_high = ((high_val - low_val) / low_val) * 100 if low_val != 0 else 0
    pct_severe = ((severe_val - low_val) / low_val) * 100 if low_val != 0 else 0

    return {
        'avg_emissions': traffic_avg.to_dict(),
        'pct_increase_normal': pct_normal,
        'pct_increase_high': pct_high,
        'pct_increase_severe': pct_severe,
    }


def analyze_route_share(df: pd.DataFrame) -> dict:
    """Tính tỷ trọng phát thải giữa các loại tuyến."""
    total_emission = df['Carbon_Emission_kgCO2e'].sum()
    route_sum = df.groupby('Route_Type')['Carbon_Emission_kgCO2e'].sum()

    urban_val = route_sum.get('Urban Last Mile', 0)
    intercity_val = route_sum.get('Inter-City', 0)

    urban_pct = (urban_val / total_emission) * 100 if total_emission != 0 else 0
    intercity_pct = (
        (intercity_val / total_emission) * 100 if total_emission != 0 else 0
    )

    if intercity_val != 0:
        urban_vs_intercity_pct = (
            (urban_val - intercity_val) / intercity_val
        ) * 100
    else:
        urban_vs_intercity_pct = 0

    return {
        'urban_pct': urban_pct,
        'intercity_pct': intercity_pct,
        'urban_vs_intercity_pct': urban_vs_intercity_pct,
        'route_totals': route_sum.to_dict(),
    }


def run_traffic_anova_test(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Kiểm định ANOVA sự khác biệt CO2 theo điều kiện giao thông."""
    groups = [
        group['Carbon_Emission_kgCO2e'].dropna().values
        for _, group in df.groupby('Traffic_Conditions')
    ]

    groups = [
        group for group in groups
        if len(group) > 0
    ]

    if len(groups) < 2:
        return {
            'f_statistic': None,
            'p_value': None,
            'alpha': alpha,
            'is_significant': False,
            'conclusion': 'Không đủ số nhóm để thực hiện kiểm định ANOVA.'
        }

    f_stat, p_value = stats.f_oneway(*groups)
    is_significant = p_value < alpha

    if is_significant:
        conclusion = (
            'Có sự khác biệt có ý nghĩa thống kê về lượng CO2 giữa các điều'
            ' kiện giao thông.'
        )
    else:
        conclusion = (
            'Chưa đủ bằng chứng thống kê để kết luận các điều kiện giao thông'
            ' tạo ra sự khác biệt về CO2.'
        )

    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'alpha': alpha,
        'is_significant': is_significant,
        'conclusion': conclusion,
    }

def plot_traffic_emission(df: pd.DataFrame):
    """Hiển thị CO2 trung bình theo điều kiện giao thông."""

    result = analyze_traffic_impact(df)

    chart_data = pd.DataFrame(
        list(result['avg_emissions'].items()),
        columns=[
            'Traffic_Conditions',
            'Average_CO2'
        ]
    )

    st.bar_chart(
        chart_data,
        x='Traffic_Conditions',
        y='Average_CO2'
    )


def plot_route_emission(df: pd.DataFrame):
    """Hiển thị tổng CO2 theo loại tuyến."""

    result = analyze_route_share(df)

    chart_data = pd.DataFrame(
        list(result['route_totals'].items()),
        columns=[
            'Route_Type',
            'Total_CO2'
        ]
    )

    st.bar_chart(
        chart_data,
        x='Route_Type',
        y='Total_CO2'
    )