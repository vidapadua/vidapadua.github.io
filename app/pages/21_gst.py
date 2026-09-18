import streamlit as st
import pandas as pd
import numpy as np

from src.data_loader import data_loader


st.set_page_config(
    page_title="GST",
    page_icon="🧾",
    layout="wide",
)


@st.cache_data
def prepare_data():
    data = data_loader()

    company = data["company"].copy()
    gst = data["gst_transactions"].copy()
    tax_codes = data["tax_codes"].copy()
    ar = data["ar_invoices"].copy()
    ap = data["ap_invoices"].copy()

    gst["Date"] = pd.to_datetime(
        gst["Date"],
        errors="coerce",
    )

    for column in ["GST_Amount", "Rate"]:
        if column in gst.columns:
            gst[column] = pd.to_numeric(
                gst[column],
                errors="coerce",
            ).fillna(0)

    for df in [ar, ap]:
        for column in [
            "Net_Amount",
            "GST",
            "Gross_Amount",
            "Paid_Amount",
            "Outstanding_Balance",
        ]:
            if column in df.columns:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce",
                ).fillna(0)

    return data, company, gst, tax_codes, ar, ap


data, company, gst, tax_codes, ar, ap = prepare_data()


st.title("🧾 GST")
st.caption(
    "Review GST transactions, input and output tax, tax-code usage, "
    "and GST reconciliation."
)

# ---------------------------------------------------------
# Company GST information
# ---------------------------------------------------------

company_row = (
    company.iloc[0]
    if not company.empty
    else None
)

if company_row is not None:
    gst_registration = company_row.get(
        "GST_Registration",
        "N/A",
    )
    gst_rate = company_row.get(
        "GST_Rate",
        0,
    )
else:
    gst_registration = "N/A"
    gst_rate = 0


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------

st.sidebar.header("GST Filters")

valid_dates = gst["Date"].dropna()

if not valid_dates.empty:

    min_date = valid_dates.min()
    max_date = valid_dates.max()

    date_range = st.sidebar.date_input(
        "GST Transaction Date",
        value=(
            min_date.date(),
            max_date.date(),
        ),
    )

    if (
        isinstance(date_range, tuple)
        and len(date_range) == 2
    ):
        start_date, end_date = date_range

        gst_filtered = gst[
            (gst["Date"].dt.date >= start_date)
            & (gst["Date"].dt.date <= end_date)
        ].copy()
    else:
        gst_filtered = gst.copy()

else:
    gst_filtered = gst.copy()


tax_code_options = sorted(
    gst_filtered["Tax_Code"]
    .dropna()
    .astype(str)
    .unique()
)

selected_tax_code = st.sidebar.selectbox(
    "Tax Code",
    ["All"] + tax_code_options,
)

if selected_tax_code != "All":
    gst_filtered = gst_filtered[
        gst_filtered["Tax_Code"].astype(str)
        == selected_tax_code
    ]


# ---------------------------------------------------------
# GST calculations
# ---------------------------------------------------------

input_tax = gst_filtered[
    gst_filtered["Direction"]
    .astype(str)
    .str.lower()
    .isin(["input", "purchase"])
]["GST_Amount"].sum()

output_tax = gst_filtered[
    gst_filtered["Direction"]
    .astype(str)
    .str.lower()
    .isin(["output", "sales"])
]["GST_Amount"].sum()

net_gst = output_tax - input_tax

transaction_count = len(gst_filtered)


# ---------------------------------------------------------
# KPI cards
# ---------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "GST Transactions",
    f"{transaction_count:,}",
)

c2.metric(
    "Input GST",
    f"${input_tax:,.2f}",
)

c3.metric(
    "Output GST",
    f"${output_tax:,.2f}",
)

c4.metric(
    "Net GST",
    f"${net_gst:,.2f}",
)

st.divider()


# ---------------------------------------------------------
# GST reconciliation
# ---------------------------------------------------------

st.subheader("GST Reconciliation")

reconciliation = pd.DataFrame(
    {
        "GST Component": [
            "Output GST",
            "Input GST",
            "Net GST",
        ],
        "Amount": [
            output_tax,
            input_tax,
            net_gst,
        ],
    }
)

st.dataframe(
    reconciliation,
    use_container_width=True,
    hide_index=True,
)

st.bar_chart(
    reconciliation.set_index(
        "GST Component"
    )
)


# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Transactions",
        "Tax Codes",
        "AR GST",
        "AP GST",
    ]
)

with tab1:

    st.subheader("GST Transaction Detail")

    display_columns = [
        "Source_ID",
        "Date",
        "GST_Amount",
        "Transaction_Type",
        "Direction",
        "Tax_Code",
        "Rate",
    ]

    st.dataframe(
        gst_filtered[
            [
                c
                for c in display_columns
                if c in gst_filtered.columns
            ]
        ].sort_values(
            "Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


with tab2:

    st.subheader("GST by Tax Code")

    tax_summary = (
        gst_filtered.groupby(
            "Tax_Code",
            dropna=False,
        )
        .agg(
            Transactions=(
                "Source_ID",
                "count",
            ),
            GST_Amount=(
                "GST_Amount",
                "sum",
            ),
        )
        .reset_index()
    )

    tax_summary = tax_summary.merge(
        tax_codes[
            [
                "Tax_Code",
                "Description",
                "Rate",
                "Tax_Type",
                "Recoverable",
                "Province_Scope",
            ]
        ],
        on="Tax_Code",
        how="left",
    )

    st.dataframe(
        tax_summary,
        use_container_width=True,
        hide_index=True,
    )


with tab3:

    st.subheader("GST on Accounts Receivable")

    ar_display = ar.copy()

    st.metric(
        "AR GST",
        f"${ar_display['GST'].sum():,.2f}",
    )

    st.dataframe(
        ar_display[
            [
                "AR_Invoice_ID",
                "Customer_ID",
                "Customer_Name",
                "Invoice_Date",
                "Net_Amount",
                "GST",
                "Gross_Amount",
                "Tax_Code",
                "Status",
            ]
        ].sort_values(
            "Invoice_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


with tab4:

    st.subheader("GST on Accounts Payable")

    ap_display = ap.copy()

    st.metric(
        "AP GST",
        f"${ap_display['GST'].sum():,.2f}",
    )

    st.dataframe(
        ap_display[
            [
                "AP_Invoice_ID",
                "Vendor_ID",
                "Vendor_Name",
                "Invoice_Date",
                "Net_Amount",
                "GST",
                "Gross_Amount",
                "Tax_Code",
                "Status",
            ]
        ].sort_values(
            "Invoice_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )


# ---------------------------------------------------------
# Compliance checks
# ---------------------------------------------------------

st.divider()

st.subheader("GST Compliance Checks")

checks = []

missing_tax_code = gst_filtered[
    gst_filtered["Tax_Code"].isna()
    | (
        gst_filtered["Tax_Code"]
        .astype(str)
        .str.strip()
        == ""
    )
]

invalid_rate = gst_filtered[
    (gst_filtered["Rate"] < 0)
    | (gst_filtered["Rate"] > 1)
]

zero_gst = gst_filtered[
    gst_filtered["GST_Amount"] == 0
]

checks.append(
    {
        "Check": "Missing Tax Code",
        "Count": len(missing_tax_code),
        "Status": (
            "Pass"
            if len(missing_tax_code) == 0
            else "Review"
        ),
    }
)

checks.append(
    {
        "Check": "Invalid GST Rate",
        "Count": len(invalid_rate),
        "Status": (
            "Pass"
            if len(invalid_rate) == 0
            else "Review"
        ),
    }
)

checks.append(
    {
        "Check": "Zero GST Amount",
        "Count": len(zero_gst),
        "Status": (
            "Pass"
            if len(zero_gst) == 0
            else "Review"
        ),
    }
)

checks_df = pd.DataFrame(checks)

st.dataframe(
    checks_df,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

csv = gst_filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    "Download GST Transactions",
    data=csv,
    file_name="gst_transactions.csv",
    mime="text/csv",
)
