import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Management Reporting",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    monthly = data["monthly_balances"].copy()
    revenue = data["revenue_by_account"].copy()
    expenses = data["expense_summary"].copy()
    ar_aging = data["ar_aging"].copy()
    income_statement = data["income_statement"].copy()
    expected = data["expected_results"].copy()

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

    for df in [
        revenue,
        expenses,
        ar_aging,
        income_statement,
        expected,
    ]:
        for column in df.columns:
            if column not in [
                "Metric",
                "Account_ID",
                "Account_Name",
                "Aging_Bucket",
            ]:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0)

    return (
        data,
        monthly,
        revenue,
        expenses,
        ar_aging,
        income_statement,
        expected,
    )


(
    data,
    monthly,
    revenue,
    expenses,
    ar_aging,
    income_statement,
    expected,
) = prepare_data()


st.title("📊 Management Reporting")
st.caption(
    "Executive-level financial reporting across revenue, profitability, "
    "cash, expenses, and receivables."
)

# ---------------------------------------------------------
# Period
# ---------------------------------------------------------

st.sidebar.header("Management Report")

months = (
    monthly["Month"]
    .dropna()
    .sort_values()
    .dt.strftime("%Y-%m")
    .unique()
    .tolist()
)

selected_month = st.sidebar.selectbox(
    "Reporting Period",
    ["Latest"] + months,
)

if selected_month == "Latest" and not monthly.empty:
    current = monthly.sort_values("Month").iloc[-1]

    current_index = (
        monthly.sort_values("Month")
        .index[-1]
    )

elif selected_month != "Latest":

    current = monthly[
        monthly["Month"].dt.strftime("%Y-%m")
        == selected_month
    ].iloc[-1]

    current_index = current.name

else:
    current = None
    current_index = None


# ---------------------------------------------------------
# Current Period
# ---------------------------------------------------------

if current is not None:

    revenue_amount = current["Revenue"]
    gross_profit = current["Gross_Profit"]
    operating_expenses = current["Operating_Expenses"]
    net_income = current["Net_Income"]
    cash = current["Cash"]

else:

    revenue_amount = 0
    gross_profit = 0
    operating_expenses = 0
    net_income = 0
    cash = 0


gross_margin = (
    gross_profit / revenue_amount
    if revenue_amount
    else 0
)

net_margin = (
    net_income / revenue_amount
    if revenue_amount
    else 0
)


# ---------------------------------------------------------
# Executive KPIs
# ---------------------------------------------------------

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Revenue",
    f"${revenue_amount:,.0f}",
)

c2.metric(
    "Gross Profit",
    f"${gross_profit:,.0f}",
)

c3.metric(
    "Gross Margin",
    f"{gross_margin:.1%}",
)

c4.metric(
    "Net Income",
    f"${net_income:,.0f}",
)

c5.metric(
    "Cash",
    f"${cash:,.0f}",
)

st.divider()

# ---------------------------------------------------------
# Management Dashboard
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Executive Summary",
        "Profitability",
        "Revenue & Expenses",
        "Working Capital",
    ]
)

with tab1:

    st.subheader("Executive Summary")

    summary = pd.DataFrame(
        {
            "Metric": [
                "Revenue",
                "Gross Profit",
                "Operating Expenses",
                "Net Income",
                "Cash",
            ],
            "Amount": [
                revenue_amount,
                gross_profit,
                operating_expenses,
                net_income,
                cash,
            ],
        }
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Monthly Financial Performance")

    trend_columns = [
        "Month",
        "Revenue",
        "Gross_Profit",
        "Operating_Expenses",
        "Net_Income",
        "Cash",
    ]

    trend = monthly[
        [
            c
            for c in trend_columns
            if c in monthly.columns
        ]
    ].sort_values("Month")

    st.dataframe(
        trend,
        use_container_width=True,
        hide_index=True,
    )

    if not trend.empty:
        st.line_chart(
            trend.set_index("Month")
        )


with tab2:

    st.subheader("Profitability Analysis")

    profitability = pd.DataFrame(
        {
            "Metric": [
                "Revenue",
                "COGS",
                "Gross Profit",
                "Gross Margin",
                "Operating Expenses",
                "Net Income",
                "Net Margin",
            ],
            "Value": [
                revenue_amount,
                current["COGS"] if current is not None else 0,
                gross_profit,
                gross_margin,
                operating_expenses,
                net_income,
                net_margin,
            ],
        }
    )

    st.dataframe(
        profitability,
        use_container_width=True,
        hide_index=True,
    )

    profit_chart = monthly[
        [
            "Month",
            "Gross_Profit",
            "Net_Income",
        ]
    ].sort_values("Month")

    st.line_chart(
        profit_chart.set_index("Month")
    )


with tab3:

    st.subheader("Revenue by Account")

    revenue_display = revenue.copy()

    st.dataframe(
        revenue_display.sort_values(
            "Amount",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    if not revenue_display.empty:
        revenue_chart = revenue_display[
            [
                "Account_Name",
                "Amount",
            ]
        ].set_index("Account_Name")

        st.bar_chart(
            revenue_chart
        )

    st.subheader("Expense Summary")

    expense_display = expenses.copy()

    st.dataframe(
        expense_display.sort_values(
            "Amount",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    if not expense_display.empty:
        expense_chart = expense_display[
            [
                "Account_Name",
                "Amount",
            ]
        ].set_index("Account_Name")

        st.bar_chart(
            expense_chart
        )


with tab4:

    st.subheader("Accounts Receivable Aging")

    aging = ar_aging.copy()

    total_ar = (
        aging["Outstanding_Balance"].sum()
        if "Outstanding_Balance" in aging.columns
        else 0
    )

    st.metric(
        "Total Outstanding AR",
        f"${total_ar:,.2f}",
    )

    st.dataframe(
        aging,
        use_container_width=True,
        hide_index=True,
    )

    if (
        not aging.empty
        and "Outstanding_Balance" in aging.columns
    ):

        aging_chart = aging[
            [
                "Aging_Bucket",
                "Outstanding_Balance",
            ]
        ].set_index("Aging_Bucket")

        st.bar_chart(
            aging_chart
        )

# ---------------------------------------------------------
# Management Commentary
# ---------------------------------------------------------

st.divider()

st.subheader("Management Review")

col1, col2 = st.columns(2)

with col1:

    if net_income >= 0:
        st.success(
            f"Current-period net income is "
            f"${net_income:,.2f}."
        )
    else:
        st.warning(
            f"Current-period net income is "
            f"negative at ${net_income:,.2f}."
        )

    if gross_margin >= 0.5:
        st.info(
            f"Gross margin is {gross_margin:.1%}."
        )
    else:
        st.warning(
            f"Gross margin is {gross_margin:.1%}."
        )

with col2:

    if total_ar > 0:
        st.info(
            f"Accounts receivable outstanding: "
            f"${total_ar:,.2f}."
        )

    st.info(
        f"Operating expenses for the selected period: "
        f"${operating_expenses:,.2f}."
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = summary.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Management Summary",
    data=csv,
    file_name="management_reporting.csv",
    mime="text/csv",
)