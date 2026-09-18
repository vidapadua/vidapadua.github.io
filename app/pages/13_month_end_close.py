import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Month-End Close",
    page_icon="📅",
    layout="wide",
)


@st.cache_data
def prepare_close_data():
    data = data_loader()

    monthly = data["monthly_balances"].copy()
    validation = data["validation_results"].copy()
    expected = data["expected_results"].copy()
    income_statement = data["income_statement"].copy()
    ar_aging = data["ar_aging"].copy()

    monthly["Month"] = pd.to_datetime(
        monthly["Month"],
        errors="coerce",
    )

    for column in [
        "Revenue",
        "COGS",
        "Gross_Profit",
        "Operating_Expenses",
        "Net_Income",
        "Cash",
        "AR_Net_Movement",
        "AP_Net_Movement",
    ]:
        if column in monthly.columns:
            monthly[column] = pd.to_numeric(
                monthly[column],
                errors="coerce",
            ).fillna(0)

    return (
        data,
        monthly,
        validation,
        expected,
        income_statement,
        ar_aging,
    )


(
    data,
    monthly,
    validation,
    expected,
    income_statement,
    ar_aging,
) = prepare_close_data()


st.title("📅 Month-End Close")
st.caption(
    "Monitor month-end financial results, validation checks, "
    "and close activities."
)

# ---------------------------------------------------------
# Month selection
# ---------------------------------------------------------

st.sidebar.header("Close Period")

available_months = (
    monthly["Month"]
    .dropna()
    .sort_values()
    .dt.strftime("%Y-%m")
    .unique()
    .tolist()
)

selected_month = st.sidebar.selectbox(
    "Month",
    available_months,
    index=len(available_months) - 1
    if available_months
    else 0,
)

if selected_month:
    monthly_period = monthly[
        monthly["Month"].dt.strftime("%Y-%m")
        == selected_month
    ].copy()
else:
    monthly_period = monthly.copy()

# ---------------------------------------------------------
# Financial metrics
# ---------------------------------------------------------

if not monthly_period.empty:

    latest = monthly_period.iloc[-1]

    revenue = latest.get("Revenue", 0)
    cogs = latest.get("COGS", 0)
    gross_profit = latest.get("Gross_Profit", 0)
    operating_expenses = latest.get(
        "Operating_Expenses",
        0,
    )
    net_income = latest.get("Net_Income", 0)
    cash = latest.get("Cash", 0)

else:
    revenue = 0
    cogs = 0
    gross_profit = 0
    operating_expenses = 0
    net_income = 0
    cash = 0


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"${revenue:,.2f}",
)

c2.metric(
    "Gross Profit",
    f"${gross_profit:,.2f}",
)

c3.metric(
    "Net Income",
    f"${net_income:,.2f}",
)

c4.metric(
    "Cash",
    f"${cash:,.2f}",
)

st.divider()

# ---------------------------------------------------------
# Close checklist
# ---------------------------------------------------------

st.subheader("Month-End Close Checklist")

validation_copy = validation.copy()

if "Passed" in validation_copy.columns:

    def normalize_passed(value):
        if isinstance(value, bool):
            return value

        value_str = str(value).strip().lower()

        return value_str in [
            "true",
            "1",
            "yes",
            "passed",
            "pass",
        ]

    validation_copy["Passed_Normalized"] = (
        validation_copy["Passed"]
        .apply(normalize_passed)
    )

else:
    validation_copy["Passed_Normalized"] = False


passed = validation_copy[
    "Passed_Normalized"
].sum()

failed = len(validation_copy) - passed

progress = (
    passed / len(validation_copy)
    if len(validation_copy) > 0
    else 0
)

st.progress(
    progress,
    text=f"Close checks completed: {passed} / {len(validation_copy)}",
)

c1, c2, c3 = st.columns(3)

c1.metric(
    "Checks Passed",
    f"{passed:,}",
)

c2.metric(
    "Checks Requiring Attention",
    f"{failed:,}",
)

c3.metric(
    "Completion",
    f"{progress:.0%}",
)

# ---------------------------------------------------------
# Validation results
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Close Checks",
        "Financial Results",
        "AR Aging",
        "Monthly Trend",
    ]
)

with tab1:

    if failed == 0:
        st.success(
            "All available month-end validation checks passed."
        )
    else:
        st.warning(
            f"{failed:,} validation check(s) require attention."
        )

    display_columns = [
        "Check",
        "Passed",
        "Detail",
    ]

    st.dataframe(
        validation_copy[
            [
                c
                for c in display_columns
                if c in validation_copy.columns
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with tab2:

    st.subheader("Income Statement")

    st.dataframe(
        income_statement,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Expected Results")

    st.dataframe(
        expected,
        use_container_width=True,
        hide_index=True,
    )

with tab3:

    st.subheader("Accounts Receivable Aging")

    aging_display = ar_aging.copy()

    if "Outstanding_Balance" in aging_display.columns:
        aging_display["Outstanding_Balance"] = (
            pd.to_numeric(
                aging_display["Outstanding_Balance"],
                errors="coerce",
            )
            .fillna(0)
        )

    st.dataframe(
        aging_display,
        use_container_width=True,
        hide_index=True,
    )

    if "Outstanding_Balance" in aging_display.columns:
        chart = aging_display[
            [
                "Aging_Bucket",
                "Outstanding_Balance",
            ]
        ].set_index("Aging_Bucket")

        st.bar_chart(
            chart,
            y="Outstanding_Balance",
        )

with tab4:

    trend_columns = [
        "Month",
        "Revenue",
        "COGS",
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
    ].copy()

    st.dataframe(
        trend.sort_values(
            "Month",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

    if "Month" in trend.columns:
        chart = trend.set_index("Month")

        numeric_columns = [
            c
            for c in [
                "Revenue",
                "Gross_Profit",
                "Operating_Expenses",
                "Net_Income",
            ]
            if c in chart.columns
        ]

        if numeric_columns:
            st.line_chart(
                chart[numeric_columns]
            )

# ---------------------------------------------------------
# Close sign-off
# ---------------------------------------------------------

st.divider()

st.subheader("Close Sign-Off")

col1, col2 = st.columns([3, 1])

with col1:
    signoff = st.checkbox(
        "I have reviewed the month-end close checks and financial results."
    )

with col2:
    if signoff and failed == 0:
        st.success("READY TO CLOSE")
    elif signoff:
        st.warning("REVIEW REQUIRED")
    else:
        st.info("NOT SIGNED OFF")

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

csv = validation_copy.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Close Validation",
    data=csv,
    file_name=f"month_end_close_{selected_month}.csv",
    mime="text/csv",
)
