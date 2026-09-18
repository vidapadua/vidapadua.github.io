import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Bank Reconciliation",
    page_icon="🏦",
    layout="wide",
)


@st.cache_data
def prepare_bank_data():
    data = data_loader()

    bank = data["bank"].copy()
    gl = data["gl"].copy()

    bank["Posting_Date"] = pd.to_datetime(bank["Posting_Date"], errors="coerce")
    bank["Value_Date"] = pd.to_datetime(bank["Value_Date"], errors="coerce")
    gl["Posting_Date"] = pd.to_datetime(gl["Posting_Date"], errors="coerce")

    bank["Bank_Net"] = (
        pd.to_numeric(bank["Credit"], errors="coerce").fillna(0)
        - pd.to_numeric(bank["Debit"], errors="coerce").fillna(0)
    )

    gl["GL_Net"] = (
        pd.to_numeric(gl["Credit"], errors="coerce").fillna(0)
        - pd.to_numeric(gl["Debit"], errors="coerce").fillna(0)
    )

    return data, bank, gl


data, bank, gl = prepare_bank_data()

st.title("🏦 Bank Reconciliation")
st.caption("Compare bank activity against the general ledger and identify outstanding items.")

# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------

st.sidebar.header("Filters")

min_date = bank["Posting_Date"].min()
max_date = bank["Posting_Date"].max()

date_range = st.sidebar.date_input(
    "Posting date",
    value=(min_date.date(), max_date.date()),
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    bank_filtered = bank[
        (bank["Posting_Date"].dt.date >= start_date)
        & (bank["Posting_Date"].dt.date <= end_date)
    ]
else:
    bank_filtered = bank.copy()

bank_accounts = sorted(
    bank_filtered["Bank_Account_ID"].dropna().astype(str).unique()
)

selected_bank_account = st.sidebar.selectbox(
    "Bank account",
    ["All"] + bank_accounts,
)

if selected_bank_account != "All":
    bank_filtered = bank_filtered[
        bank_filtered["Bank_Account_ID"].astype(str) == selected_bank_account
    ]

# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

bank_total = bank_filtered["Bank_Net"].sum()

bank_debits = pd.to_numeric(
    bank_filtered["Debit"], errors="coerce"
).fillna(0).sum()

bank_credits = pd.to_numeric(
    bank_filtered["Credit"], errors="coerce"
).fillna(0).sum()

ending_balance = (
    pd.to_numeric(
        bank_filtered["Running_Balance"], errors="coerce"
    )
    .dropna()
    .iloc[-1]
    if not bank_filtered.empty
    and pd.to_numeric(
        bank_filtered["Running_Balance"], errors="coerce"
    ).notna().any()
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Bank Transactions",
    f"{len(bank_filtered):,}",
)

col2.metric(
    "Bank Debits",
    f"${bank_debits:,.2f}",
)

col3.metric(
    "Bank Credits",
    f"${bank_credits:,.2f}",
)

col4.metric(
    "Ending Bank Balance",
    f"${ending_balance:,.2f}",
)

st.divider()

# ---------------------------------------------------------
# Reconciliation logic
# ---------------------------------------------------------

st.subheader("Reconciliation Summary")

reference_counts = (
    bank_filtered["Reference"]
    .fillna("")
    .astype(str)
    .str.strip()
)

matched = reference_counts.ne("")

unmatched_bank = bank_filtered.loc[
    ~matched
].copy()

matched_bank = bank_filtered.loc[
    matched
].copy()

summary_col1, summary_col2, summary_col3 = st.columns(3)

summary_col1.metric(
    "Items With Reference",
    f"{len(matched_bank):,}",
)

summary_col2.metric(
    "Items Requiring Review",
    f"{len(unmatched_bank):,}",
)

summary_col3.metric(
    "Review Amount",
    f"${unmatched_bank['Bank_Net'].sum():,.2f}",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Bank Transactions",
        "Items to Review",
        "GL Activity",
    ]
)

with tab1:
    st.dataframe(
        bank_filtered.sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.info(
        "Transactions without a reference are surfaced as potential "
        "reconciliation items for review."
    )

    st.dataframe(
        unmatched_bank.sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    gl_filtered = gl.copy()

    if isinstance(date_range, tuple) and len(date_range) == 2:
        gl_filtered = gl_filtered[
            (gl_filtered["Posting_Date"].dt.date >= start_date)
            & (gl_filtered["Posting_Date"].dt.date <= end_date)
        ]

    st.dataframe(
        gl_filtered[
            [
                "Posting_Date",
                "Document_ID",
                "Document_Type",
                "Account_ID",
                "Account_Name",
                "Debit",
                "Credit",
                "Description",
                "Reference",
                "Status",
            ]
        ].sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = bank_filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Bank Reconciliation Data",
    data=csv,
    file_name="bank_reconciliation.csv",
    mime="text/csv",
)