import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Income Statement",
    page_icon="📈",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    income_statement = data["income_statement"].copy()
    monthly = data["monthly_balances"].copy()
    revenue = data["revenue_by_account"].copy()
    expenses = data["expense_summary"].copy()

    for df in [income_statement, monthly, revenue, expenses]:
        for column in df.columns:
            if column not in ["Metric", "Account_Name", "Account_ID", "Month"]:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0)

    monthly["Month"] = pd.to_datetime(
        monthly["Month"],
        errors="coerce",
    )

    return data, income_statement, monthly, revenue, expenses


(
    data,
    income_statement,
    monthly,
    revenue,
    expenses,
) = prepare_data()


st.title("📈 Income Statement")
st.caption(
    "Review revenue, cost of goods sold, operating expenses, "
    "gross profit, and net income."
)

# ---------------------------------------------------------
# Period Selection
# ---------------------------------------------------------

st.sidebar.header("Report Filters")

available_months = (
    monthly["Month"]
    .dropna()
    .sort_values()
    .dt.strftime("%Y-%m")
    .unique()
    .tolist()
)

selected_month = st.sidebar.selectbox(
    "Reporting Period",
    ["Latest"] + available_months,
)

if selected_month == "Latest" and not monthly.empty:
    selected_period = monthly.sort_values("Month").iloc[-1]
elif selected_month != "Latest":
    selected_period = monthly[
        monthly["Month"].dt.strftime("%Y-%m")
        == selected_month
    ].iloc[-1]
else:
    selected_period = None


# ---------------------------------------------------------
# Financial Values
# ---------------------------------------------------------

if selected_period is not None:

    revenue_amount = selected_period.get("Revenue", 0)
    cogs_amount = selected_period.get("COGS", 0)
    gross_profit = selected_period.get("Gross_Profit", 0)
    operating_expenses = selected_period.get(
        "Operating_Expenses",
        0,
    )
    net_income = selected_period.get("Net_Income", 0)

else:

    revenue_amount = income_statement[
        income_statement["Metric"]
        .astype(str)
        .str.contains("revenue", case=False, na=False)
    ]["Amount"].sum()

    cogs_amount = 0
    gross_profit = 0
    operating_expenses = 0
    net_income = income_statement[
        income_statement["Metric"]
        .astype(str)
        .str.contains("net income", case=False, na=False)
    ]["Amount"].sum()


# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"${revenue_amount:,.2f}",
)

c2.metric(
    "COGS",
    f"${cogs_amount:,.2f}",
)

c3.metric(
    "Gross Profit",
    f"${gross_profit:,.2f}",
)

c4.metric(
    "Net Income",
    f"${net_income:,.2f}",
)

st.divider()

# ---------------------------------------------------------
# Income Statement
# ---------------------------------------------------------

st.subheader("Income Statement")

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

statement = pd.DataFrame(
    {
        "Line Item": [
            "Revenue",
            "Cost of Goods Sold",
            "Gross Profit",
            "Operating Expenses",
            "Net Income",
        ],
        "Amount": [
            revenue_amount,
            -cogs_amount,
            gross_profit,
            -operating_expenses,
            net_income,
        ],
    }
)

statement["Amount"] = statement["Amount"].round(2)

st.dataframe(
    statement,
    use_container_width=True,
    hide_index=True,
)

m1, m2 = st.columns(2)

m1.metric(
    "Gross Margin",
    f"{gross_margin:.1%}",
)

m2.metric(
    "Net Margin",
    f"{net_margin:.1%}",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Revenue",
        "Expenses",
        "Monthly Trend",
    ]
)

with tab1:

    st.subheader("Revenue by Account")

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

    if "Account_Name" in revenue_display.columns:
        chart = revenue_display[
            ["Account_Name", "Amount"]
        ].set_index("Account_Name")

        st.bar_chart(chart)

with tab2:

    st.subheader("Expense Summary")

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

    if "Account_Name" in expense_display.columns:
        chart = expense_display[
            ["Account_Name", "Amount"]
        ].set_index("Account_Name")

        st.bar_chart(chart)

with tab3:

    st.subheader("Monthly Income Statement Trend")

    trend_columns = [
        "Month",
        "Revenue",
        "COGS",
        "Gross_Profit",
        "Operating_Expenses",
        "Net_Income",
    ]

    trend = monthly[
        [
            column
            for column in trend_columns
            if column in monthly.columns
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

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = statement.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Income Statement",
    data=csv,
    file_name="income_statement.csv",
    mime="text/csv",
)

