import streamlit as st
import pandas as pd

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Full-Cycle Accounting Demo",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Sample accounting data
# -----------------------------
transactions = [
    {
        "Date": "2026-09-01",
        "Reference": "INV-1001",
        "Description": "Customer invoice - landscaping services",
        "Account": "Accounts Receivable",
        "Debit": 2500,
        "Credit": 0
    },
    {
        "Date": "2026-09-01",
        "Reference": "INV-1001",
        "Description": "Customer invoice - landscaping services",
        "Account": "Service Revenue",
        "Debit": 0,
        "Credit": 2500
    },
    {
        "Date": "2026-09-03",
        "Reference": "PAY-1001",
        "Description": "Customer payment received",
        "Account": "Cash",
        "Debit": 2500,
        "Credit": 0
    },
    {
        "Date": "2026-09-03",
        "Reference": "PAY-1001",
        "Description": "Customer payment received",
        "Account": "Accounts Receivable",
        "Debit": 0,
        "Credit": 2500
    },
    {
        "Date": "2026-09-05",
        "Reference": "BILL-1001",
        "Description": "Office supplies purchased",
        "Account": "Office Supplies Expense",
        "Debit": 300,
        "Credit": 0
    },
    {
        "Date": "2026-09-05",
        "Reference": "BILL-1001",
        "Description": "Office supplies purchased",
        "Account": "Accounts Payable",
        "Debit": 0,
        "Credit": 300
    },
    {
        "Date": "2026-09-10",
        "Reference": "PAY-1002",
        "Description": "Vendor payment",
        "Account": "Accounts Payable",
        "Debit": 300,
        "Credit": 0
    },
    {
        "Date": "2026-09-10",
        "Reference": "PAY-1002",
        "Description": "Vendor payment",
        "Account": "Cash",
        "Debit": 0,
        "Credit": 300
    }
]

df = pd.DataFrame(transactions)

# -----------------------------
# Header
# -----------------------------
st.title("📊 Full-Cycle Accounting Demonstration")
st.caption(
    "A fictional landscaping company | September 2026 | "
    "Interactive accounting portfolio project"
)

st.divider()

# -----------------------------
# Sidebar navigation
# -----------------------------
st.sidebar.title("Accounting Modules")

page = st.sidebar.radio(
    "Navigate to:",
    [
        "Dashboard",
        "Journal Entries",
        "General Ledger",
        "Trial Balance",
        "Income Statement"
    ]
)

# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":

    st.header("Accounting Dashboard")

    st.write(
        "This application demonstrates how business transactions "
        "flow from source documents into journal entries, the general "
        "ledger, and financial statements."
    )

    total_debits = df["Debit"].sum()
    total_credits = df["Credit"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Transactions", len(df) // 2)
    col2.metric("Total Debits", f"${total_debits:,.2f}")
    col3.metric("Total Credits", f"${total_credits:,.2f}")
    col4.metric(
        "Trial Balance",
        "Balanced" if total_debits == total_credits else "Out of Balance"
    )

    st.subheader("Accounting Cycle")

    st.info(
        "Source Documents → Transaction Processing → "
        "Journal Entries → General Ledger → Trial Balance → "
        "Financial Statements"
    )

    st.subheader("Sample Transactions")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# -----------------------------
# Journal Entries
# -----------------------------
elif page == "Journal Entries":

    st.header("Journal Entries")

    st.write(
        "Each business transaction is recorded using equal debits and credits."
    )

    journal = df[
        ["Date", "Reference", "Description", "Account", "Debit", "Credit"]
    ]

    st.dataframe(
        journal,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Accounting Control")

    debit_total = journal["Debit"].sum()
    credit_total = journal["Credit"].sum()

    st.write(f"**Total Debits:** ${debit_total:,.2f}")
    st.write(f"**Total Credits:** ${credit_total:,.2f}")

    if debit_total == credit_total:
        st.success("✓ Journal entries are balanced.")
    else:
        st.error("Journal entries are out of balance.")

# -----------------------------
# General Ledger
# -----------------------------
elif page == "General Ledger":

    st.header("General Ledger")

    account = st.selectbox(
        "Select an account",
        sorted(df["Account"].unique())
    )

    ledger = df[df["Account"] == account].copy()

    ledger["Net Change"] = ledger["Debit"] - ledger["Credit"]
    ledger["Running Balance"] = ledger["Net Change"].cumsum()

    st.dataframe(
        ledger[
            [
                "Date",
                "Reference",
                "Description",
                "Debit",
                "Credit",
                "Running Balance"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    balance = ledger["Net Change"].sum()

    st.metric(
        f"{account} Balance",
        f"${balance:,.2f}"
    )

# -----------------------------
# Trial Balance
# -----------------------------
elif page == "Trial Balance":

    st.header("Trial Balance")

    trial_balance = (
        df.groupby("Account")[["Debit", "Credit"]]
        .sum()
        .reset_index()
    )

    trial_balance["Balance"] = (
        trial_balance["Debit"] - trial_balance["Credit"]
    )

    st.dataframe(
        trial_balance,
        use_container_width=True,
        hide_index=True
    )

    total_debits = trial_balance["Debit"].sum()
    total_credits = trial_balance["Credit"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Debits", f"${total_debits:,.2f}")
    col2.metric("Total Credits", f"${total_credits:,.2f}")
    col3.metric(
        "Status",
        "Balanced" if total_debits == total_credits else "Out of Balance"
    )

# -----------------------------
# Income Statement
# -----------------------------
elif page == "Income Statement":

    st.header("Income Statement")

    revenue = df.loc[
        df["Account"] == "Service Revenue", "Credit"
    ].sum()

    expenses = df.loc[
        df["Account"] == "Office Supplies Expense", "Debit"
    ].sum()

    net_income = revenue - expenses

    st.subheader("Fictional Landscaping Company")
    st.caption("For the month ended September 30, 2026")

    col1, col2, col3 = st.columns(3)

    col1.metric("Revenue", f"${revenue:,.2f}")
    col2.metric("Expenses", f"${expenses:,.2f}")
    col3.metric("Net Income", f"${net_income:,.2f}")

    st.divider()

    income_statement = pd.DataFrame({
        "Account": [
            "Service Revenue",
            "Office Supplies Expense",
            "Net Income"
        ],
        "Amount": [
            revenue,
            -expenses,
            net_income
        ]
    })

    st.dataframe(
        income_statement,
        use_container_width=True,
        hide_index=True
    )

    st.success(
        "This report is generated from the underlying transaction data."
    )