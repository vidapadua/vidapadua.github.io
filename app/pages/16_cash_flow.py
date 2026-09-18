import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Cash Flow",
    page_icon="💵",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    monthly = data["monthly_balances"].copy()
    bank = data["bank"].copy()
    gl = data["gl"].copy()

    monthly["Month"] = pd.to_datetime(
        monthly["Month"],
        errors="coerce",
    )

    numeric_columns = [
        "Cash",
        "Revenue",
        "COGS",
        "Gross_Profit",
        "Operating_Expenses",
        "Net_Income",
        "AR_Net_Movement",
        "AP_Net_Movement",
    ]

    for column in numeric_columns:
        if column in monthly.columns:
            monthly[column] = pd.to_numeric(
                monthly[column],
                errors="coerce",
            ).fillna(0)

    for column in ["Debit", "Credit", "Running_Balance"]:
        if column in bank.columns:
            bank[column] = pd.to_numeric(
                bank[column],
                errors="coerce",
            ).fillna(0)

    bank["Posting_Date"] = pd.to_datetime(
        bank["Posting_Date"],
        errors="coerce",
    )

    bank["Net_Cash_Flow"] = (
        bank["Credit"] - bank["Debit"]
    )

    return data, monthly, bank, gl


data, monthly, bank, gl = prepare_data()


st.title("💵 Cash Flow")
st.caption(
    "Analyze cash movements, bank activity, operating cash drivers, "
    "and monthly cash trends."
)

# ---------------------------------------------------------
# Period
# ---------------------------------------------------------

st.sidebar.header("Cash Flow Filters")

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
    period = monthly.sort_values("Month").iloc[-1]
elif selected_month != "Latest":
    period = monthly[
        monthly["Month"].dt.strftime("%Y-%m")
        == selected_month
    ].iloc[-1]
else:
    period = None


# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

if period is not None:
    cash = period.get("Cash", 0)
    net_income = period.get("Net_Income", 0)
    ar_movement = period.get("AR_Net_Movement", 0)
    ap_movement = period.get("AP_Net_Movement", 0)
else:
    cash = 0
    net_income = 0
    ar_movement = 0
    ap_movement = 0


# Approximate operating cash flow using available monthly data.
operating_cash_flow = (
    net_income
    - ar_movement
    + ap_movement
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Cash Balance",
    f"${cash:,.2f}",
)

c2.metric(
    "Net Income",
    f"${net_income:,.2f}",
)

c3.metric(
    "Operating Cash Flow",
    f"${operating_cash_flow:,.2f}",
)

c4.metric(
    "AR Movement",
    f"${ar_movement:,.2f}",
)

st.divider()

# ---------------------------------------------------------
# Cash Flow Statement
# ---------------------------------------------------------

st.subheader("Cash Flow Summary")

cash_flow = pd.DataFrame(
    {
        "Cash Flow Component": [
            "Net Income",
            "Change in Accounts Receivable",
            "Change in Accounts Payable",
            "Operating Cash Flow",
            "Ending Cash",
        ],
        "Amount": [
            net_income,
            -ar_movement,
            ap_movement,
            operating_cash_flow,
            cash,
        ],
    }
)

st.dataframe(
    cash_flow,
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Monthly Cash",
        "Bank Activity",
        "Cash Flow Drivers",
    ]
)

with tab1:

    trend_columns = [
        "Month",
        "Cash",
        "Revenue",
        "Net_Income",
        "AR_Net_Movement",
        "AP_Net_Movement",
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
        chart = trend.set_index("Month")

        chart_columns = [
            c
            for c in [
                "Cash",
                "Net_Income",
            ]
            if c in chart.columns
        ]

        st.line_chart(
            chart[chart_columns]
        )

with tab2:

    st.subheader("Bank Transaction Activity")

    bank_display = bank.copy()

    min_date = bank_display["Posting_Date"].min()
    max_date = bank_display["Posting_Date"].max()

    bank_date_range = st.date_input(
        "Bank activity period",
        value=(
            min_date.date(),
            max_date.date(),
        ),
        key="cash_bank_dates",
    )

    if (
        isinstance(bank_date_range, tuple)
        and len(bank_date_range) == 2
    ):
        start_date, end_date = bank_date_range

        bank_display = bank_display[
            (
                bank_display["Posting_Date"].dt.date
                >= start_date
            )
            & (
                bank_display["Posting_Date"].dt.date
                <= end_date
            )
        ]

    inflows = bank_display["Credit"].sum()
    outflows = bank_display["Debit"].sum()
    net_flow = bank_display["Net_Cash_Flow"].sum()

    b1, b2, b3 = st.columns(3)

    b1.metric(
        "Cash Inflows",
        f"${inflows:,.2f}",
    )

    b2.metric(
        "Cash Outflows",
        f"${outflows:,.2f}",
    )

    b3.metric(
        "Net Cash Flow",
        f"${net_flow:,.2f}",
    )

    st.dataframe(
        bank_display.sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab3:

    drivers = pd.DataFrame(
        {
            "Driver": [
                "Net Income",
                "AR Movement",
                "AP Movement",
                "Operating Cash Flow",
            ],
            "Amount": [
                net_income,
                ar_movement,
                ap_movement,
                operating_cash_flow,
            ],
        }
    )

    st.dataframe(
        drivers,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        drivers.set_index("Driver")
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = cash_flow.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Cash Flow",
    data=csv,
    file_name="cash_flow.csv",
    mime="text/csv",
)