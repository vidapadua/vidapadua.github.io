import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Peak Accounting System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# NAVIGATION
# =========================================================

pages = {

    # =====================================================
    # 01 OVERVIEW
    # =====================================================

    "01  OVERVIEW": [

        st.Page(
            "pages/0_intro.py",
            title="Intro",
            icon=":material/dashboard:",
        ),

        st.Page(
            "pages/1_dashboard.py",
            title="Dashboard",
            icon=":material/dashboard:",
        ),

    ],


    # =====================================================
    # 02 DATA & LEDGER
    # =====================================================

    "02  DATA & LEDGER": [

        st.Page(
            "pages/2_transactions.py",
            title="Transactions",
            icon=":material/receipt_long:",
        ),

        st.Page(
            "pages/3_chart_of_accounts.py",
            title="Chart of Accounts",
            icon=":material/account_tree:",
        ),

        st.Page(
            "pages/4_general_ledger.py",
            title="General Ledger",
            icon=":material/menu_book:",
        ),

        st.Page(
            "pages/5_journal_entries.py",
            title="Journal Entries",
            icon=":material/edit_note:",
        ),

    ],


    # =====================================================
    # 03 OPERATIONS
    # =====================================================

    "03  OPERATIONS": [

        st.Page(
            "pages/6_accounts_payable.py",
            title="Accounts Payable",
            icon=":material/payments:",
        ),

        st.Page(
            "pages/7_accounts_receivable.py",
            title="Accounts Receivable",
            icon=":material/receipt:",
        ),

        st.Page(
            "pages/8_expenses.py",
            title="Expenses",
            icon=":material/receipt_long:",
        ),

        st.Page(
            "pages/9_banking.py",
            title="Banking",
            icon=":material/account_balance:",
        ),

    ],


    # =====================================================
    # 04 CLOSE & RECONCILIATION
    # =====================================================

    "04  CLOSE & RECONCILIATION": [

        st.Page(
            "pages/10_bank_reconciliation.py",
            title="Bank Reconciliation",
            icon=":material/account_balance:",
        ),

        st.Page(
            "pages/11_credit_card_reconciliation.py",
            title="Credit Card Reconciliation",
            icon=":material/credit_card:",
        ),

        st.Page(
            "pages/12_account_reconciliations.py",
            title="Account Reconciliations",
            icon=":material/balance:",
        ),

        st.Page(
            "pages/13_month_end_close.py",
            title="Month-End Close",
            icon=":material/event_available:",
        ),

    ],


    # =====================================================
    # 05 FINANCIAL REPORTING
    # =====================================================

    "05  FINANCIAL REPORTING": [

        st.Page(
            "pages/14_income_statement.py",
            title="Income Statement",
            icon=":material/monitoring:",
        ),

        st.Page(
            "pages/15_balance_sheet.py",
            title="Balance Sheet",
            icon=":material/account_balance_wallet:",
        ),

        st.Page(
            "pages/16_cash_flow.py",
            title="Cash Flow",
            icon=":material/waterfall_chart:",
        ),

        st.Page(
            "pages/17_management_reporting.py",
            title="Management Reporting",
            icon=":material/analytics:",
        ),

    ],


    # =====================================================
    # 06 ANALYSIS
    # =====================================================

    "06  ANALYSIS": [

        st.Page(
            "pages/18_variance_analysis.py",
            title="Variance Analysis",
            icon=":material/compare_arrows:",
        ),

        st.Page(
            "pages/19_trends.py",
            title="Trends",
            icon=":material/trending_up:",
        ),

        st.Page(
            "pages/20_year_over_year.py",
            title="Year-over-Year",
            icon=":material/show_chart:",
        ),

    ],


    # =====================================================
    # 07 COMPLIANCE & AUDIT
    # =====================================================

    "07  COMPLIANCE & AUDIT": [

        st.Page(
            "pages/21_gst.py",
            title="GST",
            icon=":material/receipt_long:",
        ),

        st.Page(
            "pages/22_audit_support.py",
            title="Audit Support",
            icon=":material/search:",
        ),

        st.Page(
            "pages/23_working_papers.py",
            title="Working Papers",
            icon=":material/description:",
        ),

        st.Page(
            "pages/24_internal_controls.py",
            title="Internal Controls",
            icon=":material/shield:",
        ),

    ],


    # =====================================================
    # 08 DATA & EXCEL
    # =====================================================

    "08  DATA & EXCEL": [

        # st.Page(
        #     "pages/25_data_cleaning.py",
        #     title="Data Cleaning",
        #     icon=":material/cleaning_services:",
        # ),
        #
        # st.Page(
        #     "pages/26_excel_tools.py",
        #     title="Excel Tools",
        #     icon=":material/table_view:",
        # ),
        #
        # st.Page(
        #     "pages/27_validation.py",
        #     title="Validation",
        #     icon=":material/fact_check:",
        # ),

    ],
}


# =========================================================
# RUN APP
# =========================================================

pg = st.navigation(
    pages,
    position="sidebar",
)

pg.run()
