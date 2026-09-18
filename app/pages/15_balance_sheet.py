

import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Balance Sheet",
    page_icon="⚖️",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    accounts = data["accounts"].copy()
    tb = data["trial_balance"].copy()
    opening = data["opening_balances"].copy()

    numeric_columns = [
        "Opening_Debit",
        "Opening_Credit",
        "Period_Debit",
        "Period_Credit",
        "Closing_Debit",
        "Closing_Credit",
    ]

    for column in numeric_columns:
        if column in tb.columns:
            tb[column] = pd.to_numeric(
                tb[column],
                errors="coerce",
            ).fillna(0)

    tb["Closing_Balance"] = (
        tb["Closing_Debit"]
        - tb["Closing_Credit"]
    )

    return data, accounts, tb, opening


data, accounts, tb, opening = prepare_data()


st.title("⚖️ Balance Sheet")
st.caption(
    "Review assets, liabilities, equity, and the accounting equation "
    "using the trial balance."
)

# ---------------------------------------------------------
# Account Classification
# ---------------------------------------------------------

bs_accounts = accounts[
    accounts["Account_Type"]
    .astype(str)
    .str.lower()
    .isin(
        [
            "asset",
            "liability",
            "equity",
        ]
    )
].copy()

bs = tb.merge(
    bs_accounts[
        [
            "Account_ID",
            "Account_Number",
            "Account_Name",
            "Account_Type",
        ]
    ],
    on=["Account_ID", "Account_Name"],
    how="left",
    suffixes=("", "_Master"),
)

# Prefer master account type if available
if "Account_Type_Master" in bs.columns:
    bs["Account_Type"] = bs["Account_Type_Master"].fillna(
        bs["Account_Type"]
    )

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Balance Sheet Filters")

account_types = sorted(
    bs["Account_Type"]
    .dropna()
    .astype(str)
    .unique()
)

selected_type = st.sidebar.selectbox(
    "Account Type",
    ["All"] + account_types,
)

if selected_type != "All":
    filtered_bs = bs[
        bs["Account_Type"].astype(str)
        == selected_type
    ].copy()
else:
    filtered_bs = bs.copy()


# ---------------------------------------------------------
# Totals
# ---------------------------------------------------------

def balance_for(account_type):
    subset = bs[
        bs["Account_Type"]
        .astype(str)
        .str.lower()
        == account_type.lower()
    ]

    return subset["Closing_Balance"].sum()


assets = balance_for("asset")
liabilities = balance_for("liability")
equity = balance_for("equity")

balance_check = assets - (
    liabilities + equity
)


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Assets",
    f"${assets:,.2f}",
)

c2.metric(
    "Total Liabilities",
    f"${liabilities:,.2f}",
)

c3.metric(
    "Total Equity",
    f"${equity:,.2f}",
)

c4.metric(
    "Balance Check",
    f"${balance_check:,.2f}",
)

st.divider()

# ---------------------------------------------------------
# Accounting Equation
# ---------------------------------------------------------

st.subheader("Accounting Equation")

equation = pd.DataFrame(
    {
        "Component": [
            "Assets",
            "Liabilities",
            "Equity",
            "Liabilities + Equity",
            "Balance Difference",
        ],
        "Amount": [
            assets,
            liabilities,
            equity,
            liabilities + equity,
            balance_check,
        ],
    }
)

st.dataframe(
    equation,
    use_container_width=True,
    hide_index=True,
)

if abs(balance_check) < 0.01:
    st.success(
        "The balance sheet accounting equation is balanced."
    )
else:
    st.warning(
        "The accounting equation has a difference that requires review."
    )

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Balance Sheet Accounts",
        "By Account Type",
        "Trial Balance",
    ]
)

with tab1:

    display_columns = [
        "Account_ID",
        "Account_Name",
        "Account_Type",
        "Opening_Debit",
        "Opening_Credit",
        "Period_Debit",
        "Period_Credit",
        "Closing_Debit",
        "Closing_Credit",
        "Closing_Balance",
    ]

    st.dataframe(
        filtered_bs[
            [
                c
                for c in display_columns
                if c in filtered_bs.columns
            ]
        ].sort_values(
            "Closing_Balance",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab2:

    summary = (
        bs.groupby(
            "Account_Type",
            dropna=False,
        )["Closing_Balance"]
        .sum()
        .reset_index()
        .sort_values(
            "Closing_Balance",
            ascending=False,
        )
    )

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
    )

    chart = summary.set_index(
        "Account_Type"
    )

    st.bar_chart(chart)

with tab3:

    st.dataframe(
        tb,
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = filtered_bs.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Balance Sheet",
    data=csv,
    file_name="balance_sheet.csv",
    mime="text/csv",
)