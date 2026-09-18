import streamlit as st
import pandas as pd

from src.data_loader import data_loader


st.set_page_config(
    page_title="Credit Card Reconciliation",
    page_icon="💳",
    layout="wide",
)


@st.cache_data
def prepare_credit_card_data():
    data = data_loader()

    cc = data["credit_card_transactions"].copy()
    employees = data["employees"].copy()
    departments = data["departments"].copy()

    cc["Transaction_Date"] = pd.to_datetime(
        cc["Transaction_Date"],
        errors="coerce",
    )

    cc["Total_Amount"] = pd.to_numeric(
        cc["Total_Amount"],
        errors="coerce",
    ).fillna(0)

    cc["GST"] = pd.to_numeric(
        cc["GST"],
        errors="coerce",
    ).fillna(0)

    cc["Net_Amount"] = pd.to_numeric(
        cc["Net_Amount"],
        errors="coerce",
    ).fillna(0)

    cc = cc.merge(
        employees[
            ["Employee_ID", "Employee_Name", "Department"]
        ],
        on="Employee_ID",
        how="left",
        suffixes=("", "_Employee"),
    )

    return data, cc, departments


data, cc, departments = prepare_credit_card_data()

st.title("💳 Credit Card Reconciliation")
st.caption(
    "Review credit card transactions, employee expenses, approvals, "
    "and transactions requiring attention."
)

# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.header("Filters")

min_date = cc["Transaction_Date"].min()
max_date = cc["Transaction_Date"].max()

date_range = st.sidebar.date_input(
    "Transaction date",
    value=(min_date.date(), max_date.date()),
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range

    filtered = cc[
        (cc["Transaction_Date"].dt.date >= start_date)
        & (cc["Transaction_Date"].dt.date <= end_date)
    ].copy()
else:
    filtered = cc.copy()

employees = sorted(
    filtered["Employee_Name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_employee = st.sidebar.selectbox(
    "Employee",
    ["All"] + employees,
)

if selected_employee != "All":
    filtered = filtered[
        filtered["Employee_Name"] == selected_employee
    ]

categories = sorted(
    filtered["Category"]
    .dropna()
    .astype(str)
    .unique()
)

selected_category = st.sidebar.selectbox(
    "Category",
    ["All"] + categories,
)

if selected_category != "All":
    filtered = filtered[
        filtered["Category"] == selected_category
    ]

# ---------------------------------------------------------
# Metrics
# ---------------------------------------------------------

total_spend = filtered["Total_Amount"].sum()
total_gst = filtered["GST"].sum()
total_net = filtered["Net_Amount"].sum()

pending = (
    filtered["Status"]
    .astype(str)
    .str.lower()
    .isin(["pending", "review", "unapproved"])
    .sum()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Transactions",
    f"{len(filtered):,}",
)

c2.metric(
    "Total Spend",
    f"${total_spend:,.2f}",
)

c3.metric(
    "GST",
    f"${total_gst:,.2f}",
)

c4.metric(
    "Pending / Review",
    f"{pending:,}",
)

st.divider()

# ---------------------------------------------------------
# Reconciliation checks
# ---------------------------------------------------------

st.subheader("Reconciliation Checks")

review = filtered.copy()

review["Review_Reason"] = ""

review.loc[
    review["Total_Amount"] <= 0,
    "Review_Reason",
] = "Zero or negative amount"

review.loc[
    review["GL_Account_ID"].isna(),
    "Review_Reason",
] = "Missing GL account"

review.loc[
    review["Employee_ID"].isna(),
    "Review_Reason",
] = "Missing employee"

review.loc[
    review["Project_ID"].isna(),
    "Review_Reason",
] = "Missing project"

review_items = review[
    review["Review_Reason"] != ""
].copy()

r1, r2, r3 = st.columns(3)

r1.metric(
    "Transactions Reviewed",
    f"{len(filtered):,}",
)

r2.metric(
    "Potential Exceptions",
    f"{len(review_items):,}",
)

r3.metric(
    "Exception Amount",
    f"${review_items['Total_Amount'].sum():,.2f}",
)

# ---------------------------------------------------------
# Tabs
# ---------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "All Transactions",
        "Exceptions",
        "By Employee",
        "By Category",
    ]
)

with tab1:
    display_columns = [
        "Credit_Card_Transaction_ID",
        "Transaction_Date",
        "Employee_ID",
        "Employee_Name",
        "Department",
        "Project_ID",
        "Merchant",
        "Category",
        "GL_Account_ID",
        "Net_Amount",
        "GST",
        "Total_Amount",
        "Status",
    ]

    st.dataframe(
        filtered[
            [c for c in display_columns if c in filtered.columns]
        ].sort_values(
            "Transaction_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.dataframe(
        review_items.sort_values(
            "Transaction_Date",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    employee_summary = (
        filtered.groupby(
            ["Employee_ID", "Employee_Name"],
            dropna=False,
        )
        .agg(
            Transactions=(
                "Credit_Card_Transaction_ID",
                "count",
            ),
            Net_Amount=("Net_Amount", "sum"),
            GST=("GST", "sum"),
            Total_Amount=("Total_Amount", "sum"),
        )
        .reset_index()
        .sort_values(
            "Total_Amount",
            ascending=False,
        )
    )

    st.dataframe(
        employee_summary,
        use_container_width=True,
        hide_index=True,
    )

with tab4:
    category_summary = (
        filtered.groupby(
            "Category",
            dropna=False,
        )
        .agg(
            Transactions=(
                "Credit_Card_Transaction_ID",
                "count",
            ),
            Net_Amount=("Net_Amount", "sum"),
            GST=("GST", "sum"),
            Total_Amount=("Total_Amount", "sum"),
        )
        .reset_index()
        .sort_values(
            "Total_Amount",
            ascending=False,
        )
    )

    st.dataframe(
        category_summary,
        use_container_width=True,
        hide_index=True,
    )

# ---------------------------------------------------------
# Download
# ---------------------------------------------------------

st.divider()

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Credit Card Reconciliation",
    data=csv,
    file_name="credit_card_reconciliation.csv",
    mime="text/csv",
)
