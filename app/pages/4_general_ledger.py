import streamlit as st
import pandas as pd

from src.data_loader import data_loader
from src.accounting_engine import accounting_engine

st.set_page_config(
    page_title="General Ledger",
    page_icon="📒",
    layout="wide"
)

st.title("General Ledger")
st.caption("Review posted accounting activity and account balances.")

data = data_loader()

gl = data["gl"]
accounts = data["accounts"]

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    account_options = ["All"] + accounts["Account_Name"].dropna().tolist()
    selected_account = st.selectbox("Account", account_options)

with col2:
    years = ["All"] + sorted(gl["Fiscal_Year"].dropna().unique().tolist())
    selected_year = st.selectbox("Fiscal Year", years)

with col3:
    search = st.text_input("Search description or document")

filtered_gl = gl.copy()

if selected_account != "All":
    account_id = accounts.loc[
        accounts["Account_Name"] == selected_account,
        "Account_ID"
    ].iloc[0]

    filtered_gl = filtered_gl[
        filtered_gl["Account_ID"] == account_id
    ]

if selected_year != "All":
    filtered_gl = filtered_gl[
        filtered_gl["Fiscal_Year"] == selected_year
    ]

if search:
    filtered_gl = filtered_gl[
        filtered_gl["Description"].fillna("").str.contains(
            search, case=False, na=False
        )
        |
        filtered_gl["Document_ID"].fillna("").str.contains(
            search, case=False, na=False
        )
    ]

st.dataframe(
    filtered_gl,
    use_container_width=True,
    hide_index=True
)

st.subheader("Account Balances")

balances = accounting_engine(gl, accounts)

st.dataframe(
    balances,
    use_container_width=True,
    hide_index=True
)