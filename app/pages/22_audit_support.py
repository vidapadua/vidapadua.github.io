import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Audit Support",
    page_icon="🔎",
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
    validation = data["validation_results"].copy()

    gl["Posting_Date"] = pd.to_datetime(
        gl["Posting_Date"],
        errors="coerce",
    )

    journals["Posting_Date"] = pd.to_datetime(
        journals["Posting_Date"],
        errors="coerce",
    )

    for df in [gl, journals, ap, ar, bank, cc]:

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
    validation,
) = prepare_data()


st.title("🔎 Audit Support")
st.caption(
    "Centralized audit evidence, transaction populations, "
    "journal-entry support, and exception identification."
)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "GL Transactions",
    f"{len(gl):,}",
)

c2.metric(
    "Journal Entries",
    f"{len(journals):,}",
)

c3.metric(
    "AP Invoices",
    f"{len(ap):,}",
)

c4.metric(
    "AR Invoices",
    f"{len(ar):,}",
)

st.divider()


# ---------------------------------------------------------
# Audit populations
# ---------------------------------------------------------

st.subheader("Audit Population")

population = pd.DataFrame(
    {
        "Population": [
            "General Ledger",
            "Journal Entries",
            "AP Invoices",
            "AR Invoices",
            "Bank Transactions",
            "Credit Card Transactions",
            "Validation Checks",
        ],
        "Record Count": [
            len(gl),
            len(journals),
            len(ap),
            len(ar),
            len(bank),
            len(cc),
            len(validation),
        ],
    }
)

st.dataframe(
    population,
    use_container_width=True,
    hide_index=True,
)

st.bar_chart(
    population.set_index(
        "Population"
    )
)


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Journal Entries",
        "GL Exceptions",
        "Source Documents",
        "Validation",
    ]
)


with tab1:

    st.subheader("Journal Entry Population")

    st.dataframe(
        journals.sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


with tab2:

    st.subheader("Potential GL Audit Exceptions")

    exceptions = gl.copy()

    exceptions["Exception"] = ""

    missing_reference = (
        exceptions["Reference"].isna()
        | (
            exceptions["Reference"]
            .astype(str)
            .str.strip()
            == ""
        )
    )

    missing_approval = (
        exceptions["Approved_By"].isna()
        & exceptions["Approval_Date"].isna()
    )

    unapproved_status = (
        exceptions["Status"]
        .astype(str)
        .str.lower()
        .isin(
            [
                "pending",
                "unapproved",
                "review",
            ]
        )
    )

    exceptions.loc[
        missing_reference,
        "Exception",
    ] = "Missing Reference"

    exceptions.loc[
        missing_approval,
        "Exception",
    ] = "Missing Approval"

    exceptions.loc[
        unapproved_status,
        "Exception",
    ] = "Unapproved / Review Status"

    exception_data = exceptions[
        exceptions["Exception"] != ""
    ].copy()

    st.metric(
        "Potential Exceptions",
        f"{len(exception_data):,}",
    )

    st.dataframe(
        exception_data[
            [
                "Posting_Date",
                "Document_ID",
                "Document_Type",
                "Transaction_ID",
                "Account_ID",
                "Account_Name",
                "Debit",
                "Credit",
                "Reference",
                "Approved_By",
                "Approval_Date",
                "Status",
                "Exception",
            ]
        ].sort_values(
            "Posting_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


with tab3:

    st.subheader("Source Document Populations")

    source_summary = pd.DataFrame(
        {
            "Source": [
                "AP Invoices",
                "AR Invoices",
                "Bank Transactions",
                "Credit Card Transactions",
            ],
            "Records": [
                len(ap),
                len(ar),
                len(bank),
                len(cc),
            ],
        }
    )

    st.dataframe(
        source_summary,
        use_container_width=True,
        hide_index=True,
    )

    source_choice = st.selectbox(
        "Source Population",
        [
            "AP Invoices",
            "AR Invoices",
            "Bank Transactions",
            "Credit Card Transactions",
        ],
    )

    if source_choice == "AP Invoices":
        st.dataframe(
            ap,
            use_container_width=True,
            hide_index=True,
        )

    elif source_choice == "AR Invoices":
        st.dataframe(
            ar,
            use_container_width=True,
            hide_index=True,
        )

    elif source_choice == "Bank Transactions":
        st.dataframe(
            bank,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.dataframe(
            cc,
            use_container_width=True,
            hide_index=True,
        )


with tab4:

    st.subheader("Validation Results")

    st.dataframe(
        validation,
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Audit evidence download
# ---------------------------------------------------------

st.divider()

st.subheader("Audit Evidence Export")

export_type = st.selectbox(
    "Evidence Population",
    [
        "GL",
        "Journal Entries",
        "AP Invoices",
        "AR Invoices",
        "Bank",
        "Credit Card",
        "Validation",
    ],
)

export_map = {
    "GL": gl,
    "Journal Entries": journals,
    "AP Invoices": ap,
    "AR Invoices": ar,
    "Bank": bank,
    "Credit Card": cc,
    "Validation": validation,
}

export_df = export_map[export_type]

csv = export_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    f"Download {export_type} Audit Population",
    data=csv,
    file_name=(
        f"audit_support_"
        f"{export_type.lower().replace(' ', '_')}.csv"
    ),
    mime="text/csv",
)
