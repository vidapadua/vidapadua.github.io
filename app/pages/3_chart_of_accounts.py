import streamlit as st
import pandas as pd

from src.data_loader import data_loader

st.set_page_config(
    page_title="Chart of Accounts",
    page_icon="📋",
    layout="wide"
)

st.title("Chart of Accounts")
st.caption("View the company's general ledger account structure.")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

data = data_loader()
accounts = data["accounts"].copy()

# Clean column names
accounts.columns = accounts.columns.str.strip()


# --------------------------------------------------
# FILTERS
# --------------------------------------------------

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input(
        "Search",
        placeholder="Search account number or name..."
    )

with col2:
    account_types = ["All"] + sorted(
        accounts["Account_Type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_type = st.selectbox(
        "Account Type",
        account_types
    )

with col3:
    statements = ["All"] + sorted(
        accounts["Financial_Statement"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_statement = st.selectbox(
        "Financial Statement",
        statements
    )


# --------------------------------------------------
# FILTER
# --------------------------------------------------

filtered_accounts = accounts.copy()

if search:

    search_mask = (
        filtered_accounts["Account_Number"]
        .astype(str)
        .str.contains(search, case=False, na=False)
        |
        filtered_accounts["Account_Name"]
        .astype(str)
        .str.contains(search, case=False, na=False)
        |
        filtered_accounts["Account_ID"]
        .astype(str)
        .str.contains(search, case=False, na=False)
    )

    filtered_accounts = filtered_accounts[search_mask]


if selected_type != "All":
    filtered_accounts = filtered_accounts[
        filtered_accounts["Account_Type"].astype(str)
        == selected_type
    ]


if selected_statement != "All":
    filtered_accounts = filtered_accounts[
        filtered_accounts["Financial_Statement"].astype(str)
        == selected_statement
    ]


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Accounts",
        len(accounts)
    )

with col2:
    st.metric(
        "Accounts Shown",
        len(filtered_accounts)
    )

with col3:
    st.metric(
        "Active Accounts",
        int(accounts["Active"].sum())
    )

with col4:
    st.metric(
        "Account Types",
        accounts["Account_Type"].nunique()
    )


st.divider()


# --------------------------------------------------
# ACCOUNT TABLE
# --------------------------------------------------

st.subheader("Accounts")

display_columns = [
    "Account_Number",
    "Account_Name",
    "Account_Type",
    "Financial_Statement",
    "Parent_Account",
    "Active"
]

st.dataframe(
    filtered_accounts[display_columns],
    use_container_width=True,
    hide_index=True
)