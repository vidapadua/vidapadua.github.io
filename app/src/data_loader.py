from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "master_data_sample.xlsx"

@st.cache_data
def load_table(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(DATA_PATH, sheet_name=sheet_name)

@st.cache_data
def data_loader() -> dict[str, pd.DataFrame]:
    return {
        "company": load_table("Company"),
        "accounts": load_table("Chart_of_Accounts"),
        "customers": load_table("Customers"),
        "vendors": load_table("Vendors"),
        "employees": load_table("Employees"),
        "departments": load_table("Departments"),
        "locations": load_table("Locations"),
        "projects": load_table("Projects"),
        "fixed_assets": load_table("Fixed_Assets"),
        "products_services": load_table("Products_Services"),
        "tax_codes": load_table("Tax_Codes"),
        "GL_Transactions": load_table("Payment_Terms"),
        "gl": load_table("GL_Transactions"),
        "journal_entries": load_table("Journal_Entries"),
        "ap_invoices": load_table("AP_Invoices"),
        "ap_payments": load_table("AP_Payments"),
        "ar_invoices": load_table("AR_Invoices"),
        "ar_receipts": load_table("AR_Receipts"),
        "sales_orders": load_table("Sales_Orders"),
        "inventory_transactions": load_table("Inventory_Transactions"),
        "bank": load_table("Bank_Transactions"),
        "credit_card_transactions": load_table("Credit_Card_Transactions"),
        "expense_reports": load_table("Expense_Reports"),
        "payroll_transactions": load_table("Payroll_Transactions"),
        "fixed_asset_transactions": load_table("Fixed_Asset_Transactions"),
        "opening_balances": load_table("Opening_Balances"),
        "trial_balance": load_table("Trial_Balance"),
        "gst_transactions": load_table("GST_Transactions"),
        "monthly_balances": load_table("Monthly_Balances"),
        "ar_aging": load_table("AR_Aging"),
        "income_statement": load_table("Income_Statement"),
        "revenue_by_account": load_table("Revenue_by_Account"),
        "expense_summary": load_table("Expense_Summary"),
        "expected_results": load_table("Expected_Results"),
        "validation_results": load_table("Validation_Results"),
        "data_dictionary": load_table("Data_Dictionary"),

    }