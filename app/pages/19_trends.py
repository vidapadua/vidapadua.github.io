import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Trends",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    monthly = data["monthly_balances"].copy()

    monthly["Month"] = pd.to_datetime(
        monthly["Month"],
        errors="coerce",
    )

    numeric_columns = [
        "Revenue",
        "COGS",
        "Gross_Profit",
        "Operating_Expenses",
        "Net_Income",
        "Cash",
        "AR_Net_Movement",
        "AP_Net_Movement",
    ]

    for column in numeric_columns:
        if column in monthly.columns:
            monthly[column] = pd.to_numeric(
                monthly[column],
                errors="coerce",
            ).fillna(0)

    return data, monthly


data, monthly = prepare_data()

monthly = (
    monthly
    .dropna(subset=["Month"])
    .sort_values("Month")
    .copy()
)


st.title("📈 Trends")
st.caption(
    "Analyze monthly financial trends across the available "
    "two-year reporting history."
)

if monthly.empty:
    st.warning("No monthly data is available.")
    st.stop()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Trend Filters")

years = sorted(
    monthly["Month"].dt.year.unique()
)

selected_years = st.sidebar.multiselect(
    "Years",
    years,
    default=years,
)

trend_data = monthly[
    monthly["Month"].dt.year.isin(selected_years)
].copy()


metric_options = [
    "Revenue",
    "COGS",
    "Gross_Profit",
    "Operating_Expenses",
    "Net_Income",
    "Cash",
]

selected_metric = st.sidebar.selectbox(
    "Primary Metric",
    metric_options,
)


# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------

latest = monthly.iloc[-1]

previous = (
    monthly.iloc[-2]
    if len(monthly) > 1
    else latest
)

latest_revenue = latest["Revenue"]
latest_profit = latest["Net_Income"]
latest_cash = latest["Cash"]

revenue_change = (
    latest_revenue
    - previous["Revenue"]
)

profit_change = (
    latest_profit
    - previous["Net_Income"]
)

cash_change = (
    latest_cash
    - previous["Cash"]
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Latest Revenue",
    f"${latest_revenue:,.2f}",
)

c2.metric(
    "Latest Net Income",
    f"${latest_profit:,.2f}",
)

c3.metric(
    "Latest Cash",
    f"${latest_cash:,.2f}",
)

c4.metric(
    "Revenue Change",
    f"${revenue_change:,.2f}",
)

st.divider()


# ---------------------------------------------------------
# Primary trend
# ---------------------------------------------------------

st.subheader(
    f"{selected_metric.replace('_', ' ')} Trend"
)

trend_chart = trend_data[
    [
        "Month",
        selected_metric,
    ]
].set_index("Month")

st.line_chart(
    trend_chart
)


# ---------------------------------------------------------
# Financial Trends
# ---------------------------------------------------------

st.subheader("Financial Performance Trends")

trend_columns = [
    "Revenue",
    "COGS",
    "Gross_Profit",
    "Operating_Expenses",
    "Net_Income",
]

available_columns = [
    column
    for column in trend_columns
    if column in trend_data.columns
]

financial_chart = trend_data[
    ["Month"] + available_columns
].set_index("Month")

st.line_chart(
    financial_chart
)


# ---------------------------------------------------------
# Cash Trend
# ---------------------------------------------------------

st.subheader("Cash Trend")

cash_chart = trend_data[
    [
        "Month",
        "Cash",
    ]
].set_index("Month")

st.area_chart(
    cash_chart
)


# ---------------------------------------------------------
# Trend table
# ---------------------------------------------------------

st.divider()

st.subheader("Monthly Trend Data")

display_columns = [
    "Month",
    "Revenue",
    "COGS",
    "Gross_Profit",
    "Operating_Expenses",
    "Net_Income",
    "Cash",
    "AR_Net_Movement",
    "AP_Net_Movement",
]

st.dataframe(
    trend_data[
        [
            c
            for c in display_columns
            if c in trend_data.columns
        ]
    ].sort_values(
        "Month",
        ascending=False,
    ),
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Growth calculations
# ---------------------------------------------------------

st.divider()

st.subheader("Month-to-Month Movement")

movement = trend_data.copy()

movement["Revenue Change"] = (
    movement["Revenue"].diff()
)

movement["Revenue Change %"] = (
    movement["Revenue"]
    .pct_change()
)

movement["Net Income Change"] = (
    movement["Net_Income"].diff()
)

movement["Net Income Change %"] = (
    movement["Net_Income"]
    .pct_change()
)

st.dataframe(
    movement[
        [
            "Month",
            "Revenue Change",
            "Revenue Change %",
            "Net Income Change",
            "Net Income Change %",
        ]
    ].sort_values(
        "Month",
        ascending=False,
    ),
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

csv = trend_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Trend Analysis",
    data=csv,
    file_name="financial_trends.csv",
    mime="text/csv",
)
