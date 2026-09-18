import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import data_loader


st.set_page_config(
    page_title="Variance Analysis",
    page_icon="📉",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    monthly = data["monthly_balances"].copy()
    expected = data["expected_results"].copy()
    income_statement = data["income_statement"].copy()
    revenue = data["revenue_by_account"].copy()
    expenses = data["expense_summary"].copy()

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

    for df in [expected, income_statement, revenue, expenses]:
        for column in df.columns:
            if column not in [
                "Metric",
                "Account_ID",
                "Account_Name",
            ]:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0)

    return (
        data,
        monthly,
        expected,
        income_statement,
        revenue,
        expenses,
    )


(
    data,
    monthly,
    expected,
    income_statement,
    revenue,
    expenses,
) = prepare_data()


st.title("📉 Variance Analysis")
st.caption(
    "Compare financial results across periods and identify "
    "material changes in revenue, profitability, expenses, and cash."
)

# ---------------------------------------------------------
# Validate available periods
# ---------------------------------------------------------

monthly = monthly.dropna(subset=["Month"]).sort_values("Month")

if monthly.empty:
    st.warning("No monthly financial data is available.")
    st.stop()

available_months = (
    monthly["Month"]
    .dt.strftime("%Y-%m")
    .unique()
    .tolist()
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Variance Filters")

current_period = st.sidebar.selectbox(
    "Current Period",
    available_months,
    index=len(available_months) - 1,
)

current_row = monthly[
    monthly["Month"].dt.strftime("%Y-%m")
    == current_period
].iloc[-1]

current_date = current_row["Month"]

prior_rows = monthly[
    monthly["Month"] < current_date
]

if prior_rows.empty:
    st.warning(
        "A prior period is required to calculate variance."
    )
    st.stop()

prior_period = st.sidebar.selectbox(
    "Comparison Period",
    prior_rows["Month"]
    .dt.strftime("%Y-%m")
    .tolist(),
    index=len(prior_rows) - 1,
)

prior_row = monthly[
    monthly["Month"].dt.strftime("%Y-%m")
    == prior_period
].iloc[-1]


# ---------------------------------------------------------
# Variance calculation
# ---------------------------------------------------------

metrics = [
    "Revenue",
    "COGS",
    "Gross_Profit",
    "Operating_Expenses",
    "Net_Income",
    "Cash",
    "AR_Net_Movement",
    "AP_Net_Movement",
]

variance_rows = []

for metric in metrics:

    current_value = float(
        current_row.get(metric, 0)
    )

    prior_value = float(
        prior_row.get(metric, 0)
    )

    variance = current_value - prior_value

    if prior_value != 0:
        variance_pct = variance / abs(prior_value)
    else:
        variance_pct = np.nan

    variance_rows.append(
        {
            "Metric": metric.replace("_", " "),
            "Current Period": current_value,
            "Prior Period": prior_value,
            "Variance": variance,
            "Variance %": variance_pct,
        }
    )

variance_df = pd.DataFrame(variance_rows)


# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

revenue_variance = variance_df.loc[
    variance_df["Metric"] == "Revenue",
    "Variance",
].iloc[0]

profit_variance = variance_df.loc[
    variance_df["Metric"] == "Net Income",
    "Variance",
].iloc[0]

expense_variance = variance_df.loc[
    variance_df["Metric"] == "Operating Expenses",
    "Variance",
].iloc[0]

cash_variance = variance_df.loc[
    variance_df["Metric"] == "Cash",
    "Variance",
].iloc[0]


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue Variance",
    f"${revenue_variance:,.2f}",
)

c2.metric(
    "Net Income Variance",
    f"${profit_variance:,.2f}",
)

c3.metric(
    "Expense Variance",
    f"${expense_variance:,.2f}",
)

c4.metric(
    "Cash Variance",
    f"${cash_variance:,.2f}",
)

st.divider()


# ---------------------------------------------------------
# Variance table
# ---------------------------------------------------------

st.subheader(
    f"Financial Variance: {current_period} vs {prior_period}"
)

display_variance = variance_df.copy()

display_variance["Current Period"] = display_variance[
    "Current Period"
].map(lambda x: f"${x:,.2f}")

display_variance["Prior Period"] = display_variance[
    "Prior Period"
].map(lambda x: f"${x:,.2f}")

display_variance["Variance"] = display_variance[
    "Variance"
].map(lambda x: f"${x:,.2f}")

display_variance["Variance %"] = display_variance[
    "Variance %"
].map(
    lambda x: (
        f"{x:.1%}"
        if pd.notna(x)
        else "N/A"
    )
)

st.dataframe(
    display_variance,
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------
# Variance chart
# ---------------------------------------------------------

st.subheader("Variance by Metric")

chart_df = variance_df[
    [
        "Metric",
        "Variance",
    ]
].set_index("Metric")

st.bar_chart(chart_df)


# ---------------------------------------------------------
# Revenue variance
# ---------------------------------------------------------

st.divider()

tab1, tab2, tab3 = st.tabs(
    [
        "Revenue",
        "Expenses",
        "Profitability",
    ]
)

with tab1:

    st.subheader("Revenue Variance by Account")

    revenue_display = revenue.copy()

    if "Amount" in revenue_display.columns:
        revenue_display["Amount"] = pd.to_numeric(
            revenue_display["Amount"],
            errors="coerce",
        ).fillna(0)

    st.dataframe(
        revenue_display.sort_values(
            "Amount",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab2:

    st.subheader("Expense Variance by Account")

    expense_display = expenses.copy()

    if "Amount" in expense_display.columns:
        expense_display["Amount"] = pd.to_numeric(
            expense_display["Amount"],
            errors="coerce",
        ).fillna(0)

    st.dataframe(
        expense_display.sort_values(
            "Amount",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab3:

    st.subheader("Profitability Comparison")

    profitability = pd.DataFrame(
        {
            "Metric": [
                "Revenue",
                "Gross Profit",
                "Operating Expenses",
                "Net Income",
            ],
            current_period: [
                current_row["Revenue"],
                current_row["Gross_Profit"],
                current_row["Operating_Expenses"],
                current_row["Net_Income"],
            ],
            prior_period: [
                prior_row["Revenue"],
                prior_row["Gross_Profit"],
                prior_row["Operating_Expenses"],
                prior_row["Net_Income"],
            ],
        }
    )

    profitability["Variance"] = (
        profitability[current_period]
        - profitability[prior_period]
    )

    st.dataframe(
        profitability,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = variance_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Variance Analysis",
    data=csv,
    file_name=f"variance_analysis_{current_period}.csv",
    mime="text/csv",
)