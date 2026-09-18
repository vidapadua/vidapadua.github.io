import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Working Papers",
    page_icon="📋",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    accounts = data["accounts"].copy()
    tb = data["trial_balance"].copy()
    gl = data["gl"].copy()
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

    gl["Posting_Date"] = pd.to_datetime(
        gl["Posting_Date"],
        errors="coerce",
    )

    for column in ["Debit", "Credit"]:
        gl[column] = pd.to_numeric(
            gl[column],
            errors="coerce",
        ).fillna(0)

    gl["Net_Amount"] = (
        gl["Debit"]
        - gl["Credit"]
    )

    return data, accounts, tb, gl, opening


data, accounts, tb, gl, opening = prepare_data()


st.title("📋 Working Papers")
st.caption(
    "Create an organized working-paper view of account balances, "
    "supporting GL activity, and reconciliation documentation."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Working Paper")

account_list = (
    tb[
        [
            "Account_ID",
            "Account_Name",
        ]
    ]
    .drop_duplicates()
    .copy()
)

account_list["Display"] = (
    account_list["Account_ID"].astype(str)
    + " - "
    + account_list["Account_Name"].astype(str)
)

selected_account = st.sidebar.selectbox(
    "Account",
    account_list["Display"].tolist(),
)

selected_row = account_list[
    account_list["Display"] == selected_account
].iloc[0]

account_id = selected_row["Account_ID"]

account_tb = tb[
    tb["Account_ID"] == account_id
].copy()

account_gl = gl[
    gl["Account_ID"] == account_id
].copy()


# ---------------------------------------------------------
# Account balance
# ---------------------------------------------------------

if account_tb.empty:

    closing_balance = 0
    period_debit = 0
    period_credit = 0

else:

    closing_balance = account_tb[
        "Closing_Balance"
    ].sum()

    period_debit = account_tb[
        "Period_Debit"
    ].sum()

    period_credit = account_tb[
        "Period_Credit"
    ].sum()


gl_net = account_gl[
    "Net_Amount"
].sum()


# ---------------------------------------------------------
# KPIs
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Closing Balance",
    f"${closing_balance:,.2f}",
)

c2.metric(
    "Period Debits",
    f"${period_debit:,.2f}",
)

c3.metric(
    "Period Credits",
    f"${period_credit:,.2f}",
)

c4.metric(
    "GL Net Activity",
    f"${gl_net:,.2f}",
)

st.divider()


# ---------------------------------------------------------
# Working paper summary
# ---------------------------------------------------------

st.subheader(
    f"Working Paper — {selected_account}"
)

working_paper = pd.DataFrame(
    {
        "Item": [
            "Account ID",
            "Account Name",
            "Period Debits",
            "Period Credits",
            "Closing Balance",
            "GL Net Activity",
            "GL Transaction Count",
        ],
        "Value": [
            account_id,
            selected_row["Account_Name"],
            f"${period_debit:,.2f}",
            f"${period_credit:,.2f}",
            f"${closing_balance:,.2f}",
            f"${gl_net:,.2f}",
            f"{len(account_gl):,}",
        ],
    }
)

st.dataframe(
    working_paper,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------

difference = (
    closing_balance
    - gl_net
)

st.subheader("Working Paper Reconciliation")

reconciliation = pd.DataFrame(
    {
        "Measure": [
            "Trial Balance Closing Balance",
            "GL Net Activity",
            "Difference",
        ],
        "Amount": [
            closing_balance,
            gl_net,
            difference,
        ],
    }
)

st.dataframe(
    reconciliation,
    use_container_width=True,
    hide_index=True,
)

if abs(difference) < 0.01:
    st.success(
        "The selected working paper is reconciled."
    )
else:
    st.warning(
        "A difference exists between the trial balance "
        "balance and calculated GL activity."
    )


# ---------------------------------------------------------
# Supporting detail
# ---------------------------------------------------------

tab1, tab2, tab3 = st.tabs(
    [
        "Account Balance",
        "GL Support",
        "Documentation",
    ]
)

with tab1:

    st.subheader("Trial Balance Support")

    st.dataframe(
        account_tb,
        use_container_width=True,
        hide_index=True,
    )


with tab2:

    st.subheader("General Ledger Support")

    st.dataframe(
        account_gl[
            [
                "Posting_Date",
                "Document_ID",
                "Document_Type",
                "Transaction_ID",
                "Debit",
                "Credit",
                "Net_Amount",
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


with tab3:

    st.subheader("Working Paper Notes")

    preparer = st.text_input(
        "Prepared By",
    )

    reviewer = st.text_input(
        "Reviewed By",
    )

    notes = st.text_area(
        "Reconciliation Notes",
        height=180,
        placeholder=(
            "Enter supporting documentation, "
            "reconciliation explanations, "
            "or follow-up items."
        ),
    )

    status = st.selectbox(
        "Working Paper Status",
        [
            "Draft",
            "In Review",
            "Completed",
            "Requires Follow-Up",
        ],
    )

    if st.button("Save Working Paper Status"):

        st.success(
            f"Working paper marked as '{status}'."
        )

        if preparer:
            st.write(
                f"Prepared by: {preparer}"
            )

        if reviewer:
            st.write(
                f"Reviewed by: {reviewer}"
            )


# ---------------------------------------------------------
# Export
# ---------------------------------------------------------

st.divider()

csv = account_gl.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Working Paper Support",
    data=csv,
    file_name=(
        "working_paper_"
        f"{account_id}.csv"
    ),
    mime="text/csv",
)
