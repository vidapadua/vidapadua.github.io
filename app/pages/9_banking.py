import pandas as pd
import streamlit as st

from src.data_loader import data_loader


st.set_page_config(
    page_title="Banking",
    page_icon="🏦",
    layout="wide",
)


# ============================================================
# LOAD DATA
# ============================================================

data = data_loader()

company = data["company"]
bank = data["bank"].copy()


# ============================================================
# PREPARE DATA
# ============================================================

for col in [
    "Posting_Date",
    "Value_Date",
]:
    bank[col] = pd.to_datetime(
        bank[col],
        errors="coerce",
    )


for col in [
    "Debit",
    "Credit",
    "Running_Balance",
]:
    bank[col] = pd.to_numeric(
        bank[col],
        errors="coerce",
    ).fillna(0)


# ============================================================
# HELPERS
# ============================================================

def money(value):
    return f"${value:,.2f}"


def download_csv(df, filename):
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

st.title("🏦 Banking")

st.caption(
    f"{company_name} • Banking & Cash Management • {currency}"
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Banking Filters")


bank_accounts = sorted(
    bank["Bank_Account_ID"]
    .dropna()
    .astype(str)
    .unique()
)

selected_accounts = st.sidebar.multiselect(
    "Bank Account",
    bank_accounts,
)


document_types = sorted(
    bank["Document_Type"]
    .dropna()
    .astype(str)
    .unique()
)

selected_documents = st.sidebar.multiselect(
    "Transaction Type",
    document_types,
)


# ============================================================
# DATE FILTER
# ============================================================

dates = bank["Posting_Date"].dropna()

if not dates.empty:

    min_date = dates.min().date()
    max_date = dates.max().date()

    date_range = st.sidebar.date_input(
        "Posting Date",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

else:
    date_range = None


# ============================================================
# FILTER
# ============================================================

df = bank.copy()


if selected_accounts:

    df = df[
        df["Bank_Account_ID"]
        .astype(str)
        .isin(selected_accounts)
    ]


if selected_documents:

    df = df[
        df["Document_Type"]
        .astype(str)
        .isin(selected_documents)
    ]


if date_range and len(date_range) == 2:

    start_date = pd.Timestamp(
        date_range[0]
    )

    end_date = pd.Timestamp(
        date_range[1]
    )

    df = df[
        df["Posting_Date"].between(
            start_date,
            end_date,
        )
    ]


# ============================================================
# KPI
# ============================================================

money_in = df["Credit"].sum()
money_out = df["Debit"].sum()

net_cash_flow = (
    money_in -
    money_out
)

transaction_count = len(df)


# Latest balance per account
latest_balances = (
    df.sort_values(
        "Posting_Date"
    )
    .groupby(
        "Bank_Account_ID",
        as_index=False,
    )
    .tail(1)
)

total_balance = latest_balances[
    "Running_Balance"
].sum()


c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Bank Balance",
    money(total_balance),
)

c2.metric(
    "Money In",
    money(money_in),
)

c3.metric(
    "Money Out",
    money(money_out),
)

c4.metric(
    "Net Cash Flow",
    money(net_cash_flow),
)


st.divider()


# ============================================================
# CASH FLOW
# ============================================================

st.subheader("Cash Flow")

if not df.empty:

    daily = (
        df.groupby("Posting_Date")
        .agg(
            Money_In=("Credit", "sum"),
            Money_Out=("Debit", "sum"),
        )
        .reset_index()
    )

    daily["Net_Cash_Flow"] = (
        daily["Money_In"]
        - daily["Money_Out"]
    )

    daily = daily.set_index(
        "Posting_Date"
    )

    st.line_chart(
        daily[
            [
                "Money_In",
                "Money_Out",
                "Net_Cash_Flow",
            ]
        ]
    )


st.divider()


# ============================================================
# BANK ACCOUNT SUMMARY
# ============================================================

st.subheader("Bank Account Balances")

if not latest_balances.empty:

    account_summary = latest_balances[
        [
            "Bank_Account_ID",
            "Posting_Date",
            "Running_Balance",
        ]
    ].sort_values(
        "Running_Balance",
        ascending=False,
    )

    st.dataframe(
        account_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Posting_Date": st.column_config.DateColumn(
                "Last Transaction"
            ),
            "Running_Balance": st.column_config.NumberColumn(
                "Balance",
                format="$%,.2f",
            ),
        },
    )

    download_csv(
        account_summary,
        "bank_account_balances.csv",
    )


st.divider()


# ============================================================
# TRANSACTION TYPE
# ============================================================

st.subheader("Bank Activity by Transaction Type")

if not df.empty:

    type_summary = (
        df.groupby(
            "Document_Type",
            dropna=False,
        )
        .agg(
            Transactions=(
                "Bank_Transaction_ID",
                "count",
            ),
            Debits=(
                "Debit",
                "sum",
            ),
            Credits=(
                "Credit",
                "sum",
            ),
        )
        .reset_index()
    )

    type_summary["Net"] = (
        type_summary["Credits"]
        - type_summary["Debits"]
    )

    st.dataframe(
        type_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Debits": st.column_config.NumberColumn(
                "Debits",
                format="$%,.2f",
            ),
            "Credits": st.column_config.NumberColumn(
                "Credits",
                format="$%,.2f",
            ),
            "Net": st.column_config.NumberColumn(
                "Net",
                format="$%,.2f",
            ),
        },
    )


st.divider()


# ============================================================
# BANK TRANSACTION REGISTER
# ============================================================

st.subheader("Bank Transaction Register")

search = st.text_input(
    "Search transactions",
    placeholder="Transaction ID, document, description, reference...",
)


detail = df.copy()


if search:

    search = search.lower()

    search_columns = [
        "Bank_Transaction_ID",
        "Document_ID",
        "Document_Type",
        "Description",
        "Bank_Account_ID",
        "Reference",
    ]

    mask = pd.Series(
        False,
        index=detail.index,
    )

    for col in search_columns:

        if col in detail.columns:

            mask |= (
                detail[col]
                .astype(str)
                .str.lower()
                .str.contains(
                    search,
                    na=False,
                )
            )

    detail = detail[mask]


display_columns = [
    "Bank_Transaction_ID",
    "Posting_Date",
    "Document_ID",
    "Document_Type",
    "Description",
    "Debit",
    "Credit",
    "Bank_Account_ID",
    "Value_Date",
    "Reference",
    "Running_Balance",
]


st.dataframe(
    detail[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Posting_Date": st.column_config.DateColumn(
            "Posting Date"
        ),
        "Value_Date": st.column_config.DateColumn(
            "Value Date"
        ),
        "Debit": st.column_config.NumberColumn(
            "Debit",
            format="$%,.2f",
        ),
        "Credit": st.column_config.NumberColumn(
            "Credit",
            format="$%,.2f",
        ),
        "Running_Balance": st.column_config.NumberColumn(
            "Running Balance",
            format="$%,.2f",
        ),
    },
)


download_csv(
    detail,
    "bank_transactions.csv",
)


st.divider()


# ============================================================
# BANK TRANSACTION COUNT
# ============================================================

st.caption(
    f"Showing {len(df):,} bank transactions."
)