import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import data_loader


st.set_page_config(
    page_title="Year-over-Year",
    page_icon="🔄",
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


st.title("🔄 Year-over-Year")
st.caption(
    "Compare monthly financial performance with the same month "
    "in the previous year."
)

if monthly.empty:
    st.warning("No monthly data is available.")
    st.stop()


# ---------------------------------------------------------
# Determine available years
# ---------------------------------------------------------

years = sorted(
    monthly["Month"].dt.year.unique()
)

if len(years) < 2:
    st.warning(
        "Year-over-year analysis requires at least two years of data."
    )
    st.stop()


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("YoY Filters")

current_year = st.sidebar.selectbox(
    "Current Year",
    years[1:],
    index=len(years[1:]) - 1,
)

prior_year_options = [
    year
    for year in years
    if year < current_year
]

prior_year = st.sidebar.selectbox(
    "Comparison Year",
    prior_year_options,
    index=len(prior_year_options) - 1,
)


metric_options = [
    "Revenue",
    "COGS",
    "Gross_Profit",
    "Operating_Expenses",
    "Net_Income",
    "Cash",
]

selected_metric = st.sidebar.selectbox(
    "Metric",
    metric_options,
)


# ---------------------------------------------------------
# Create YoY dataset
# ---------------------------------------------------------

current = monthly[
    monthly["Month"].dt.year == current_year
].copy()

prior = monthly[
    monthly["Month"].dt.year == prior_year
].copy()


current["Month_Number"] = (
    current["Month"].dt.month
)

prior["Month_Number"] = (
    prior["Month"].dt.month
)

current = current.set_index(
    "Month_Number"
)

prior = prior.set_index(
    "Month_Number"
)


yoy = pd.DataFrame(
    index=range(1, 13)
)

yoy["Month"] = pd.to_datetime(
    {
        "year": current_year,
        "month": yoy.index,
        "day": 1,
    }
).strftime("%b")


yoy["Current Year"] = current[
    selected_metric
]

yoy["Prior Year"] = prior[
    selected_metric
]

yoy["Variance"] = (
    yoy["Current Year"]
    - yoy["Prior Year"]
)

yoy["YoY %"] = np.where(
    yoy["Prior Year"] != 0,
    yoy["Variance"]
    / yoy["Prior Year"].abs(),
    np.nan,
)

yoy = yoy.reset_index(
    drop=True
)

# Remove months for which both years have no data
yoy = yoy[
    ~(
        yoy["Current Year"].isna()
        & yoy["Prior Year"].isna()
    )
].copy()


# ---------------------------------------------------------
# KPI calculations
# ---------------------------------------------------------

current_total = yoy[
    "Current Year"
].fillna(0).sum()

prior_total = yoy[
    "Prior Year"
].fillna(0).sum()

total_variance = (
    current_total
    - prior_total
)

if prior_total != 0:
    total_yoy_pct = (
        total_variance
        / abs(prior_total)
    )
else:
    total_yoy_pct = np.nan


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    f"{current_year} Total",
    f"${current_total:,.2f}",
)

c2.metric(
    f"{prior_year} Total",
    f"${prior_total:,.2f}",
)

c3.metric(
    "YoY Variance",
    f"${total_variance:,.2f}",
)

c4.metric(
    "YoY Change",
    (
        f"{total_yoy_pct:.1%}"
        if pd.notna(total_yoy_pct)
        else "N/A"
    ),
)

st.divider()


# ---------------------------------------------------------
# Main comparison
# ---------------------------------------------------------

st.subheader(
    f"{selected_metric.replace('_', ' ')}: "
    f"{current_year} vs {prior_year}"
)

display_yoy = yoy.copy()

display_yoy[
    "Current Year"
] = display_yoy[
    "Current Year"
].map(
    lambda x: (
        f"${x:,.2f}"
        if pd.notna(x)
        else "N/A"
    )
)

display_yoy[
    "Prior Year"
] = display_yoy[
    "Prior Year"
].map(
    lambda x: (
        f"${x:,.2f}"
        if pd.notna(x)
        else "N/A"
    )
)

display_yoy[
    "Variance"
] = display_yoy[
    "Variance"
].map(
    lambda x: (
        f"${x:,.2f}"
        if pd.notna(x)
        else "N/A"
    )
)

display_yoy[
    "YoY %"
] = display_yoy[
    "YoY %"
].map(
    lambda x: (
        f"{x:.1%}"
        if pd.notna(x)
        else "N/A"
    )
)

st.dataframe(
    display_yoy,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Comparison chart
# ---------------------------------------------------------

st.subheader("Year-over-Year Comparison")

chart_data = yoy[
    [
        "Month",
        "Current Year",
        "Prior Year",
    ]
].copy()

chart_data = chart_data.set_index(
    "Month"
)

chart_data.columns = [
    str(current_year),
    str(prior_year),
]

st.line_chart(
    chart_data
)


# ---------------------------------------------------------
# Variance chart
# ---------------------------------------------------------

st.subheader("Monthly YoY Variance")

variance_chart = yoy[
    [
        "Month",
        "Variance",
    ]
].set_index("Month")

st.bar_chart(
    variance_chart
)


# ---------------------------------------------------------
# Full financial YoY
# ---------------------------------------------------------

st.divider()

st.subheader("Full Financial Year-over-Year")

financial_metrics = [
    "Revenue",
    "COGS",
    "Gross_Profit",
    "Operating_Expenses",
    "Net_Income",
    "Cash",
]

financial_rows = []

for metric in financial_metrics:

    current_total_metric = current[
        metric
    ].fillna(0).sum()

    prior_total_metric = prior[
        metric
    ].fillna(0).sum()

    variance = (
        current_total_metric
        - prior_total_metric
    )

    if prior_total_metric != 0:
        variance_pct = (
            variance
            / abs(prior_total_metric)
        )
    else:
        variance_pct = np.nan

    financial_rows.append(
        {
            "Metric": metric.replace(
                "_",
                " ",
            ),
            str(current_year): current_total_metric,
            str(prior_year): prior_total_metric,
            "Variance": variance,
            "YoY %": variance_pct,
        }
    )

financial_df = pd.DataFrame(
    financial_rows
)

display_financial = financial_df.copy()

for column in [
    str(current_year),
    str(prior_year),
    "Variance",
]:
    display_financial[column] = (
        display_financial[column]
        .map(
            lambda x: f"${x:,.2f}"
        )
    )

display_financial["YoY %"] = (
    display_financial["YoY %"]
    .map(
        lambda x: (
            f"{x:.1%}"
            if pd.notna(x)
            else "N/A"
        )
    )
)

st.dataframe(
    display_financial,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Available data note
# ---------------------------------------------------------

st.divider()

st.info(
    f"YoY analysis currently compares {prior_year} "
    f"against {current_year}. The workbook contains "
    f"{len(years)} years of monthly data: "
    + ", ".join(str(year) for year in years)
    + "."
)


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

csv = financial_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Year-over-Year Analysis",
    data=csv,
    file_name=(
        f"yoy_analysis_{current_year}_vs_{prior_year}.csv"
    ),
    mime="text/csv",
)
