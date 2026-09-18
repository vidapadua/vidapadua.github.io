import streamlit as st
import pandas as pd

from src.data_loader import data_loader


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Transactions",
    page_icon="📑",
    layout="wide"
)


# ==================================================
# LOAD DATA
# ==================================================

data = data_loader()

gl = data["gl"].copy()


# Clean column names
gl.columns = gl.columns.str.strip()


# ==================================================
# PAGE HEADER
# ==================================================

st.title("Transactions")
st.caption(
    "Review posted general ledger transactions and accounting activity."
)


# ==================================================
# SUMMARY
# ==================================================

total_transactions = len(gl)

total_debits = pd.to_numeric(
    gl["Debit"],
    errors="coerce"
).fillna(0).sum()

total_credits = pd.to_numeric(
    gl["Credit"],
    errors="coerce"
).fillna(0).sum()

unique_documents = gl["Document_ID"].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Transactions",
        f"{total_transactions:,}"
    )

with col2:
    st.metric(
        "Total Debits",
        f"${total_debits:,.2f}"
    )

with col3:
    st.metric(
        "Total Credits",
        f"${total_credits:,.2f}"
    )

with col4:
    st.metric(
        "Documents",
        f"{unique_documents:,}"
    )


st.divider()


# ==================================================
# FILTERS
# ==================================================

st.subheader("Transaction Register")

col1, col2, col3 = st.columns(3)

with col1:
    search = st.text_input(
        "Search",
        placeholder="Document, transaction, description, or reference..."
    )

with col2:
    document_types = ["All"] + sorted(
        gl["Document_Type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_document_type = st.selectbox(
        "Document Type",
        document_types
    )

with col3:
    statuses = ["All"] + sorted(
        gl["Status"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_status = st.selectbox(
        "Status",
        statuses
    )


# Second row of filters

col1, col2, col3 = st.columns(3)

with col1:
    accounts = data["accounts"].copy()

    account_lookup = dict(
        zip(
            accounts["Account_ID"],
            accounts["Account_Name"]
        )
    )

    account_options = ["All"] + sorted(
        accounts["Account_Name"]
        .dropna()
        .astype(str)
        .tolist()
    )

    selected_account = st.selectbox(
        "Account",
        account_options
    )

with col2:
    fiscal_years = ["All"] + sorted(
        gl["Fiscal_Year"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_year = st.selectbox(
        "Fiscal Year",
        fiscal_years
    )

with col3:
    departments = ["All"] + sorted(
        gl["Department_ID"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_department = st.selectbox(
        "Department",
        departments
    )


# ==================================================
# APPLY FILTERS
# ==================================================

filtered_gl = gl.copy()


# Search

if search:

    search_columns = [
        "Document_ID",
        "Transaction_ID",
        "Description",
        "Reference"
    ]

    search_mask = pd.Series(
        False,
        index=filtered_gl.index
    )

    for column in search_columns:

        if column in filtered_gl.columns:

            search_mask |= (
                filtered_gl[column]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            )

    filtered_gl = filtered_gl[search_mask]


# Document type

if selected_document_type != "All":

    filtered_gl = filtered_gl[
        filtered_gl["Document_Type"].astype(str)
        == selected_document_type
    ]


# Status

if selected_status != "All":

    filtered_gl = filtered_gl[
        filtered_gl["Status"].astype(str)
        == selected_status
    ]


# Account

if selected_account != "All":

    selected_account_id = accounts.loc[
        accounts["Account_Name"] == selected_account,
        "Account_ID"
    ].iloc[0]

    filtered_gl = filtered_gl[
        filtered_gl["Account_ID"]
        == selected_account_id
    ]


# Fiscal year

if selected_year != "All":

    filtered_gl = filtered_gl[
        filtered_gl["Fiscal_Year"]
        == selected_year
    ]


# Department

if selected_department != "All":

    filtered_gl = filtered_gl[
        filtered_gl["Department_ID"].astype(str)
        == selected_department
    ]


# ==================================================
# FILTERED TOTALS
# ==================================================

filtered_debits = pd.to_numeric(
    filtered_gl["Debit"],
    errors="coerce"
).fillna(0).sum()

filtered_credits = pd.to_numeric(
    filtered_gl["Credit"],
    errors="coerce"
).fillna(0).sum()


st.write(
    f"**{len(filtered_gl):,}** transactions found"
)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Filtered Debits",
        f"${filtered_debits:,.2f}"
    )

with col2:
    st.metric(
        "Filtered Credits",
        f"${filtered_credits:,.2f}"
    )


# ==================================================
# TRANSACTION TABLE
# ==================================================

display_columns = [
    "Posting_Date",
    "Document_ID",
    "Document_Type",
    "Transaction_ID",
    "Line_ID",
    "Account_ID",
    "Account_Name",
    "Debit",
    "Credit",
    "Department_ID",
    "Location_ID",
    "Project_ID",
    "Description",
    "Reference",
    "Status"
]

display_columns = [
    column
    for column in display_columns
    if column in filtered_gl.columns
]

display_df = filtered_gl[display_columns].copy()


# Currency formatting

for column in ["Debit", "Credit"]:

    if column in display_df.columns:

        display_df[column] = pd.to_numeric(
            display_df[column],
            errors="coerce"
        ).fillna(0)


st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Debit": st.column_config.NumberColumn(
            "Debit",
            format="$%.2f"
        ),
        "Credit": st.column_config.NumberColumn(
            "Credit",
            format="$%.2f"
        ),
        "Posting_Date": st.column_config.DateColumn(
            "Posting Date"
        )
    }
)


# ==================================================
# TRANSACTION DETAILS
# ==================================================

st.divider()

st.subheader("Transaction Details")

if len(filtered_gl) > 0:

    transaction_options = filtered_gl[
        "Transaction_ID"
    ].dropna().astype(str).unique().tolist()

    selected_transaction = st.selectbox(
        "Select Transaction",
        transaction_options
    )

    transaction = filtered_gl[
        filtered_gl["Transaction_ID"].astype(str)
        == selected_transaction
    ]

    st.dataframe(
        transaction,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No transactions match the selected filters.")