import pandas as pd
import streamlit as st

from src.data_loader import data_loader


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Accounts Payable",
    page_icon="📤",
    layout="wide",
)


# ============================================================
# LOAD DATA
# ============================================================

data = data_loader()

company = data["company"]
vendors = data["vendors"]
ap_invoices = data["ap_invoices"].copy()
ap_payments = data["ap_payments"].copy()


# ============================================================
# PREPARE DATA
# ============================================================

for col in ["Invoice_Date", "Due_Date"]:
    if col in ap_invoices.columns:
        ap_invoices[col] = pd.to_datetime(
            ap_invoices[col],
            errors="coerce",
        )

if "Payment_Date" in ap_payments.columns:
    ap_payments["Payment_Date"] = pd.to_datetime(
        ap_payments["Payment_Date"],
        errors="coerce",
    )


money_columns = [
    "Net_Amount",
    "GST",
    "Gross_Amount",
    "Paid_Amount",
    "Outstanding_Balance",
]

for col in money_columns:
    if col in ap_invoices.columns:
        ap_invoices[col] = pd.to_numeric(
            ap_invoices[col],
            errors="coerce",
        ).fillna(0)

if "Amount" in ap_payments.columns:
    ap_payments["Amount"] = pd.to_numeric(
        ap_payments["Amount"],
        errors="coerce",
    ).fillna(0)


# ============================================================
# HELPERS
# ============================================================

def money(value):
    return f"${value:,.2f}"


def csv_download(df, filename):
    st.download_button(
        "⬇️ Download CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


# ============================================================
# COMPANY
# ============================================================

company_name = (
    company.iloc[0]["Company_Name"]
    if not company.empty
    else "Company"
)

currency = (
    company.iloc[0]["Currency"]
    if "Currency" in company.columns
    else "CAD"
)


# ============================================================
# HEADER
# ============================================================

st.title("📤 Accounts Payable")

st.caption(
    f"{company_name} • Accounts Payable Management • {currency}"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("AP Filters")

# Vendor
vendor_options = sorted(
    ap_invoices["Vendor_Name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_vendors = st.sidebar.multiselect(
    "Vendor",
    vendor_options,
)


# Status
status_options = sorted(
    ap_invoices["Status"]
    .dropna()
    .astype(str)
    .unique()
)

selected_status = st.sidebar.multiselect(
    "Invoice Status",
    status_options,
)


# Aging
aging_options = sorted(
    ap_invoices["Aging_Bucket"]
    .dropna()
    .astype(str)
    .unique()
)

selected_aging = st.sidebar.multiselect(
    "Aging Bucket",
    aging_options,
)


# Date range
date_values = ap_invoices["Invoice_Date"].dropna()

if not date_values.empty:

    min_date = date_values.min().date()
    max_date = date_values.max().date()

    date_range = st.sidebar.date_input(
        "Invoice Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

else:
    date_range = None


# ============================================================
# FILTER DATA
# ============================================================

df = ap_invoices.copy()

if selected_vendors:
    df = df[
        df["Vendor_Name"]
        .astype(str)
        .isin(selected_vendors)
    ]

if selected_status:
    df = df[
        df["Status"]
        .astype(str)
        .isin(selected_status)
    ]

if selected_aging:
    df = df[
        df["Aging_Bucket"]
        .astype(str)
        .isin(selected_aging)
    ]

if date_range and len(date_range) == 2:

    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    df = df[
        df["Invoice_Date"].between(
            start_date,
            end_date,
        )
    ]


# ============================================================
# KPI CALCULATIONS
# ============================================================

total_invoiced = df["Gross_Amount"].sum()
total_paid = df["Paid_Amount"].sum()
total_outstanding = df["Outstanding_Balance"].sum()

invoice_count = len(df)

# Overdue = anything other than current / not due
overdue_buckets = [
    bucket
    for bucket in df["Aging_Bucket"]
    .dropna()
    .astype(str)
    .unique()
    if bucket.lower() not in [
        "current",
        "not due",
        "0-30",
    ]
]

overdue_df = df[
    df["Aging_Bucket"]
    .astype(str)
    .isin(overdue_buckets)
]

overdue_amount = overdue_df["Outstanding_Balance"].sum()


# ============================================================
# KPI CARDS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "AP Invoiced",
    money(total_invoiced),
)

c2.metric(
    "AP Paid",
    money(total_paid),
)

c3.metric(
    "AP Outstanding",
    money(total_outstanding),
)

c4.metric(
    "Overdue",
    money(overdue_amount),
)


st.divider()


# ============================================================
# AGING ANALYSIS
# ============================================================

st.subheader("AP Aging")

if not df.empty:

    aging = (
        df.groupby("Aging_Bucket", dropna=False)
        .agg(
            Invoice_Count=("AP_Invoice_ID", "count"),
            Outstanding=("Outstanding_Balance", "sum"),
        )
        .reset_index()
    )

    aging = aging.sort_values(
        "Outstanding",
        ascending=False,
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        st.dataframe(
            aging,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Invoice_Count": st.column_config.NumberColumn(
                    "Invoices",
                    format="%d",
                ),
                "Outstanding": st.column_config.NumberColumn(
                    "Outstanding",
                    format="$%,.2f",
                ),
            },
        )

    with col2:

        chart = aging.set_index(
            "Aging_Bucket"
        )["Outstanding"]

        st.bar_chart(
            chart,
            color="#E74C3C",
        )

else:
    st.info("No AP aging data for the selected filters.")


st.divider()


# ============================================================
# VENDOR SUMMARY
# ============================================================

st.subheader("Outstanding by Vendor")

if not df.empty:

    vendor_summary = (
        df.groupby(
            ["Vendor_ID", "Vendor_Name"],
            dropna=False,
        )
        .agg(
            Invoices=("AP_Invoice_ID", "count"),
            Invoiced=("Gross_Amount", "sum"),
            Paid=("Paid_Amount", "sum"),
            Outstanding=("Outstanding_Balance", "sum"),
        )
        .reset_index()
        .sort_values(
            "Outstanding",
            ascending=False,
        )
    )

    st.dataframe(
        vendor_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Invoices": st.column_config.NumberColumn(
                "Invoices",
                format="%d",
            ),
            "Invoiced": st.column_config.NumberColumn(
                "Invoiced",
                format="$%,.2f",
            ),
            "Paid": st.column_config.NumberColumn(
                "Paid",
                format="$%,.2f",
            ),
            "Outstanding": st.column_config.NumberColumn(
                "Outstanding",
                format="$%,.2f",
            ),
        },
    )

    csv_download(
        vendor_summary,
        "accounts_payable_vendor_summary.csv",
    )


st.divider()


# ============================================================
# INVOICE SEARCH
# ============================================================

st.subheader("AP Invoice Register")

search = st.text_input(
    "Search invoices",
    placeholder="Invoice ID, vendor, project, account...",
)


invoice_df = df.copy()

if search:

    search = search.lower()

    columns = [
        "AP_Invoice_ID",
        "Vendor_ID",
        "Vendor_Name",
        "Project_ID",
        "Department_ID",
        "Expense_Account",
        "Tax_Code",
    ]

    columns = [
        col
        for col in columns
        if col in invoice_df.columns
    ]

    mask = pd.Series(
        False,
        index=invoice_df.index,
    )

    for col in columns:

        mask |= (
            invoice_df[col]
            .astype(str)
            .str.lower()
            .str.contains(
                search,
                na=False,
            )
        )

    invoice_df = invoice_df[mask]


display_columns = [
    "AP_Invoice_ID",
    "Vendor_ID",
    "Vendor_Name",
    "Project_ID",
    "Department_ID",
    "Invoice_Date",
    "Due_Date",
    "Net_Amount",
    "GST",
    "Gross_Amount",
    "Paid_Amount",
    "Outstanding_Balance",
    "Status",
    "Tax_Code",
    "Aging_Bucket",
]

display_columns = [
    col
    for col in display_columns
    if col in invoice_df.columns
]


st.dataframe(
    invoice_df[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Invoice_Date": st.column_config.DateColumn(
            "Invoice Date"
        ),
        "Due_Date": st.column_config.DateColumn(
            "Due Date"
        ),
        "Net_Amount": st.column_config.NumberColumn(
            "Net",
            format="$%,.2f",
        ),
        "GST": st.column_config.NumberColumn(
            "GST",
            format="$%,.2f",
        ),
        "Gross_Amount": st.column_config.NumberColumn(
            "Gross",
            format="$%,.2f",
        ),
        "Paid_Amount": st.column_config.NumberColumn(
            "Paid",
            format="$%,.2f",
        ),
        "Outstanding_Balance": st.column_config.NumberColumn(
            "Outstanding",
            format="$%,.2f",
        ),
    },
)

csv_download(
    invoice_df,
    "accounts_payable_invoices.csv",
)


st.divider()


# ============================================================
# PAYMENT REGISTER
# ============================================================

st.subheader("AP Payment Register")

payments = ap_payments.copy()

if not df.empty:

    payments = payments[
        payments["AP_Invoice_ID"].isin(
            df["AP_Invoice_ID"]
        )
    ]

if not payments.empty:

    payments = payments.merge(
        ap_invoices[
            [
                "AP_Invoice_ID",
                "Vendor_Name",
            ]
        ].drop_duplicates(),
        on="AP_Invoice_ID",
        how="left",
    )

    payment_columns = [
        "AP_Payment_ID",
        "AP_Invoice_ID",
        "Vendor_ID",
        "Vendor_Name",
        "Payment_Date",
        "Amount",
        "Bank_Account_ID",
        "Reference",
    ]

    payment_columns = [
        col
        for col in payment_columns
        if col in payments.columns
    ]

    st.dataframe(
        payments[payment_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Payment_Date": st.column_config.DateColumn(
                "Payment Date"
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format="$%,.2f",
            ),
        },
    )

    csv_download(
        payments,
        "accounts_payable_payments.csv",
    )

else:
    st.info("No AP payments for the selected filters.")


st.divider()

st.caption(
    f"Showing {len(df):,} AP invoices from the loaded Excel data."
)
