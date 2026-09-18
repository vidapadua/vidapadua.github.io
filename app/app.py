import streamlit as st


st.set_page_config(
    page_title="Finance System",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# NAVIGATION
# =========================================================

pages = {

    # -----------------------------------------------------
    # CORE
    # -----------------------------------------------------
    "": [
        st.Page(
            "pages/transactions.py",
            title="Transactions",
            icon=":material/receipt_long:",
        ),

        st.Page(
            "pages/chart_of_accounts.py",
            title="Chart of Accounts",
            icon=":material/account_tree:",
        ),

        st.Page(
            "pages/general_ledger.py",
            title="General Ledger",
            icon=":material/menu_book:",
        ),

        st.Page(
            "pages/journal_entries.py",
            title="Journal Entries",
            icon=":material/edit_note:",
        ),

        st.Page(
            "pages/accounts_payable.py",
            title="Accounts Payable",
            icon=":material/payments:",
        ),

        st.Page(
            "pages/accounts_receivable.py",
            title="Accounts Receivable",
            icon=":material/receipt:",
        ),

        st.Page(
            "pages/expenses.py",
            title="Expenses",
            icon=":material/receipt_long:",
        ),

        st.Page(
            "pages/banking.py",
            title="Banking",
            icon=":material/account_balance:",
        ),
    ],


    # -----------------------------------------------------
    # 01 RECONCILIATIONS
    # -----------------------------------------------------
    "01  RECONCILIATIONS": [

        st.Page(
            "pages/1_Bank_Reconciliation.py",
            title="Bank Reconciliation",
            icon=":material/account_balance:",
        ),

        st.Page(
            "pages/2_Credit_Card_Reconciliation.py",
            title="Credit Card Reconciliation",
            icon=":material/credit_card:",
        ),

        st.Page(
            "pages/3_Account_Reconciliations.py",
            title="Account Reconciliations",
            icon=":material/balance:",
        ),

        st.Page(
            "pages/4_Month_End_Close.py",
            title="Month-End Close",
            icon=":material/event_available:",
        ),
    ],


    # -----------------------------------------------------
    # 02 FINANCIAL REPORTING
    # -----------------------------------------------------
    "02  FINANCIAL REPORTING": [

        st.Page(
            "pages/5_Income_Statement.py",
            title="Income Statement",
            icon=":material/monitoring:",
        ),

        st.Page(
            "pages/6_Balance_Sheet.py",
            title="Balance Sheet",
            icon=":material/account_balance_wallet:",
        ),

        st.Page(
            "pages/7_Cash_Flow.py",
            title="Cash Flow",
            icon=":material/waterfall_chart:",
        ),

        st.Page(
            "pages/8_Management_Reporting.py",
            title="Management Reporting",
            icon=":material/analytics:",
        ),
    ],


    # -----------------------------------------------------
    # 03 ANALYSIS
    # -----------------------------------------------------
    "03  ANALYSIS": [

        st.Page(
            "pages/9_Variance_Analysis.py",
            title="Variance Analysis",
            icon=":material/compare_arrows:",
        ),

        st.Page(
            "pages/10_Trends.py",
            title="Trends",
            icon=":material/trending_up:",
        ),

        st.Page(
            "pages/11_Year_over_Year.py",
            title="Year-over-Year",
            icon=":material/show_chart:",
        ),
    ],


    # -----------------------------------------------------
    # 04 COMPLIANCE & AUDIT
    # -----------------------------------------------------
    "04  COMPLIANCE & AUDIT": [

        st.Page(
            "pages/12_GST.py",
            title="GST",
            icon=":material/receipt_long:",
        ),

        st.Page(
            "pages/13_Audit_Support.py",
            title="Audit Support",
            icon=":material/search:",
        ),

        st.Page(
            "pages/14_Working_Papers.py",
            title="Working Papers",
            icon=":material/description:",
        ),

        st.Page(
            "pages/15_Internal_Controls.py",
            title="Internal Controls",
            icon=":material/shield:",
        ),
    ],
}


# =========================================================
# RUN NAVIGATION
# =========================================================

pg = st.navigation(pages)

pg.run()
