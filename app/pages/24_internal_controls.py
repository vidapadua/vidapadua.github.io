import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Internal Controls",
    page_icon="🛡️",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    gl = data["gl"].copy()
    journals = data["journal_entries"].copy()
    ap = data["ap_invoices"].copy()
    ar = data["ar_invoices"].copy()
    bank = data["bank"].copy()
    cc = data["credit_card_transactions"].copy()
    expenses = data["expense_reports"].copy()
    validation = data["validation_results"].copy()

    for df in [
        gl,
        journals,
        ap,
        ar,
        bank,
        cc,
        expenses,
    ]:

        for column in [
            "Debit",
            "Credit",
            "Total_Debit",
            "Total_Credit",
            "Net_Amount",
            "GST",
            "Gross_Amount",
            "Amount",
            "Total_Amount",
        ]:

            if column in df.columns:

                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0)

    return (
        data,
        gl,
        journals,
        ap,
        ar,
        bank,
        cc,
        expenses,
        validation,
    )


(
    data,
    gl,
    journals,
    ap,
    ar,
    bank,
    cc,
    expenses,
    validation,
) = prepare_data()


st.title("🛡️ Internal Controls")
st.caption(
    "Monitor transaction-level control checks and identify populations "
    "requiring management review."
)


# ---------------------------------------------------------
# Control checks
# ---------------------------------------------------------

control_results = []


def add_control(
    name,
    population,
    exception_count,
    description,
):
    control_results.append(
        {
            "Control": name,
            "Population": population,
            "Exceptions": exception_count,
            "Status": (
                "Pass"
                if exception_count == 0
                else "Review"
            ),
            "Description": description,
        }
    )


# GL reference control
gl_missing_reference = gl[
    gl["Reference"].isna()
    | (
        gl["Reference"]
        .astype(str)
        .str.strip()
        == ""
    )
]

add_control(
    "GL Reference Completeness",
    len(gl),
    len(gl_missing_reference),
    "GL transactions should contain a reference.",
)


# GL approval control
gl_missing_approval = gl[
    gl["Approved_By"].isna()
    & gl["Approval_Date"].isna()
]

add_control(
    "GL Approval Evidence",
    len(gl),
    len(gl_missing_approval),
    "Transactions without approval evidence are flagged.",
)


# Journal entry balance
if (
    "Total_Debit" in journals.columns
    and "Total_Credit" in journals.columns
):

    journal_difference = (
        journals["Total_Debit"]
        - journals["Total_Credit"]
    )

    journal_exceptions = journals[
        journal_difference.abs() > 0.01
    ]

else:

    journal_exceptions = journals.iloc[0:0]


add_control(
    "Journal Entry Balance",
    len(journals),
    len(journal_exceptions),
    "Journal entries should have equal debits and credits.",
)


# AP tax code
ap_missing_tax = ap[
    ap["Tax_Code"].isna()
    | (
        ap["Tax_Code"]
        .astype(str)
        .str.strip()
        == ""
    )
]

add_control(
    "AP Tax Code Completeness",
    len(ap),
    len(ap_missing_tax),
    "AP invoices should contain a tax code.",
)


# AR tax code
ar_missing_tax = ar[
    ar["Tax_Code"].isna()
    | (
        ar["Tax_Code"]
        .astype(str)
        .str.strip()
        == ""
    )
]

add_control(
    "AR Tax Code Completeness",
    len(ar),
    len(ar_missing_tax),
    "AR invoices should contain a tax code.",
)


# Credit card status
cc_review = cc[
    cc["Status"]
    .astype(str)
    .str.lower()
    .isin(
        [
            "pending",
            "review",
            "unapproved",
        ]
    )
]

add_control(
    "Credit Card Approval Status",
    len(cc),
    len(cc_review),
    "Credit card transactions with review statuses are flagged.",
)


# Expense report receipts
missing_receipts = expenses[
    expenses["Receipt_Status"]
    .astype(str)
    .str.lower()
    .isin(
        [
            "missing",
            "not received",
            "pending",
        ]
    )
]

add_control(
    "Expense Receipt Evidence",
    len(expenses),
    len(missing_receipts),
    "Expense reports without completed receipt evidence are flagged.",
)


# ---------------------------------------------------------
# Control results
# ---------------------------------------------------------

controls = pd.DataFrame(
    control_results
)

total_controls = len(controls)

passed_controls = (
    controls["Status"] == "Pass"
).sum()

review_controls = (
    controls["Status"] == "Review"
).sum()

completion = (
    passed_controls / total_controls
    if total_controls
    else 0
)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Controls Tested",
    f"{total_controls:,}",
)

c2.metric(
    "Controls Passed",
    f"{passed_controls:,}",
)

c3.metric(
    "Controls Requiring Review",
    f"{review_controls:,}",
)

c4.metric(
    "Pass Rate",
    f"{completion:.0%}",
)

st.progress(
    completion,
    text=f"Control pass rate: {completion:.0%}",
)

st.divider()


# ---------------------------------------------------------
# Control matrix
# ---------------------------------------------------------

st.subheader("Internal Control Matrix")

st.dataframe(
    controls,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Exceptions
# ---------------------------------------------------------

st.subheader("Control Exceptions")

exception_summary = controls[
    controls["Exceptions"] > 0
].copy()

if exception_summary.empty:

    st.success(
        "No control exceptions were identified by the configured checks."
    )

else:

    st.warning(
        f"{len(exception_summary):,} control(s) have exceptions."
    )

    st.dataframe(
        exception_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.bar_chart(
        exception_summary.set_index(
            "Control"
        )[
            "Exceptions"
        ]
    )


# ---------------------------------------------------------
# Detailed exception populations
# ---------------------------------------------------------

st.divider()

st.subheader("Exception Detail")

exception_type = st.selectbox(
    "Exception Population",
    [
        "GL Missing References",
        "GL Missing Approvals",
        "Unbalanced Journal Entries",
        "AP Missing Tax Codes",
        "AR Missing Tax Codes",
        "Credit Card Review",
        "Expense Receipt Exceptions",
    ],
)


if exception_type == "GL Missing References":

    detail = gl_missing_reference

elif exception_type == "GL Missing Approvals":

    detail = gl_missing_approval

elif exception_type == "Unbalanced Journal Entries":

    detail = journal_exceptions

elif exception_type == "AP Missing Tax Codes":

    detail = ap_missing_tax

elif exception_type == "AR Missing Tax Codes":

    detail = ar_missing_tax

elif exception_type == "Credit Card Review":

    detail = cc_review

else:

    detail = missing_receipts


st.metric(
    "Exception Records",
    f"{len(detail):,}",
)

st.dataframe(
    detail,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Validation cross-check
# ---------------------------------------------------------

st.divider()

st.subheader("Existing Validation Results")

st.dataframe(
    validation,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

csv = controls.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download Internal Control Matrix",
    data=csv,
    file_name="internal_controls.csv",
    mime="text/csv",
)
