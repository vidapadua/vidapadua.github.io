import pandas as pd
import streamlit as st

from src.data_loader import data_loader


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Accounts Receivable",
    page_icon="📥",
    layout="wide",
)


# ============================================================
# LOAD DATA
# ============================================================

data = data_loader()

company = data["company"]
customers = data["customers"]
ar_invoices = data["ar_invoices"].copy()
ar_receipts = data["ar_receipts"].copy()


# ============================================================
# PREPARE DATA
# ============================================================

for col in ["Invoice_Date", "Due_Date"]:
    if col in ar_invoices.columns:
        ar_invoices[col] = pd.to_datetime(
            ar_invoices[col],
            errors="coerce",
        )

if "Receipt_Date" in ar_receipts.columns:
    ar_receipts["Receipt_Date"] = pd.to_datetime(
        ar_receipts["Receipt_Date"],
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
    if col in ar_invoices.columns:
        ar_invoices[col] = pd.to_numeric(
            ar_invoices[col],
            errors="coerce",
        ).fillna(0)

if "Amount" in ar_receipts.columns:
    ar_receipts["Amount"] = pd.to_numeric(
        ar_receipts["Amount"],
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

st.title("📥 Accounts Receivable")

st.caption(
    f"{company_name} • Accounts Receivable Management • {currency}"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("AR Filters")


# Customer
customer_options = sorted(
    ar_invoices["Customer_Name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_customers = st.sidebar.multiselect(
    "Customer",
    customer_options,
)


# Status
status_options = sorted(
    ar_invoices["Status"]
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
    ar_invoices["Aging_Bucket"]
    .dropna()
    .astype(str)
    .unique()
)

selected_aging = st.sidebar.multiselect(
    "Aging Bucket",
    aging_options,
)


# Date range
date_values = ar_invoices["Invoice_Date"].dropna()

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

df = ar_invoices.copy()


if selected_customers:
    df = df[
        df["Customer_Name"]
        .astype(str)
        .isin(selected_customers)
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
total_collected = df["Paid_Amount"].sum()
total_outstanding = df["Outstanding_Balance"].sum()

invoice_count = len(df)


# Determine overdue
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
    "AR Invoiced",
    money(total_invoiced),
)

c2.metric(
    "AR Collected",
    money(total_collected),
)

c3.metric(
    "AR Outstanding",
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

st.subheader("AR Aging")

if not df.empty:

    aging = (
        df.groupby("Aging_Bucket", dropna=False)
        .agg(
            Invoice_Count=("AR_Invoice_ID", "count"),
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
            color="#2E86DE",
        )

else:
    st.info("No AR aging data for the selected filters.")


st.divider()


# ============================================================
# CUSTOMER SUMMARY
# ============================================================

st.subheader("Outstanding by Customer")

if not df.empty:

    customer_summary = (
        df.groupby(
            ["Customer_ID", "Customer_Name"],
            dropna=False,
        )
        .agg(
            Invoices=("AR_Invoice_ID", "count"),
            Invoiced=("Gross_Amount", "sum"),
            Collected=("Paid_Amount", "sum"),
            Outstanding=("Outstanding_Balance", "sum"),
        )
        .reset_index()
        .sort_values(
            "Outstanding",
            ascending=False,
        )
    )

    st.dataframe(
        customer_summary,
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
            "Collected": st.column_config.NumberColumn(
                "Collected",
                format="$%,.2f",
            ),
            "Outstanding": st.column_config.NumberColumn(
                "Outstanding",
                format="$%,.2f",
            ),
        },
    )

    csv_download(
        customer_summary,
        "accounts_receivable_customer_summary.csv",
    )


st.divider()


# ============================================================
# INVOICE SEARCH
# ============================================================

st.subheader("AR Invoice Register")

search = st.text_input(
    "Search invoices",
    placeholder="Invoice ID, customer, project, account...",
)


invoice_df = df.copy()


if search:

    search = search.lower()

    columns = [
        "AR_Invoice_ID",
        "Customer_ID",
        "Customer_Name",
        "Project_ID",
        "Revenue_Account",
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
    "AR_Invoice_ID",
    "Customer_ID",
    "Customer_Name",
    "Project_ID",
    "Revenue_Account",
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
            "Collected",
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
    "accounts_receivable_invoices.csv",
)


st.divider()


# ============================================================
# RECEIPT REGISTER
# ============================================================

st.subheader("AR Receipt Register")

receipts = ar_receipts.copy()


if not df.empty:

    receipts = receipts[
        receipts["AR_Invoice_ID"].isin(
            df["AR_Invoice_ID"]
        )
    ]


if not receipts.empty:

    receipts = receipts.merge(
        ar_invoices[
            [
                "AR_Invoice_ID",
                "Customer_Name",
            ]
        ].drop_duplicates(),
        on="AR_Invoice_ID",
        how="left",
    )

    receipt_columns = [
        "AR_Receipt_ID",
        "AR_Invoice_ID",
        "Customer_ID",
        "Customer_Name",
        "Receipt_Date",
        "Amount",
        "Bank_Account_ID",
        "Reference",
    ]

    receipt_columns = [
        col
        for col in receipt_columns
        if col in receipts.columns
    ]

    st.dataframe(
        receipts[receipt_columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Receipt_Date": st.column_config.DateColumn(
                "Receipt Date"
            ),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format="$%,.2f",
            ),
        },
    )

    csv_download(
        receipts,
        "accounts_receivable_receipts.csv",
    )

else:
    st.info(
        "No AR receipts for the selected filters."
    )


st.divider()

st.caption(
    f"Showing {len(df):,} AR invoices from the loaded Excel data."
)