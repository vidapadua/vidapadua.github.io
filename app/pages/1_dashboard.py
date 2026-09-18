import streamlit as st
import pandas as pd


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Dashboard | Peak Accounting System",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# LOAD DATA
# =========================================================

from src.data_loader import data_loader

data = data_loader()

monthly = data["monthly_balances"].copy()
income_statement = data["income_statement"].copy()
revenue = data["revenue_by_account"].copy()
expenses = data["expense_summary"].copy()
ar_aging = data["ar_aging"].copy()
trial_balance = data["trial_balance"].copy()
validation = data["validation_results"].copy()
gl = data["gl"].copy()
bank = data["bank"].copy()
ap = data["ap_invoices"].copy()
ar = data["ar_invoices"].copy()


# =========================================================
# HELPERS
# =========================================================

def money(value):
    if pd.isna(value):
        return "$0"
    return f"${value:,.0f}"


def money_1(value):
    if pd.isna(value):
        return "$0.0K"

    value = float(value)

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"

    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"

    return f"${value:,.0f}"


def numeric_columns(df):
    return df.select_dtypes(include="number").columns.tolist()


# =========================================================
# CLEAN / PREPARE DATA
# =========================================================

# Monthly balances
if "Month" in monthly.columns:
    monthly["Month"] = pd.to_datetime(
        monthly["Month"],
        errors="coerce",
    )

    monthly = monthly.sort_values("Month")


# Income statement
income_lookup = {}

if not income_statement.empty:
    income_lookup = (
        income_statement
        .set_index("Metric")["Amount"]
        .to_dict()
    )


revenue_total = float(
    income_lookup.get("Revenue", 0)
)

cogs_total = float(
    income_lookup.get("COGS", 0)
)

gross_profit = float(
    income_lookup.get("Gross Profit", 0)
)

operating_expenses = float(
    income_lookup.get("Operating Expenses", 0)
)

net_income = float(
    income_lookup.get("Net Income", 0)
)


# Fallback calculations if the income statement
# uses slightly different metric names.
if revenue_total == 0 and "Revenue" in monthly.columns:
    revenue_total = monthly["Revenue"].sum()

if cogs_total == 0 and "COGS" in monthly.columns:
    cogs_total = monthly["COGS"].sum()

if gross_profit == 0 and "Gross_Profit" in monthly.columns:
    gross_profit = monthly["Gross_Profit"].sum()

if operating_expenses == 0 and "Operating_Expenses" in monthly.columns:
    operating_expenses = monthly["Operating_Expenses"].sum()

if net_income == 0 and "Net_Income" in monthly.columns:
    net_income = monthly["Net_Income"].sum()


# =========================================================
# HEADER
# =========================================================

st.title("📊 Accounting Dashboard")

st.caption(
    "A high-level view of financial performance, liquidity, "
    "working capital, activity, and accounting controls."
)


# =========================================================
# PERIOD FILTER
# =========================================================

if not monthly.empty and monthly["Month"].notna().any():

    available_months = monthly["Month"].dropna().sort_values()

    selected_month = st.selectbox(
        "Reporting Period",
        available_months,
        index=len(available_months) - 1,
        format_func=lambda x: x.strftime("%B %Y"),
    )

    current_month = monthly[
        monthly["Month"] == selected_month
    ]

else:
    selected_month = None
    current_month = monthly


# =========================================================
# CURRENT PERIOD VALUES
# =========================================================

if not current_month.empty:

    row = current_month.iloc[-1]

    current_revenue = float(
        row.get("Revenue", 0)
    )

    current_gross_profit = float(
        row.get("Gross_Profit", 0)
    )

    current_net_income = float(
        row.get("Net_Income", 0)
    )

    current_cash = float(
        row.get("Cash", 0)
    )

    current_ar_movement = float(
        row.get("AR_Net_Movement", 0)
    )

    current_ap_movement = float(
        row.get("AP_Net_Movement", 0)
    )

else:

    current_revenue = 0
    current_gross_profit = 0
    current_net_income = 0
    current_cash = 0
    current_ar_movement = 0
    current_ap_movement = 0


# =========================================================
# KPI CARDS
# =========================================================

st.subheader("Financial Snapshot")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric(
        "Revenue",
        money_1(current_revenue),
    )

with k2:
    st.metric(
        "Gross Profit",
        money_1(current_gross_profit),
    )

with k3:
    st.metric(
        "Net Income",
        money_1(current_net_income),
    )

with k4:
    st.metric(
        "Cash",
        money_1(current_cash),
    )

with k5:
    st.metric(
        "GL Transactions",
        f"{len(gl):,}",
    )


# =========================================================
# PROFITABILITY METRICS
# =========================================================

if current_revenue:

    gross_margin = (
        current_gross_profit / current_revenue
    ) * 100

    net_margin = (
        current_net_income / current_revenue
    ) * 100

else:

    gross_margin = 0
    net_margin = 0


m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "Gross Margin",
        f"{gross_margin:.1f}%",
    )

with m2:
    st.metric(
        "Net Margin",
        f"{net_margin:.1f}%",
    )

with m3:
    st.metric(
        "Open AR",
        money_1(
            ar["Outstanding_Balance"].sum()
            if "Outstanding_Balance" in ar.columns
            else 0
        ),
    )


st.divider()


# =========================================================
# REVENUE / PROFIT TREND
# =========================================================

st.subheader("Financial Performance")

left, right = st.columns(2)

with left:

    st.markdown("#### Revenue & Profit Trend")

    if not monthly.empty:

        chart_data = monthly[
            [
                c
                for c in [
                    "Month",
                    "Revenue",
                    "Gross_Profit",
                    "Net_Income",
                ]
                if c in monthly.columns
            ]
        ].copy()

        if "Month" in chart_data.columns:
            chart_data = chart_data.set_index("Month")

        st.line_chart(
            chart_data,
            height=330,
        )

    else:

        st.info("No monthly financial data available.")


with right:

    st.markdown("#### Monthly Net Income")

    if not monthly.empty and "Net_Income" in monthly.columns:

        profit_chart = monthly[
            ["Month", "Net_Income"]
        ].copy()

        profit_chart = profit_chart.set_index("Month")

        st.bar_chart(
            profit_chart,
            height=330,
        )

    else:

        st.info("No net income data available.")


# =========================================================
# REVENUE / EXPENSE BREAKDOWN
# =========================================================

st.divider()

st.subheader("Revenue & Expense Breakdown")

left, right = st.columns(2)


with left:

    st.markdown("#### Revenue by Account")

    if not revenue.empty:

        revenue_display = revenue.copy()

        if "Amount" in revenue_display.columns:
            revenue_display = revenue_display.sort_values(
                "Amount",
                ascending=False,
            )

        if {
            "Account_Name",
            "Amount",
        }.issubset(revenue_display.columns):

            revenue_chart = (
                revenue_display[
                    ["Account_Name", "Amount"]
                ]
                .set_index("Account_Name")
            )

            st.bar_chart(
                revenue_chart,
                height=330,
            )

        st.dataframe(
            revenue_display,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No revenue data available.")


with right:

    st.markdown("#### Expenses by Account")

    if not expenses.empty:

        expense_display = expenses.copy()

        if "Amount" in expense_display.columns:
            expense_display = expense_display.sort_values(
                "Amount",
                ascending=False,
            )

        if {
            "Account_Name",
            "Amount",
        }.issubset(expense_display.columns):

            expense_chart = (
                expense_display[
                    ["Account_Name", "Amount"]
                ]
                .set_index("Account_Name")
            )

            st.bar_chart(
                expense_chart,
                height=330,
            )

        st.dataframe(
            expense_display,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No expense data available.")


# =========================================================
# WORKING CAPITAL
# =========================================================

st.divider()

st.subheader("Working Capital & Liquidity")

w1, w2, w3 = st.columns(3)


# ---------------------------------------------------------
# AR
# ---------------------------------------------------------

with w1:

    st.markdown("#### Accounts Receivable")

    ar_balance = (
        ar["Outstanding_Balance"].sum()
        if "Outstanding_Balance" in ar.columns
        else 0
    )

    st.metric(
        "Outstanding AR",
        money_1(ar_balance),
    )

    if not ar_aging.empty:

        if {
            "Aging_Bucket",
            "Outstanding_Balance",
        }.issubset(ar_aging.columns):

            aging_chart = (
                ar_aging[
                    [
                        "Aging_Bucket",
                        "Outstanding_Balance",
                    ]
                ]
                .set_index("Aging_Bucket")
            )

            st.bar_chart(
                aging_chart,
                height=250,
            )


# ---------------------------------------------------------
# AP
# ---------------------------------------------------------

with w2:

    st.markdown("#### Accounts Payable")

    ap_balance = (
        ap["Outstanding_Balance"].sum()
        if "Outstanding_Balance" in ap.columns
        else 0
    )

    st.metric(
        "Outstanding AP",
        money_1(ap_balance),
    )

    if "Status" in ap.columns:

        ap_status = (
            ap["Status"]
            .value_counts()
            .rename("Invoices")
        )

        st.bar_chart(
            ap_status,
            height=250,
        )


# ---------------------------------------------------------
# CASH
# ---------------------------------------------------------

with w3:

    st.markdown("#### Cash Position")

    st.metric(
        "Current Cash",
        money_1(current_cash),
    )

    if (
        not monthly.empty
        and "Cash" in monthly.columns
    ):

        cash_chart = monthly[
            ["Month", "Cash"]
        ].copy()

        cash_chart = cash_chart.set_index("Month")

        st.line_chart(
            cash_chart,
            height=250,
        )


# =========================================================
# CASH FLOW DRIVERS
# =========================================================

st.divider()

st.subheader("Cash Flow Drivers")

if not monthly.empty:

    flow_columns = [
        c
        for c in [
            "Revenue",
            "COGS",
            "Operating_Expenses",
            "AR_Net_Movement",
            "AP_Net_Movement",
        ]
        if c in monthly.columns
    ]

    if flow_columns:

        flow_data = monthly[
            ["Month"] + flow_columns
        ].copy()

        flow_data = flow_data.set_index("Month")

        st.bar_chart(
            flow_data,
            height=350,
        )


# =========================================================
# ACCOUNTING ACTIVITY
# =========================================================

st.divider()

st.subheader("Accounting Activity")

a1, a2, a3, a4 = st.columns(4)

with a1:

    st.metric(
        "GL Entries",
        f"{len(gl):,}",
    )

with a2:

    st.metric(
        "Journal Entries",
        f"{len(data['journal_entries']):,}",
    )

with a3:

    st.metric(
        "AP Invoices",
        f"{len(ap):,}",
    )

with a4:

    st.metric(
        "AR Invoices",
        f"{len(ar):,}",
    )


# =========================================================
# BANKING ACTIVITY
# =========================================================

st.markdown("#### Banking Activity")

if not bank.empty:

    bank_numeric = [
        c
        for c in [
            "Debit",
            "Credit",
        ]
        if c in bank.columns
    ]

    if bank_numeric:

        bank_summary = bank[bank_numeric].sum()

        b1, b2 = st.columns(2)

        with b1:
            st.metric(
                "Bank Debits",
                money_1(
                    bank_summary.get("Debit", 0)
                ),
            )

        with b2:
            st.metric(
                "Bank Credits",
                money_1(
                    bank_summary.get("Credit", 0)
                ),
            )


# =========================================================
# TRIAL BALANCE
# =========================================================

st.divider()

st.subheader("Trial Balance Overview")

if not trial_balance.empty:

    tb = trial_balance.copy()

    if {
        "Closing_Debit",
        "Closing_Credit",
    }.issubset(tb.columns):

        total_debit = tb["Closing_Debit"].sum()
        total_credit = tb["Closing_Credit"].sum()

        t1, t2, t3 = st.columns(3)

        with t1:
            st.metric(
                "Closing Debits",
                money_1(total_debit),
            )

        with t2:
            st.metric(
                "Closing Credits",
                money_1(total_credit),
            )

        with t3:

            difference = total_debit - total_credit

            st.metric(
                "Difference",
                money_1(difference),
                delta=(
                    "Balanced"
                    if abs(difference) < 0.01
                    else "Review"
                ),
            )

        tb_chart = tb[
            [
                c
                for c in [
                    "Account_Name",
                    "Closing_Debit",
                    "Closing_Credit",
                ]
                if c in tb.columns
            ]
        ].copy()

        if "Account_Name" in tb_chart.columns:

            tb_chart = tb_chart.set_index(
                "Account_Name"
            )

            st.bar_chart(
                tb_chart,
                height=350,
            )


# =========================================================
# CONTROL / VALIDATION STATUS
# =========================================================

st.divider()

st.subheader("Accounting Controls")

if not validation.empty:

    if "Passed" in validation.columns:

        passed = validation["Passed"]

        passed_count = (
            passed.astype(str)
            .str.lower()
            .isin(["true", "1", "yes", "passed"])
            .sum()
        )

        total_checks = len(validation)

        failed_count = total_checks - passed_count

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Checks Performed",
                total_checks,
            )

        with c2:
            st.metric(
                "Passed",
                int(passed_count),
            )

        with c3:
            st.metric(
                "Needs Review",
                int(failed_count),
            )

        display_validation = validation.copy()

        st.dataframe(
            display_validation,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.dataframe(
            validation,
            use_container_width=True,
            hide_index=True,
        )

else:

    st.info("No validation results available.")


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Peak Accounting System • Dashboard • Sample data"
)
