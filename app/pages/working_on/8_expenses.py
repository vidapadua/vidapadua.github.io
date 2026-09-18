import pandas as pd
import streamlit as st

from src.data_loader import data_loader


st.set_page_config(
    page_title="Expenses",
    page_icon="💳",
    layout="wide",
)


# ============================================================
# LOAD DATA
# ============================================================

data = data_loader()

company = data["company"]
expense_reports = data["expense_reports"].copy()
credit_card_transactions = data["credit_card_transactions"].copy()
payroll_transactions = data["payroll_transactions"].copy()


# ============================================================
# PREPARE DATA
# ============================================================

expense_reports["Date"] = pd.to_datetime(
    expense_reports["Date"],
    errors="coerce",
)

for col in ["Amount", "GST", "Total_Amount"]:
    expense_reports[col] = pd.to_numeric(
        expense_reports[col],
        errors="coerce",
    ).fillna(0)


credit_card_transactions["Transaction_Date"] = pd.to_datetime(
    credit_card_transactions["Transaction_Date"],
    errors="coerce",
)

for col in ["Net_Amount", "GST", "Total_Amount"]:
    credit_card_transactions[col] = pd.to_numeric(
        credit_card_transactions[col],
        errors="coerce",
    ).fillna(0)


payroll_transactions["Payroll_Period"] = pd.to_datetime(
    payroll_transactions["Payroll_Period"],
    errors="coerce",
)

for col in [
    "Gross_Wages",
    "Employer_Benefits",
    "Employee_Withholdings",
    "Net_Pay",
    "Payroll_Liability",
]:
    payroll_transactions[col] = pd.to_numeric(
        payroll_transactions[col],
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

st.title("💳 Expenses")

st.caption(
    f"{company_name} • Expense Management • {currency}"
)

st.divider()


# ============================================================
# FILTERS
# ============================================================

st.sidebar.header("Expense Filters")

categories = sorted(
    expense_reports["Expense_Category"]
    .dropna()
    .astype(str)
    .unique()
)

selected_categories = st.sidebar.multiselect(
    "Expense Category",
    categories,
)


employees = sorted(
    expense_reports["Employee_ID"]
    .dropna()
    .astype(str)
    .unique()
)

selected_employees = st.sidebar.multiselect(
    "Employee",
    employees,
)


projects = sorted(
    expense_reports["Project_ID"]
    .dropna()
    .astype(str)
    .unique()
)

selected_projects = st.sidebar.multiselect(
    "Project",
    projects,
)


approval_statuses = sorted(
    expense_reports["Approval_Status"]
    .dropna()
    .astype(str)
    .unique()
)

selected_approval = st.sidebar.multiselect(
    "Approval Status",
    approval_statuses,
)


reimbursement_statuses = sorted(
    expense_reports["Reimbursement_Status"]
    .dropna()
    .astype(str)
    .unique()
)

selected_reimbursement = st.sidebar.multiselect(
    "Reimbursement Status",
    reimbursement_statuses,
)


# ============================================================
# FILTER EXPENSE REPORTS
# ============================================================

df = expense_reports.copy()


if selected_categories:
    df = df[
        df["Expense_Category"]
        .astype(str)
        .isin(selected_categories)
    ]


if selected_employees:
    df = df[
        df["Employee_ID"]
        .astype(str)
        .isin(selected_employees)
    ]


if selected_projects:
    df = df[
        df["Project_ID"]
        .astype(str)
        .isin(selected_projects)
    ]


if selected_approval:
    df = df[
        df["Approval_Status"]
        .astype(str)
        .isin(selected_approval)
    ]


if selected_reimbursement:
    df = df[
        df["Reimbursement_Status"]
        .astype(str)
        .isin(selected_reimbursement)
    ]


# ============================================================
# KPI
# ============================================================

total_expenses = df["Total_Amount"].sum()
total_net = df["Amount"].sum()
total_gst = df["GST"].sum()

approved = df[
    df["Approval_Status"]
    .astype(str)
    .str.lower()
    .eq("approved")
]["Total_Amount"].sum()

pending = df[
    df["Approval_Status"]
    .astype(str)
    .str.lower()
    .str.contains("pending", na=False)
]["Total_Amount"].sum()


c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Total Expenses",
    money(total_expenses),
)

c2.metric(
    "Net Expenses",
    money(total_net),
)

c3.metric(
    "GST",
    money(total_gst),
)

c4.metric(
    "Approved",
    money(approved),
)

c5.metric(
    "Pending",
    money(pending),
)


st.divider()


# ============================================================
# EXPENSE CATEGORY ANALYSIS
# ============================================================

st.subheader("Expenses by Category")

if not df.empty:

    category_summary = (
        df.groupby(
            "Expense_Category",
            dropna=False,
        )
        .agg(
            Reports=("Expense_Report_ID", "count"),
            Net=("Amount", "sum"),
            GST=("GST", "sum"),
            Total=("Total_Amount", "sum"),
        )
        .reset_index()
        .sort_values(
            "Total",
            ascending=False,
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        st.dataframe(
            category_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Net": st.column_config.NumberColumn(
                    "Net",
                    format="$%,.2f",
                ),
                "GST": st.column_config.NumberColumn(
                    "GST",
                    format="$%,.2f",
                ),
                "Total": st.column_config.NumberColumn(
                    "Total",
                    format="$%,.2f",
                ),
            },
        )

    with col2:

        st.bar_chart(
            category_summary.set_index(
                "Expense_Category"
            )["Total"],
            color="#E67E22",
        )

else:
    st.info("No expense data found.")


st.divider()


# ============================================================
# EMPLOYEE EXPENSES
# ============================================================

st.subheader("Expenses by Employee")

if not df.empty:

    employee_summary = (
        df.groupby(
            "Employee_ID",
            dropna=False,
        )
        .agg(
            Reports=("Expense_Report_ID", "count"),
            Total=("Total_Amount", "sum"),
        )
        .reset_index()
        .sort_values(
            "Total",
            ascending=False,
        )
    )

    st.dataframe(
        employee_summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total": st.column_config.NumberColumn(
                "Total",
                format="$%,.2f",
            ),
        },
    )

    download_csv(
        employee_summary,
        "employee_expense_summary.csv",
    )


st.divider()


# ============================================================
# EXPENSE REPORT REGISTER
# ============================================================

st.subheader("Expense Report Register")

search = st.text_input(
    "Search",
    placeholder="Report ID, employee, merchant, category, project...",
)

detail = df.copy()

if search:

    search = search.lower()

    search_columns = [
        "Expense_Report_ID",
        "Employee_ID",
        "Merchant",
        "Expense_Category",
        "Project_ID",
        "Approval_Status",
        "Reimbursement_Status",
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
    "Expense_Report_ID",
    "Employee_ID",
    "Date",
    "Merchant",
    "Expense_Category",
    "Project_ID",
    "Amount",
    "GST",
    "Total_Amount",
    "Receipt_Status",
    "Approval_Status",
    "Reimbursement_Status",
]

st.dataframe(
    detail[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn(
            "Date"
        ),
        "Amount": st.column_config.NumberColumn(
            "Net",
            format="$%,.2f",
        ),
        "GST": st.column_config.NumberColumn(
            "GST",
            format="$%,.2f",
        ),
        "Total_Amount": st.column_config.NumberColumn(
            "Total",
            format="$%,.2f",
        ),
    },
)

download_csv(
    detail,
    "expense_reports.csv",
)


st.divider()


# ============================================================
# CREDIT CARD EXPENSES
# ============================================================

st.subheader("Credit Card Expenses")

card_summary = (
    credit_card_transactions
    .groupby(
        "Category",
        dropna=False,
    )
    .agg(
        Transactions=(
            "Credit_Card_Transaction_ID",
            "count",
        ),
        Net=("Net_Amount", "sum"),
        GST=("GST", "sum"),
        Total=("Total_Amount", "sum"),
    )
    .reset_index()
    .sort_values(
        "Total",
        ascending=False,
    )
)

st.dataframe(
    card_summary,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Net": st.column_config.NumberColumn(
            "Net",
            format="$%,.2f",
        ),
        "GST": st.column_config.NumberColumn(
            "GST",
            format="$%,.2f",
        ),
        "Total": st.column_config.NumberColumn(
            "Total",
            format="$%,.2f",
        ),
    },
)

download_csv(
    credit_card_transactions,
    "credit_card_transactions.csv",
)


st.divider()


# ============================================================
# PAYROLL EXPENSE
# ============================================================

st.subheader("Payroll Expense")

gross_wages = payroll_transactions[
    "Gross_Wages"
].sum()

benefits = payroll_transactions[
    "Employer_Benefits"
].sum()

total_payroll = (
    gross_wages +
    benefits
)


p1, p2, p3 = st.columns(3)

p1.metric(
    "Gross Wages",
    money(gross_wages),
)

p2.metric(
    "Employer Benefits",
    money(benefits),
)

p3.metric(
    "Total Payroll Cost",
    money(total_payroll),
)


payroll_by_department = (
    payroll_transactions
    .groupby(
        "Department_ID",
        dropna=False,
    )
    .agg(
        Employees=("Employee_ID", "nunique"),
        Gross_Wages=("Gross_Wages", "sum"),
        Benefits=("Employer_Benefits", "sum"),
    )
    .reset_index()
)

payroll_by_department["Total_Cost"] = (
    payroll_by_department["Gross_Wages"]
    + payroll_by_department["Benefits"]
)

st.dataframe(
    payroll_by_department,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Gross_Wages": st.column_config.NumberColumn(
            "Gross Wages",
            format="$%,.2f",
        ),
        "Benefits": st.column_config.NumberColumn(
            "Benefits",
            format="$%,.2f",
        ),
        "Total_Cost": st.column_config.NumberColumn(
            "Total Cost",
            format="$%,.2f",
        ),
    },
)

download_csv(
    payroll_by_department,
    "payroll_by_department.csv",
)