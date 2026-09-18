import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Account Reconciliations",
    page_icon="📒",
    layout="wide",
)


@st.cache_data
def prepare_account_data():
    data = data_loader()

    accounts = data["accounts"].copy()
    tb = data["trial_balance"].copy()
    gl = data["gl"].copy()

    tb["Closing_Debit"] = pd.to_numeric(
        tb["Closing_Debit"],
        errors="coerce",
    ).fillna(0)

    tb["Closing_Credit"] = pd.to_numeric(
        tb["Closing_Credit"],
        errors="coerce",
    ).fillna(0)

    tb["Closing_Balance"] = (
        tb["Closing_Debit"] - tb["Closing_Credit"]
    )

    gl["Debit"] = pd.to_numeric(
        gl["Debit"],
        errors="coerce",
    ).fillna(0)

    gl["Credit"] = pd.to_numeric(
        gl["Credit"],
        errors="coerce",
    ).fillna(0)

    gl["Net_Amount"] = gl["Debit"] - gl["Credit"]

    return data, accounts, tb, gl


data, accounts, tb, gl = prepare_account_data()

st.title("📒 Account Reconciliations")
st.caption(
    "Review trial balance accounts and investigate account-level "
    "general ledger activity."
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Reconciliation Filters")

account_options = (
    accounts[
        [
            "Account_ID",
            "Account_Number",
            "Account_Name",
        ]
    ]
    .drop_duplicates()
    .copy()
)

account_options["Display"] = (
    account_options["Account_Number"].astype(str)
    + " - "
    + account_options["Account_Name"].astype(str)
)

selected_account = st.sidebar.selectbox(
    "Account",
    ["All"] + account_options["Display"].tolist(),
)

if selected_account != "All":
    selected_row = account_options[
        account_options["Display"] == selected_account
    ].iloc[0]

    account_id = selected_row["Account_ID"]

    tb_filtered = tb[
        tb["Account_ID"] == account_id
    ].copy()

    gl_filtered = gl[
        gl["Account_ID"] == account_id
    ].copy()
else:
    tb_filtered = tb.copy()
    gl_filtered = gl.copy()

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

total_debit = tb_filtered["Closing_Debit"].sum()
total_credit = tb_filtered["Closing_Credit"].sum()
net_balance = tb_filtered["Closing_Balance"].sum()

gl_activity = gl_filtered["Net_Amount"].sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Accounts",
    f"{len(tb_filtered):,}",
)

c2.metric(
    "Closing Debit",
    f"${total_debit:,.2f}",
)

c3.metric(
    "Closing Credit",
    f"${total_credit:,.2f}",
)

c4.metric(
    "Net Balance",
    f"${net_balance:,.2f}",
)

st.divider()

# ---------------------------------------------------------
# Account reconciliation status
# ---------------------------------------------------------

st.subheader("Account Reconciliation Status")

recon = tb_filtered.copy()

recon["Variance"] = (
    recon["Closing_Debit"]
    - recon["Closing_Credit"]
)

recon["Status"] = recon["Variance"].apply(
    lambda x: "Review" if abs(x) > 0.01 else "Reconciled"
)

reconciled_count = (
    recon["Status"] == "Reconciled"
).sum()

review_count = (
    recon["Status"] == "Review"
).sum()

r1, r2, r3 = st.columns(3)

r1.metric(
    "Reconciled",
    f"{reconciled_count:,}",
)

r2.metric(
    "Requires Review",
    f"{review_count:,}",
)

r3.metric(
    "GL Activity",
    f"${gl_activity:,.2f}",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Trial Balance",
        "GL Detail",
        "Exceptions",
    ]
)

with tab1:
    st.dataframe(
        recon[
            [
                "Account_ID",
                "Account_Name",
                "Opening_Debit",
                "Opening_Credit",
                "Period_Debit",
                "Period_Credit",
                "Closing_Debit",
                "Closing_Credit",
                "Variance",
                "Status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    gl_columns = [
        "Posting_Date",
        "Document_ID",
        "Document_Type",
        "Transaction_ID",
        "Account_ID",
        "Account_Name",
        "Debit",
        "Credit",
        "Net_Amount",
        "Department_ID",
        "Location_ID",
        "Project_ID",
        "Description",
        "Reference",
        "Status",
    ]

    st.dataframe(
        gl_filtered[
            [c for c in gl_columns if c in gl_filtered.columns]
        ].sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    exceptions = recon[
        recon["Status"] == "Review"
    ].copy()

    if exceptions.empty:
        st.success("No account reconciliation exceptions found.")
    else:
        st.warning(
            f"{len(exceptions):,} account(s) require review."
        )

        st.dataframe(
            exceptions,
            use_container_width=True,
            hide_index=True,
        )

# ---------------------------------------------------------
# Account activity chart
# ---------------------------------------------------------

st.divider()

st.subheader("Account Balances")

chart_data = recon[
    [
        "Account_Name",
        "Closing_Balance",
    ]
].copy()

if not chart_data.empty:
    chart_data = chart_data.set_index(
        "Account_Name"
    )

    st.bar_chart(
        chart_data,
        y="Closing_Balance",
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

csv = recon.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Account Reconciliation",
    data=csv,
    file_name="account_reconciliations.csv",
    mime="text/csv",
)
