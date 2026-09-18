from pathlib import Path
from datetime import date, timedelta
import random
import math
import pandas as pd
import numpy as np
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# Reproducibility
random.seed(42)
np.random.seed(42)

OUT_DIR = Path(__file__).resolve().parent
xlsx_path = OUT_DIR / "master_data_sample.xlsx"

# -----------------------------
# Configuration
# -----------------------------
company_id = "PNE-001"
company_name = "Vida's North Energy Services Ltd. Demo"
gst_rate = 0.05
start_date = pd.Timestamp("2025-01-01")
end_date = pd.Timestamp("2026-12-31")
dates = pd.date_range(start_date, end_date, freq="D")

# -----------------------------
# Master data
# -----------------------------
company = pd.DataFrame([{
    "Company_ID": company_id,
    "Company_Name": "Prairie North Energy Services",
    "Legal_Name": company_name,
    "Province": "Alberta",
    "Country": "Canada",
    "Currency": "CAD",
    "Fiscal_Year_End": "December 31",
    "GST_Registration": "Fictional GST Registrant",
    "GST_Rate": gst_rate,
}])

accounts_data = [
    ("1000","Cash - Operating","Asset","Balance Sheet","1000",True),
    ("1010","Cash - Payroll","Asset","Balance Sheet","1000",True),
    ("1100","Accounts Receivable","Asset","Balance Sheet","1100",True),
    ("1200","Inventory","Asset","Balance Sheet","1200",True),
    ("1300","Prepaid Expenses","Asset","Balance Sheet","1300",True),
    ("1400","Deposits","Asset","Balance Sheet","1400",True),
    ("1500","Fixed Assets - Cost","Asset","Balance Sheet","1500",True),
    ("1590","Accumulated Depreciation","Contra Asset","Balance Sheet","1500",True),
    ("2000","Accounts Payable","Liability","Balance Sheet","2000",True),
    ("2100","Accrued Liabilities","Liability","Balance Sheet","2100",True),
    ("2200","GST Payable","Liability","Balance Sheet","2200",True),
    ("2300","Payroll Liabilities","Liability","Balance Sheet","2300",True),
    ("2400","Equipment Financing","Liability","Balance Sheet","2400",True),
    ("2500","Other Current Liabilities","Liability","Balance Sheet","2500",True),
    ("3000","Share Capital","Equity","Balance Sheet","3000",True),
    ("3100","Retained Earnings","Equity","Balance Sheet","3100",True),
    ("4000","Field Services Revenue","Revenue","Income Statement","4000",True),
    ("4100","Equipment Rental Revenue","Revenue","Income Statement","4100",True),
    ("4200","Parts & Supplies Revenue","Revenue","Income Statement","4200",True),
    ("4300","Other Revenue","Revenue","Income Statement","4300",True),
    ("5000","Parts Cost","Expense","Income Statement","5000",True),
    ("5100","Equipment Rental Direct Costs","Expense","Income Statement","5100",True),
    ("5200","Field Service Direct Costs","Expense","Income Statement","5200",True),
    ("5300","Subcontractor Costs","Expense","Income Statement","5300",True),
    ("6000","Salaries & Wages","Expense","Income Statement","6000",True),
    ("6100","Benefits","Expense","Income Statement","6100",True),
    ("6200","Fuel","Expense","Income Statement","6200",True),
    ("6300","Vehicle Expense","Expense","Income Statement","6300",True),
    ("6400","Repairs & Maintenance","Expense","Income Statement","6400",True),
    ("6500","Insurance","Expense","Income Statement","6500",True),
    ("6600","Rent","Expense","Income Statement","6600",True),
    ("6700","Utilities","Expense","Income Statement","6700",True),
    ("6800","Telephone & Internet","Expense","Income Statement","6800",True),
    ("6900","Software","Expense","Income Statement","6900",True),
    ("7000","Office Supplies","Expense","Income Statement","7000",True),
    ("7100","Professional Fees","Expense","Income Statement","7100",True),
    ("7200","Advertising","Expense","Income Statement","7200",True),
    ("7300","Travel","Expense","Income Statement","7300",True),
    ("7400","Meals","Expense","Income Statement","7400",True),
    ("7500","Bank Fees","Expense","Income Statement","7500",True),
    ("7600","Interest Expense","Expense","Income Statement","7600",True),
    ("7700","Depreciation Expense","Expense","Income Statement","7700",True),
]
accounts = pd.DataFrame(accounts_data, columns=[
    "Account_Number","Account_Name","Account_Type","Financial_Statement",
    "Parent_Account","Active"
])
accounts.insert(0, "Account_ID", ["ACCT-" + n for n in accounts["Account_Number"]])

departments = pd.DataFrame([
    ("DEPT-01","Field Services"),
    ("DEPT-02","Equipment Rental"),
    ("DEPT-03","Parts"),
    ("DEPT-04","Operations"),
    ("DEPT-05","Finance"),
    ("DEPT-06","Administration"),
    ("DEPT-07","Sales"),
    ("DEPT-08","Management"),
], columns=["Department_ID","Department_Name"])

locations = pd.DataFrame([
    ("LOC-01","Calgary Head Office"),
    ("LOC-02","Calgary Yard"),
    ("LOC-03","Equipment Yard"),
    ("LOC-04","Service Shop"),
    ("LOC-05","Field Operations"),
], columns=["Location_ID","Location_Name"])

tax_codes = pd.DataFrame([
    ("GST5","GST 5%",0.05,"GST","Yes","Alberta taxable transactions"),
    ("EXEMPT","GST exempt",0.00,"Exempt","No","Exempt supplies"),
    ("ZERO","GST zero-rated",0.00,"Zero-rated","No","Zero-rated supplies"),
], columns=["Tax_Code","Description","Rate","Tax_Type","Recoverable","Province_Scope"])

payment_terms = pd.DataFrame([
    ("NET15","Net 15 days",15),
    ("NET30","Net 30 days",30),
    ("NET45","Net 45 days",45),
    ("DUE","Due on receipt",0),
], columns=["Payment_Term_ID","Description","Days"])

# Fictional names
customer_prefixes = ["Prairie","Northern","Summit","Frontier","Canyon","Aspen","Iron","Redstone","BlueSky","Western"]
customer_suffixes = ["Drilling Ltd.","Resources Inc.","Energy Corp.","Industrial Services Ltd.","Field Operations Inc.","Pipeline Services Ltd.","Well Services Ltd.","Contracting Corp."]
customer_rows = []
for i in range(1, 101):
    customer_rows.append({
        "Customer_ID": f"CUST-{i:04d}",
        "Customer_Name": f"{random.choice(customer_prefixes)} {random.choice(customer_suffixes)} {i:03d}",
        "Industry": random.choice(["Oil & Gas","Pipeline","Mining","Construction","Utilities","Industrial Manufacturing"]),
        "Province": random.choice(["Alberta","Saskatchewan","British Columbia"]),
        "City": random.choice(["Calgary","Red Deer","Edmonton","Grande Prairie","Fort McMurray","Lloydminster"]),
        "Payment_Terms": random.choice(["NET15","NET30","NET45"]),
        "Credit_Limit": random.choice([25000,50000,75000,100000,150000]),
        "Customer_Status": "Active",
        "Default_Tax_Code": "GST5",
        "Default_Revenue_Account": random.choice(["ACCT-4000","ACCT-4100","ACCT-4200"]),
    })
customers = pd.DataFrame(customer_rows)

vendor_categories = ["Fuel","Utilities","Equipment Maintenance","Parts","Insurance","Software","Office Supplies","Transportation","Subcontractors","Professional Services","Telecommunications","Rent","Safety Equipment","Industrial Supplies"]
vendor_rows = []
for i in range(1, 71):
    vendor_rows.append({
        "Vendor_ID": f"VEND-{i:04d}",
        "Vendor_Name": f"{random.choice(['Alberta','Prairie','Rocky Mountain','Western','Northstar','Clearwater','Foothills'])} {random.choice(['Supply','Services','Industrial','Solutions','Equipment','Partners'])} {i:03d}",
        "Vendor_Category": random.choice(vendor_categories),
        "Province": random.choice(["Alberta","Saskatchewan","British Columbia","Ontario"]),
        "Payment_Terms": random.choice(["NET15","NET30","NET45"]),
        "GST_Applicable": "Yes",
        "Default_GL_Account": random.choice(["ACCT-6200","ACCT-6400","ACCT-7000","ACCT-6800","ACCT-7100"]),
        "Vendor_Status": "Active",
    })
vendors = pd.DataFrame(vendor_rows)

employee_names = [
    "Alex Morgan","Jordan Lee","Taylor Singh","Casey Brown","Morgan Chen","Riley Wilson",
    "Avery Patel","Cameron Smith","Drew Martin","Jamie Wong","Quinn Davis","Reese Thompson",
    "Skyler Johnson","Parker Anderson","Hayden Clark","Emerson White","Rowan Hall","Finley Scott",
    "Dakota Green","Blake Young","Kendall King","Sage Wright","Harper Lewis","Elliot Walker",
    "Logan Adams","Mackenzie Hill","Charlie Baker","Peyton Nelson","Bailey Carter","Reagan Mitchell",
    "Jesse Roberts","Tatum Turner","Marley Phillips","Shawn Campbell","Robin Parker","Devon Evans",
    "Sam Edwards","Chris Collins","Ari Stewart","Nico Sanchez","Milan Kumar","Noah Bennett",
    "Maya Foster","Liam Hughes","Nora Reed","Owen Cook","Eva Bailey","Max Rivera","Lena Cooper",
    "Theo Richardson","Isla Cox","Mia Howard","Ethan Ward","Zoe Torres","Leo Peterson","Ivy Gray",
    "Ben Ramirez","Ella James"
]
employee_rows = []
for i, name in enumerate(employee_names, 1):
    dept = random.choice(departments["Department_ID"].tolist())
    position = random.choice(["Technician","Equipment Operator","Coordinator","Accountant","Sales Representative","Mechanic","Manager","Administrator"])
    salary = random.choice([42000,48000,52000,58000,65000,72000,85000,95000])
    employee_rows.append({
        "Employee_ID": f"EMP-{i:04d}",
        "Employee_Name": name,
        "Department": dept,
        "Position": position,
        "Employment_Type": random.choice(["Full-Time","Full-Time","Full-Time","Part-Time"]),
        "Annual_Salary": salary,
        "Hourly_Rate": round(salary / 2080, 2),
        "Start_Date": (start_date - pd.Timedelta(days=random.randint(30, 1800))).date(),
        "Status": "Active",
    })
employees = pd.DataFrame(employee_rows)

products = pd.DataFrame([
    ("PROD-001","Field labour - standard","Field Services","ACCT-4000","ACCT-5200",145.00,"GST5"),
    ("PROD-002","Field labour - emergency","Field Services","ACCT-4000","ACCT-5200",225.00,"GST5"),
    ("PROD-003","Equipment rental - compressor","Equipment Rental","ACCT-4100","ACCT-5100",850.00,"GST5"),
    ("PROD-004","Equipment rental - generator","Equipment Rental","ACCT-4100","ACCT-5100",625.00,"GST5"),
    ("PROD-005","Equipment rental - pump","Equipment Rental","ACCT-4100","ACCT-5100",475.00,"GST5"),
    ("PROD-006","Industrial replacement parts","Parts","ACCT-4200","ACCT-5000",275.00,"GST5"),
    ("PROD-007","Safety equipment","Parts","ACCT-4200","ACCT-5000",95.00,"GST5"),
    ("PROD-008","Transportation and mobilization","Field Services","ACCT-4000","ACCT-5200",450.00,"GST5"),
    ("PROD-009","Maintenance service","Field Services","ACCT-4000","ACCT-5200",185.00,"GST5"),
    ("PROD-010","Consumables","Parts","ACCT-4200","ACCT-5000",65.00,"GST5"),
], columns=["Product_ID","Description","Category","Revenue_Account","COGS_Account","Standard_Price","Tax_Code"])

# Projects
project_rows = []
for i in range(1, 151):
    customer = random.choice(customers["Customer_ID"].tolist())
    dept = random.choice(["DEPT-01","DEPT-02","DEPT-03"])
    project_rows.append({
        "Project_ID": f"PROJ-{i:05d}",
        "Project_Name": f"Service Project {i:04d}",
        "Customer_ID": customer,
        "Department_ID": dept,
        "Project_Manager": random.choice(employees.loc[employees["Department"].isin(["DEPT-01","DEPT-02","DEPT-04"]),"Employee_ID"].tolist()),
        "Start_Date": (start_date + pd.Timedelta(days=random.randint(0, 650))).date(),
        "End_Date": None,
        "Status": random.choice(["Open","Completed","Open","Open"]),
        "Budget_Revenue": random.randint(10000, 150000),
        "Budget_Cost": random.randint(5000, 100000),
    })
projects = pd.DataFrame(project_rows)

# Fixed assets
asset_classes = [
    ("Truck","Vehicles",7,["DEPT-01","DEPT-04"]),
    ("Trailer","Vehicles",10,["DEPT-02","DEPT-04"]),
    ("Compressor","Heavy Equipment",10,["DEPT-02"]),
    ("Generator","Heavy Equipment",10,["DEPT-02"]),
    ("Pump","Heavy Equipment",10,["DEPT-02"]),
    ("Service Equipment","Shop Equipment",5,["DEPT-01","DEPT-04"]),
    ("Shop Equipment","Shop Equipment",5,["DEPT-04"]),
    ("Computer","IT Equipment",3,["DEPT-05","DEPT-06"]),
    ("Office Equipment","Office Equipment",5,["DEPT-06"]),
]
asset_rows = []
for i in range(1, 81):
    cls, category, life, dept_choices = random.choice(asset_classes)
    purchase_date = start_date + pd.Timedelta(days=random.randint(0, 650))
    cost = random.randint(2500, 180000) if category == "Heavy Equipment" else random.randint(800, 85000)
    asset_rows.append({
        "Asset_ID": f"ASSET-{i:04d}",
        "Asset_Description": f"{cls} {i:03d}",
        "Asset_Class": category,
        "Purchase_Date": purchase_date.date(),
        "Purchase_Cost": float(cost),
        "Useful_Life": life,
        "Depreciation_Method": "Straight-line",
        "Department_ID": random.choice(dept_choices),
        "Location_ID": random.choice(locations["Location_ID"].tolist()),
        "Project_ID": random.choice(projects["Project_ID"].tolist()),
        "Status": "Active",
    })
fixed_assets = pd.DataFrame(asset_rows)

# -----------------------------
# Opening balances
# -----------------------------
opening_rows = [
    ("ACCT-1000", 425000.00, 0.0),
    ("ACCT-1010", 85000.00, 0.0),
    ("ACCT-1100", 625000.00, 0.0),
    ("ACCT-1200", 310000.00, 0.0),
    ("ACCT-1300", 95000.00, 0.0),
    ("ACCT-1400", 25000.00, 0.0),
    ("ACCT-1500", 3250000.00, 0.0),
    ("ACCT-1590", 0.0, 725000.00),
    ("ACCT-2000", 0.0, 485000.00),
    ("ACCT-2100", 0.0, 90000.00),
    ("ACCT-2200", 0.0, 35000.00),
    ("ACCT-2300", 0.0, 65000.00),
    ("ACCT-2400", 0.0, 1100000.00),
    ("ACCT-2500", 0.0, 25000.00),
    ("ACCT-3000", 0.0, 1000000.00),
    ("ACCT-3100", 0.0, 1290000.00)
]
opening_balances = pd.DataFrame(opening_rows, columns=["Account_ID","Opening_Debit","Opening_Credit"])
opening_balances["As_Of_Date"] = pd.Timestamp("2025-01-01").date()

# -----------------------------
# Generate coherent AR and AP
# -----------------------------
def seasonality(month):
    return {1:0.75,2:0.78,3:0.90,4:1.00,5:1.08,6:1.18,7:1.20,8:1.16,9:1.08,10:1.00,11:0.92,12:0.82}[month]

ar_rows, ar_receipt_rows = [], []
ap_rows, ap_payment_rows = [], []
sales_order_rows, purchase_order_rows = [], []
gl_rows = []
je_rows = []

def money(x):
    return round(float(x), 2)

def add_je(je_id, posting_date, doc_type, source_id, description, lines, department_id=None, project_id=None):
    # lines: list of (account_id, debit, credit, tax_code, tax_amount, customer_id, vendor_id, employee_id)
    total_debit = money(sum(x[1] for x in lines))
    total_credit = money(sum(x[2] for x in lines))
    assert abs(total_debit-total_credit) < 0.01, (je_id, total_debit, total_credit)
    batch_id = f"BATCH-{posting_date.year}-{posting_date.month:02d}"
    for line_no, (acct, debit, credit, tax_code, tax_amount, cust, vend, emp) in enumerate(lines, 1):
        account_name = accounts.loc[accounts["Account_ID"] == acct, "Account_Name"].iloc[0]
        gl_rows.append({
            "Company_Code": company_id,
            "Fiscal_Year": posting_date.year,
            "Fiscal_Period": posting_date.month,
            "Posting_Date": posting_date.date(),
            "Document_Date": posting_date.date(),
            "Document_ID": source_id,
            "Document_Type": doc_type,
            "Transaction_ID": f"GL-{len(gl_rows)+1:08d}",
            "Line_ID": line_no,
            "Batch_ID": batch_id,
            "Account_ID": acct,
            "Account_Name": account_name,
            "Debit": money(debit),
            "Credit": money(credit),
            "Currency": "CAD",
            "Exchange_Rate": 1.0,
            "Department_ID": department_id,
            "Location_ID": random.choice(locations["Location_ID"].tolist()),
            "Project_ID": project_id,
            "Customer_ID": cust,
            "Vendor_ID": vend,
            "Employee_ID": emp,
            "Tax_Code": tax_code,
            "Tax_Amount": money(tax_amount),
            "Description": description,
            "Reference": source_id,
            "Created_By": "SYSTEM",
            "Created_Date": posting_date.date(),
            "Approved_By": "FIN-MGR",
            "Approval_Date": posting_date.date(),
            "Status": "Posted",
        })
    je_rows.append({
        "Journal_Entry_ID": je_id,
        "Posting_Date": posting_date.date(),
        "Document_Type": doc_type,
        "Source_ID": source_id,
        "Batch_ID": batch_id,
        "Description": description,
        "Total_Debit": total_debit,
        "Total_Credit": total_credit,
        "Status": "Posted",
    })

# Opening balance JE
opening_lines = []
for _, r in opening_balances.iterrows():
    opening_lines.append((r["Account_ID"], r["Opening_Debit"], r["Opening_Credit"], None, 0, None, None, None))
add_je("JE-OPEN-2025", pd.Timestamp("2025-01-01"), "Opening Balance", "OPEN-2025", "Opening balances", opening_lines)

# AR invoices: 2,400
ar_invoice_count = 0
for year in [2025, 2026]:
    for month in range(1,13):
        n = int(round(100 * seasonality(month)))  # 900? total 2400
        if year == 2026:
            n = int(round(n * 1.08))
        for j in range(n):
            ar_invoice_count += 1
            inv_date = pd.Timestamp(year=year, month=month, day=random.randint(1, 28))
            customer = customers.sample(1).iloc[0]
            product = products.sample(1).iloc[0]
            qty = random.randint(1, 12)
            unit_price = float(product["Standard_Price"]) * random.uniform(0.85, 1.20)
            net = money(qty * unit_price)
            tax = money(net * gst_rate)
            gross = money(net + tax)
            due_date = inv_date + pd.Timedelta(days=int(payment_terms.loc[payment_terms["Payment_Term_ID"] == customer["Payment_Terms"], "Days"].iloc[0]))
            inv_id = f"AR-{year}-{ar_invoice_count:05d}"
            so_id = f"SO-{year}-{ar_invoice_count:05d}"
            customer_projects = projects[
                projects["Customer_ID"] == customer["Customer_ID"]
                ]

            if len(customer_projects) > 0:
                project = customer_projects.sample(1).iloc[0]
            else:
                project = projects.sample(1).iloc[0]

            sales_order_rows.append({
                "Sales_Order_ID": so_id, "Customer_ID": customer["Customer_ID"], "Project_ID": project["Project_ID"],
                "Product_ID": product["Product_ID"], "Order_Date": inv_date.date(), "Quantity": qty,
                "Unit_Price": money(unit_price), "Net_Amount": net, "GST": tax, "Total": gross, "Status": "Invoiced"
            })
            ar_rows.append({
                "AR_Invoice_ID": inv_id, "Sales_Order_ID": so_id, "Customer_ID": customer["Customer_ID"],
                "Customer_Name": customer["Customer_Name"], "Project_ID": project["Project_ID"],
                "Invoice_Date": inv_date.date(), "Due_Date": due_date.date(), "Revenue_Account": product["Revenue_Account"],
                "Net_Amount": net, "GST": tax, "Gross_Amount": gross, "Paid_Amount": 0.0,
                "Outstanding_Balance": gross, "Status": "Outstanding", "Tax_Code": "GST5"
            })
            add_je(f"JE-{year}-AR-{ar_invoice_count:05d}", inv_date, "AR Invoice", inv_id,
                   f"AR invoice {inv_id}", [
                       ("ACCT-1100", gross, 0, "GST5", tax, customer["Customer_ID"], None, None),
                       (product["Revenue_Account"], 0, net, "GST5", 0, customer["Customer_ID"], None, None),
                       ("ACCT-2200", 0, tax, "GST5", tax, customer["Customer_ID"], None, None),
                   ], department_id=project["Department_ID"], project_id=project["Project_ID"])

# AR receipts: pay invoices with probability, including partials
for idx, inv in ar_rows if False else enumerate(ar_rows):
    pass
# convert and create receipts
for i, inv in enumerate(ar_rows):
    invoice_date = pd.Timestamp(inv["Invoice_Date"])
    age_days = (end_date - invoice_date).days
    pay_prob = 0.88 if age_days > 60 else 0.58
    if random.random() < pay_prob:
        paid = inv["Gross_Amount"] if random.random() < 0.87 else money(inv["Gross_Amount"] * random.uniform(0.25, 0.85))
        receipt_date = min(invoice_date + pd.Timedelta(days=random.randint(5, 75)), end_date)
        receipt_id = f"ARR-{receipt_date.year}-{i+1:05d}"
        ar_receipt_rows.append({
            "AR_Receipt_ID": receipt_id, "AR_Invoice_ID": inv["AR_Invoice_ID"], "Customer_ID": inv["Customer_ID"],
            "Receipt_Date": receipt_date.date(), "Amount": paid, "Bank_Account_ID": "ACCT-1000",
            "Reference": f"Receipt for {inv['AR_Invoice_ID']}"
        })
        inv["Paid_Amount"] = money(paid)
        inv["Outstanding_Balance"] = money(inv["Gross_Amount"] - paid)
        inv["Status"] = "Paid" if inv["Outstanding_Balance"] < 0.01 else "Partially Paid"
        add_je(f"JE-{receipt_date.year}-ARR-{i+1:05d}", receipt_date, "AR Receipt", receipt_id,
               f"Customer receipt for {inv['AR_Invoice_ID']}", [
                   ("ACCT-1000", paid, 0, None, 0, inv["Customer_ID"], None, None),
                   ("ACCT-1100", 0, paid, None, 0, inv["Customer_ID"], None, None),
               ])

# AP invoices: 1,800
ap_invoice_count = 0
for year in [2025, 2026]:
    for month in range(1,13):
        n = int(round(72 * seasonality(month)))
        if year == 2026:
            n = int(round(n * 1.06))
        for j in range(n):
            ap_invoice_count += 1
            inv_date = pd.Timestamp(year=year, month=month, day=random.randint(1, 28))
            vendor = vendors.sample(1).iloc[0]
            project = projects.sample(1).iloc[0]
            net = money(random.uniform(300, 12000))
            tax = money(net * gst_rate)
            gross = money(net + tax)
            due_days = int(payment_terms.loc[payment_terms["Payment_Term_ID"] == vendor["Payment_Terms"], "Days"].iloc[0])
            due_date = inv_date + pd.Timedelta(days=due_days)
            inv_id = f"AP-{year}-{ap_invoice_count:05d}"
            po_id = f"PO-{year}-{ap_invoice_count:05d}"
            expense_account = vendor["Default_GL_Account"]
            purchase_order_rows.append({
                "Purchase_Order_ID": po_id, "Vendor_ID": vendor["Vendor_ID"], "Product_Service_ID": f"SVC-{random.randint(1,30):03d}",
                "Project_ID": project["Project_ID"], "Department_ID": project["Department_ID"], "Order_Date": inv_date.date(),
                "Quantity": 1, "Unit_Cost": net, "Net_Amount": net, "GST": tax, "Total": gross, "Status": "Invoiced"
            })
            ap_rows.append({
                "AP_Invoice_ID": inv_id, "Purchase_Order_ID": po_id, "Vendor_ID": vendor["Vendor_ID"],
                "Vendor_Name": vendor["Vendor_Name"], "Project_ID": project["Project_ID"], "Department_ID": project["Department_ID"],
                "Invoice_Date": inv_date.date(), "Due_Date": due_date.date(), "Expense_Account": expense_account,
                "Net_Amount": net, "GST": tax, "Gross_Amount": gross, "Paid_Amount": 0.0,
                "Outstanding_Balance": gross, "Status": "Outstanding", "Tax_Code": "GST5"
            })
            add_je(f"JE-{year}-AP-{ap_invoice_count:05d}", inv_date, "AP Invoice", inv_id,
                   f"AP invoice {inv_id}", [
                       (expense_account, net, 0, "GST5", 0, None, vendor["Vendor_ID"], None),
                       ("ACCT-2200", tax, 0, "GST5", tax, None, vendor["Vendor_ID"], None),
                       ("ACCT-2000", 0, gross, "GST5", tax, None, vendor["Vendor_ID"], None),
                   ], department_id=project["Department_ID"], project_id=project["Project_ID"])

for i, inv in enumerate(ap_rows):
    invoice_date = pd.Timestamp(inv["Invoice_Date"])
    age_days = (end_date - invoice_date).days
    pay_prob = 0.90 if age_days > 60 else 0.60
    if random.random() < pay_prob:
        paid = inv["Gross_Amount"] if random.random() < 0.90 else money(inv["Gross_Amount"] * random.uniform(0.30, 0.85))
        payment_date = min(invoice_date + pd.Timedelta(days=random.randint(5, 70)), end_date)
        payment_id = f"APP-{payment_date.year}-{i+1:05d}"
        ap_payment_rows.append({
            "AP_Payment_ID": payment_id, "AP_Invoice_ID": inv["AP_Invoice_ID"], "Vendor_ID": inv["Vendor_ID"],
            "Payment_Date": payment_date.date(), "Amount": paid, "Bank_Account_ID": "ACCT-1000",
            "Reference": f"Payment for {inv['AP_Invoice_ID']}"
        })
        inv["Paid_Amount"] = money(paid)
        inv["Outstanding_Balance"] = money(inv["Gross_Amount"] - paid)
        inv["Status"] = "Paid" if inv["Outstanding_Balance"] < 0.01 else "Partially Paid"
        add_je(f"JE-{payment_date.year}-APP-{i+1:05d}", payment_date, "AP Payment", payment_id,
               f"Vendor payment for {inv['AP_Invoice_ID']}", [
                   ("ACCT-2000", paid, 0, None, 0, None, inv["Vendor_ID"], None),
                   ("ACCT-1000", 0, paid, None, 0, None, inv["Vendor_ID"], None),
               ])

# Other recurring operating expenses, payroll, depreciation, bank fees and interest
monthly_support_rows = []
for dt in pd.date_range(start_date, end_date, freq="MS"):
    # Payroll
    payroll_gross = money(employees["Annual_Salary"].sum() / 24)
    benefits = money(payroll_gross * 0.105)
    payroll_id = f"PAY-{dt.year}-{dt.month:02d}"
    add_je(f"JE-{dt.year}-PAY-{dt.month:02d}", dt, "Payroll", payroll_id, "Monthly payroll", [
        ("ACCT-6000", payroll_gross, 0, None, 0, None, None, None),
        ("ACCT-6100", benefits, 0, None, 0, None, None, None),
        ("ACCT-2300", 0, money(payroll_gross * 0.18 + benefits), None, 0, None, None, None),
        ("ACCT-1000", 0, money(payroll_gross * 0.82), None, 0, None, None, None),
    ])
    # Recurring expenses
    recurring = [
        ("ACCT-6600", money(24000 * (1 if dt.month not in [1,2] else 0.95)), "Rent"),
        ("ACCT-6700", money(random.uniform(4500, 8500)), "Utilities"),
        ("ACCT-6800", money(random.uniform(1800, 3000)), "Telephone and internet"),
        ("ACCT-6900", money(random.uniform(2500, 4500)), "Software"),
        ("ACCT-6500", money(random.uniform(6000, 9000)), "Insurance"),
        ("ACCT-7500", money(random.uniform(350, 800)), "Bank fees"),
        ("ACCT-7600", money(random.uniform(5000, 9000)), "Interest"),
    ]
    for acct, amount, desc in recurring:
        source = f"EXP-{dt.year}-{dt.month:02d}-{acct[-4:]}"
        add_je(f"JE-{dt.year}-{dt.month:02d}-{acct[-4:]}", dt, "Operating Expense", source, desc, [
            (acct, amount, 0, None, 0, None, None, None),
            ("ACCT-1000", 0, amount, None, 0, None, None, None),
        ])
    # Depreciation based on assets in service
    dep = 0
    for _, asset in fixed_assets.iterrows():
        if pd.Timestamp(asset["Purchase_Date"]) <= dt:
            dep += asset["Purchase_Cost"] / (asset["Useful_Life"] * 12)
    dep = money(dep)
    add_je(f"JE-{dt.year}-DEP-{dt.month:02d}", dt, "Depreciation", f"DEP-{dt.year}-{dt.month:02d}", "Monthly depreciation", [
        ("ACCT-7700", dep, 0, None, 0, None, None, None),
        ("ACCT-1590", 0, dep, None, 0, None, None, None),
    ])
    monthly_support_rows.append({
        "Month": dt.date(),
        "Payroll_Gross": payroll_gross,
        "Benefits": benefits,
        "Depreciation": dep,
    })

# Fixed asset transactions
fixed_asset_transactions = []
for _, asset in fixed_assets.iterrows():
    purchase_date = pd.Timestamp(asset["Purchase_Date"])
    fixed_asset_transactions.append({
        "Fixed_Asset_Transaction_ID": f"FAT-{asset['Asset_ID']}",
        "Asset_ID": asset["Asset_ID"],
        "Transaction_Date": purchase_date.date(),
        "Transaction_Type": "Acquisition",
        "Amount": asset["Purchase_Cost"],
        "Debit_Account": "ACCT-1500",
        "Credit_Account": "ACCT-1000",
        "Reference": asset["Asset_ID"],
    })
    add_je(f"JE-{purchase_date.year}-FA-{asset['Asset_ID']}", purchase_date, "Fixed Asset Acquisition", asset["Asset_ID"],
           f"Acquisition of {asset['Asset_Description']}", [
               ("ACCT-1500", asset["Purchase_Cost"], 0, None, 0, None, None, None),
               ("ACCT-1000", 0, asset["Purchase_Cost"], None, 0, None, None, None),
           ], department_id=asset["Department_ID"], project_id=asset["Project_ID"])

# Bank transactions derived from cash-affecting GL lines
gl = pd.DataFrame(gl_rows)
journal_entries = pd.DataFrame(je_rows)
ap_invoices = pd.DataFrame(ap_rows)
ap_payments = pd.DataFrame(ap_payment_rows)
ar_invoices = pd.DataFrame(ar_rows)
ar_receipts = pd.DataFrame(ar_receipt_rows)
sales_orders = pd.DataFrame(sales_order_rows)
purchase_orders = pd.DataFrame(purchase_order_rows)
monthly_support = pd.DataFrame(monthly_support_rows)
fixed_asset_transactions = pd.DataFrame(fixed_asset_transactions)

# Bank statement mirrors cash-account GL movements, with a separate running balance
cash_gl = gl[gl["Account_ID"].isin(["ACCT-1000","ACCT-1010"])].copy()
cash_gl["Net_Change"] = cash_gl["Debit"] - cash_gl["Credit"]
cash_gl = cash_gl.sort_values(["Posting_Date","Transaction_ID"])
bank_transactions = cash_gl[["Posting_Date","Document_ID","Document_Type","Description","Debit","Credit","Net_Change"]].copy()
bank_transactions.insert(0, "Bank_Transaction_ID", [f"BANK-{i+1:08d}" for i in range(len(bank_transactions))])
bank_transactions["Bank_Account_ID"] = "ACCT-1000"
bank_transactions["Value_Date"] = bank_transactions["Posting_Date"]
bank_transactions["Reference"] = bank_transactions["Document_ID"]
opening_cash = 510000.00
bank_transactions["Running_Balance"] = opening_cash + bank_transactions["Net_Change"].cumsum()
bank_transactions = bank_transactions.drop(columns=["Net_Change"])

# Credit card transactions and expense reports
cc_rows, expense_rows = [], []
for i in range(1, 4501):
    dt = random.choice(dates)
    employee = employees.sample(1).iloc[0]
    category, acct = random.choice([
        ("Fuel","ACCT-6200"),("Travel","ACCT-7300"),("Meals","ACCT-7400"),
        ("Office Supplies","ACCT-7000"),("Software","ACCT-6900"),
        ("Hardware","ACCT-7000"),("Vehicle Expense","ACCT-6300"),
        ("Maintenance","ACCT-6400"),("Hotel","ACCT-7300"),("Transportation","ACCT-7300")
    ])
    net = money(random.uniform(25, 1250))
    tax = money(net * gst_rate)
    cc_rows.append({
        "Credit_Card_Transaction_ID": f"CC-{i:07d}",
        "Transaction_Date": dt.date(),
        "Employee_ID": employee["Employee_ID"],
        "Department_ID": employee["Department"],
        "Project_ID": random.choice(projects["Project_ID"].tolist()),
        "Merchant": f"Merchant {random.randint(1,250):03d}",
        "Category": category,
        "GL_Account_ID": acct,
        "Net_Amount": net,
        "GST": tax,
        "Total_Amount": money(net+tax),
        "Status": "Posted",
    })
for i in range(1, 1801):
    dt = random.choice(dates)
    employee = employees.sample(1).iloc[0]
    category = random.choice(["Fuel","Travel","Meals","Office Supplies","Maintenance","Transportation"])
    net = money(random.uniform(20, 900))
    tax = money(net * gst_rate)
    expense_rows.append({
        "Expense_Report_ID": f"EXP-RPT-{i:06d}",
        "Employee_ID": employee["Employee_ID"],
        "Date": dt.date(),
        "Merchant": f"Merchant {random.randint(1,250):03d}",
        "Expense_Category": category,
        "Project_ID": random.choice(projects["Project_ID"].tolist()),
        "Amount": net,
        "GST": tax,
        "Total_Amount": money(net+tax),
        "Receipt_Status": "Attached",
        "Approval_Status": "Approved",
        "Reimbursement_Status": random.choice(["Paid","Paid","Pending"]),
    })
credit_card_transactions = pd.DataFrame(cc_rows)
expense_reports = pd.DataFrame(expense_rows)

# Inventory transactions
inventory_rows = []
inventory_products = products[products["Category"] == "Parts"]
for i in range(1, 3501):
    dt = random.choice(dates)
    product = inventory_products.sample(1).iloc[0]
    tx_type = random.choice(["Purchase","Purchase","Sale","Sale","Transfer","Adjustment","Return"])
    qty = random.randint(1, 40)
    unit_cost = money(product["Standard_Price"] * random.uniform(0.35, 0.65))
    if tx_type == "Sale":
        qty = -qty
    elif tx_type == "Return":
        qty = qty
    total = money(abs(qty) * unit_cost)
    inventory_rows.append({
        "Inventory_Transaction_ID": f"INV-TX-{i:07d}",
        "SKU": product["Product_ID"],
        "Product": product["Description"],
        "Warehouse": random.choice(["Calgary Yard","Service Shop","Equipment Yard"]),
        "Transaction_Type": tx_type,
        "Quantity": qty,
        "Unit_Cost": unit_cost,
        "Total_Cost": total,
        "Purchase_Order_ID": random.choice(purchase_orders["Purchase_Order_ID"].tolist()) if tx_type in ["Purchase","Return"] else None,
        "Sales_Order_ID": random.choice(sales_orders["Sales_Order_ID"].tolist()) if tx_type == "Sale" else None,
        "Date": dt.date(),
    })
inventory_transactions = pd.DataFrame(inventory_rows)

# GST transactions derived from AP/AR
gst_transactions = pd.concat([
    ar_invoices[["AR_Invoice_ID","Invoice_Date","GST"]].rename(columns={"AR_Invoice_ID":"Source_ID","Invoice_Date":"Date"}).assign(Transaction_Type="GST Collected", Direction="Collected"),
    ap_invoices[["AP_Invoice_ID","Invoice_Date","GST"]].rename(columns={"AP_Invoice_ID":"Source_ID","Invoice_Date":"Date"}).assign(Transaction_Type="Recoverable GST / ITC", Direction="Recoverable")
], ignore_index=True)
gst_transactions["Tax_Code"] = "GST5"
gst_transactions["Rate"] = gst_rate
gst_transactions = gst_transactions.rename(columns={"GST":"GST_Amount"})

# Payroll detail
payroll_rows = []
for dt in pd.date_range(start_date, end_date, freq="MS"):
    for _, emp in employees.iterrows():
        gross = money(emp["Annual_Salary"]/24)
        employer_benefits = money(gross*0.105)
        payroll_rows.append({
            "Payroll_Transaction_ID": f"PAY-TX-{dt.year}{dt.month:02d}-{emp['Employee_ID']}",
            "Payroll_Period": dt.date(),
            "Employee_ID": emp["Employee_ID"],
            "Department_ID": emp["Department"],
            "Gross_Wages": gross,
            "Employer_Benefits": employer_benefits,
            "Employee_Withholdings": money(gross*0.18),
            "Net_Pay": money(gross*0.82),
            "Payroll_Liability": money(gross*0.18 + employer_benefits),
            "Payment_Status": "Paid",
        })
payroll_transactions = pd.DataFrame(payroll_rows)

# -----------------------------
# Expected results and validation
# -----------------------------
# Trial balance from opening + GL excluding opening JE
gl_nonopening = gl[gl["Document_ID"] != "OPEN-2025"].copy()
tb = gl.groupby(["Account_ID","Account_Name"], as_index=False).agg(
    Period_Debit=("Debit","sum"), Period_Credit=("Credit","sum")
)
tb = tb.merge(opening_balances[["Account_ID","Opening_Debit","Opening_Credit"]], on="Account_ID", how="left")
tb[["Opening_Debit","Opening_Credit"]] = tb[["Opening_Debit","Opening_Credit"]].fillna(0)
tb["Closing_Debit"] = tb["Opening_Debit"] + tb["Period_Debit"]
tb["Closing_Credit"] = tb["Opening_Credit"] + tb["Period_Credit"]
trial_balance = tb[["Account_ID","Account_Name","Opening_Debit","Opening_Credit","Period_Debit","Period_Credit","Closing_Debit","Closing_Credit"]]

# Monthly balances
gl["Month"] = pd.to_datetime(gl["Posting_Date"]).dt.to_period("M").astype(str)
monthly = []
for month, g in gl.groupby("Month"):
    revenue = g[g["Account_ID"].str.startswith(("ACCT-4",))]["Credit"].sum() - g[g["Account_ID"].str.startswith(("ACCT-4",))]["Debit"].sum()
    cogs = g[g["Account_ID"].isin(["ACCT-5000","ACCT-5100","ACCT-5200","ACCT-5300"])]["Debit"].sum() - g[g["Account_ID"].isin(["ACCT-5000","ACCT-5100","ACCT-5200","ACCT-5300"])]["Credit"].sum()
    opex_accounts = [a for a in accounts["Account_ID"] if a in ["ACCT-"+str(x) for x in range(6000,7800,100)]]
    opex = g[g["Account_ID"].isin(opex_accounts)]["Debit"].sum() - g[g["Account_ID"].isin(opex_accounts)]["Credit"].sum()
    cash = opening_cash + g[g["Account_ID"]=="ACCT-1000"]["Debit"].sum() - g[g["Account_ID"]=="ACCT-1000"]["Credit"].sum()
    ar_balance = g[g["Account_ID"]=="ACCT-1100"]["Debit"].sum() - g[g["Account_ID"]=="ACCT-1100"]["Credit"].sum()
    ap_balance = g[g["Account_ID"]=="ACCT-2000"]["Credit"].sum() - g[g["Account_ID"]=="ACCT-2000"]["Debit"].sum()
    monthly.append({
        "Month": month,
        "Revenue": money(revenue),
        "COGS": money(cogs),
        "Gross_Profit": money(revenue-cogs),
        "Operating_Expenses": money(opex),
        "Net_Income": money(revenue-cogs-opex),
        "Cash": money(cash),
        "AR_Net_Movement": money(ar_balance),
        "AP_Net_Movement": money(ap_balance),
    })
monthly_balances = pd.DataFrame(monthly)

# Income statement and balance sheet
revenue_by_account = gl[gl["Account_ID"].str.startswith("ACCT-4")].groupby(["Account_ID","Account_Name"], as_index=False).agg(
    Amount=("Credit","sum")
)
expense_accounts = accounts[accounts["Account_Type"]=="Expense"]["Account_ID"].tolist()
expense_summary = gl[gl["Account_ID"].isin(expense_accounts)].groupby(["Account_ID","Account_Name"], as_index=False).agg(
    Amount=("Debit","sum")
)
income_statement = pd.DataFrame([{
    "Metric": "Total Revenue",
    "Amount": money(revenue_by_account["Amount"].sum())
},{
    "Metric": "Total Expenses",
    "Amount": money(expense_summary["Amount"].sum())
},{
    "Metric": "Net Income",
    "Amount": money(revenue_by_account["Amount"].sum() - expense_summary["Amount"].sum())
}])

# AR/AP aging as of end date
as_of = end_date
def aging_bucket(due_date, outstanding):
    if outstanding <= 0.005:
        return "Paid"
    days = (as_of - pd.Timestamp(due_date)).days
    if days <= 0: return "Current"
    if days <= 30: return "1-30 days"
    if days <= 60: return "31-60 days"
    if days <= 90: return "61-90 days"
    return "90+ days"

ar_invoices["Aging_Bucket"] = [aging_bucket(d, o) for d,o in zip(ar_invoices["Due_Date"], ar_invoices["Outstanding_Balance"])]
ap_invoices["Aging_Bucket"] = [aging_bucket(d, o) for d,o in zip(ap_invoices["Due_Date"], ap_invoices["Outstanding_Balance"])]
ar_aging = ar_invoices.groupby("Aging_Bucket", as_index=False).agg(
    Invoice_Count=("AR_Invoice_ID","count"), Outstanding_Balance=("Outstanding_Balance","sum")
)
ap_aging = ap_invoices.groupby("Aging_Bucket", as_index=False).agg(
    Invoice_Count=("AP_Invoice_ID","count"), Outstanding_Balance=("Outstanding_Balance","sum")
)

# Expected results
expected_results = pd.DataFrame([
    {"Metric":"Annual Revenue - 2025","Value": money(gl[(gl["Fiscal_Year"]==2025) & (gl["Account_ID"].str.startswith("ACCT-4"))]["Credit"].sum())},
    {"Metric":"Annual Revenue - 2026","Value": money(gl[(gl["Fiscal_Year"]==2026) & (gl["Account_ID"].str.startswith("ACCT-4"))]["Credit"].sum())},
    {"Metric":"Total Revenue - 2 Years","Value": money(revenue_by_account["Amount"].sum())},
    {"Metric":"Total Expenses - 2 Years","Value": money(expense_summary["Amount"].sum())},
    {"Metric":"Net Income - 2 Years","Value": money(income_statement.loc[income_statement["Metric"]=="Net Income","Amount"].iloc[0])},
    {"Metric":"Ending Cash - Operating","Value": money(bank_transactions["Running_Balance"].iloc[-1])},
    {"Metric":"Outstanding AR","Value": money(ar_invoices["Outstanding_Balance"].sum())},
    {"Metric":"Outstanding AP","Value": money(ap_invoices["Outstanding_Balance"].sum())},
    {"Metric":"GST Collected","Value": money(ar_invoices["GST"].sum())},
    {"Metric":"Recoverable GST / ITCs","Value": money(ap_invoices["GST"].sum())},
    {"Metric":"Net GST Position","Value": money(ar_invoices["GST"].sum()-ap_invoices["GST"].sum())},
    {"Metric":"Fixed Asset Cost","Value": money(fixed_assets["Purchase_Cost"].sum())},
])

# Data dictionary
data_dictionary_rows = []
sheet_columns = {
    "Company": company.columns,
    "Chart_of_Accounts": accounts.columns,
    "Customers": customers.columns,
    "Vendors": vendors.columns,
    "Employees": employees.columns,
    "Departments": departments.columns,
    "Locations": locations.columns,
    "Projects": projects.columns,
    "Fixed_Assets": fixed_assets.columns,
    "Products_Services": products.columns,
    "Tax_Codes": tax_codes.columns,
    "Payment_Terms": payment_terms.columns,
    "GL_Transactions": gl.drop(columns=["Month"]).columns,
    "Journal_Entries": journal_entries.columns,
    "AP_Invoices": ap_invoices.columns,
    "AP_Payments": ap_payments.columns,
    "AR_Invoices": ar_invoices.columns,
    "AR_Receipts": ar_receipts.columns,
    "Purchase_Orders": purchase_orders.columns,
    "Sales_Orders": sales_orders.columns,
    "Inventory_Transactions": inventory_transactions.columns,
    "Bank_Transactions": bank_transactions.columns,
    "Credit_Card_Transactions": credit_card_transactions.columns,
    "Expense_Reports": expense_reports.columns,
    "Payroll_Transactions": payroll_transactions.columns,
    "Fixed_Asset_Transactions": fixed_asset_transactions.columns,
    "Opening_Balances": opening_balances.columns,
    "Trial_Balance": trial_balance.columns,
    "GST_Transactions": gst_transactions.columns,
    "Monthly_Balances": monthly_balances.columns,
    "Expected_Results": expected_results.columns,
}
for sheet, cols in sheet_columns.items():
    for col in cols:
        data_dictionary_rows.append({
            "Table": sheet,
            "Field": col,
            "Description": col.replace("_"," "),
            "Data_Type": "Date" if "Date" in col or col in ["Month"] else "Numeric" if any(k in col for k in ["Amount","Debit","Credit","Rate","Cost","Price","Balance","Quantity","Salary","Income","Revenue","Expense","GST","Tax","Total"]) else "Text",
            "Required": "Yes",
            "Example": "",
            "Primary_Key": "Yes" if col.endswith("_ID") and col in ["Company_ID","Account_ID","Customer_ID","Vendor_ID","Employee_ID","Department_ID","Location_ID","Project_ID","Asset_ID","Product_ID","Tax_Code","Payment_Term_ID"] else "No",
            "Foreign_Key": "Yes" if col.endswith("_ID") and col not in ["Company_ID","Account_ID","Customer_ID","Vendor_ID","Employee_ID","Department_ID","Location_ID","Project_ID","Asset_ID","Product_ID","Tax_Code","Payment_Term_ID"] else "No",
            "Related_Table": "",
        })
data_dictionary = pd.DataFrame(data_dictionary_rows)

readme = pd.DataFrame({
    "Section": [
        "Purpose","Company","Period","Currency","GST","Golden Master Principle",
        "Accounting Integrity","Dirty Data Layer","Generated Scope"
    ],
    "Description": [
        "Clean fictional ERP-style accounting dataset for a Streamlit portfolio application.",
        company_name + ", Calgary, Alberta, Canada; oilfield services, equipment rental, and industrial parts.",
        "January 1, 2025 through December 31, 2026.",
        "CAD",
        "5% GST for normal Alberta taxable transactions.",
        "This workbook is intended to be the clean source of truth. Data corruption should be applied only to copies.",
        "Journal entries are generated with equal total debits and credits. AP/AR invoice balances are linked to payments/receipts. Trial balance and reporting outputs are derived from the GL.",
        "Create a separate generator that copies selected tables and introduces controlled, documented data-quality issues.",
        f"Customers: {len(customers):,}; Vendors: {len(vendors):,}; Employees: {len(employees):,}; Projects: {len(projects):,}; Fixed assets: {len(fixed_assets):,}; GL lines: {len(gl):,}; AP invoices: {len(ap_invoices):,}; AR invoices: {len(ar_invoices):,}."
    ]
})

# -----------------------------
# Validation checks
# -----------------------------
checks = []

def check(name, passed, detail):
    checks.append({"Check": name, "Passed": bool(passed), "Detail": detail})

check("Journal entries balance",
      np.isclose(journal_entries["Total_Debit"].sum(), journal_entries["Total_Credit"].sum()),
      f"Debits={journal_entries['Total_Debit'].sum():,.2f}; Credits={journal_entries['Total_Credit'].sum():,.2f}")

check("GL debits equal credits",
      np.isclose(gl["Debit"].sum(), gl["Credit"].sum()),
      f"Debits={gl['Debit'].sum():,.2f}; Credits={gl['Credit'].sum():,.2f}")

check("AR invoice arithmetic",
      np.allclose(ar_invoices["Net_Amount"] + ar_invoices["GST"], ar_invoices["Gross_Amount"]),
      "Net + GST = Gross for all AR invoices")

check("AP invoice arithmetic",
      np.allclose(ap_invoices["Net_Amount"] + ap_invoices["GST"], ap_invoices["Gross_Amount"]),
      "Net + GST = Gross for all AP invoices")

check("AR outstanding arithmetic",
      np.allclose(ar_invoices["Gross_Amount"] - ar_invoices["Paid_Amount"], ar_invoices["Outstanding_Balance"]),
      "Gross - paid = outstanding for all AR invoices")

check("AP outstanding arithmetic",
      np.allclose(ap_invoices["Gross_Amount"] - ap_invoices["Paid_Amount"], ap_invoices["Outstanding_Balance"]),
      "Gross - paid = outstanding for all AP invoices")

check("Bank running balance",
      np.isclose(bank_transactions["Running_Balance"].iloc[-1],
                 opening_cash + cash_gl["Net_Change"].sum()),
      "Opening cash + cash movements = ending bank balance")

check("Trial balance balances",
      np.isclose(trial_balance["Closing_Debit"].sum(), trial_balance["Closing_Credit"].sum()),
      f"Closing debits={trial_balance['Closing_Debit'].sum():,.2f}; Closing credits={trial_balance['Closing_Credit'].sum():,.2f}")

check("Referential integrity - customers",
      set(ar_invoices["Customer_ID"]).issubset(set(customers["Customer_ID"])),
      "All AR customer IDs exist in Customers")

check("Referential integrity - vendors",
      set(ap_invoices["Vendor_ID"]).issubset(set(vendors["Vendor_ID"])),
      "All AP vendor IDs exist in Vendors")

validation_results = pd.DataFrame(checks)

if not validation_results["Passed"].all():
    raise ValueError(validation_results.to_string(index=False))

# Remove helper column before export
gl_export = gl.drop(columns=["Month"])

# -----------------------------
# Export workbook
# -----------------------------
sheets = {
    "Company": company,
    "Chart_of_Accounts": accounts,
    "Customers": customers,
    "Vendors": vendors,
    "Employees": employees,
    "Departments": departments,
    "Locations": locations,
    "Projects": projects,
    "Fixed_Assets": fixed_assets,
    "Products_Services": products,
    "Tax_Codes": tax_codes,
    "Payment_Terms": payment_terms,
    "GL_Transactions": gl_export,
    "Journal_Entries": journal_entries,
    "AP_Invoices": ap_invoices,
    "AP_Payments": ap_payments,
    "AR_Invoices": ar_invoices,
    "AR_Receipts": ar_receipts,
    "Purchase_Orders": purchase_orders,
    "Sales_Orders": sales_orders,
    "Inventory_Transactions": inventory_transactions,
    "Bank_Transactions": bank_transactions,
    "Credit_Card_Transactions": credit_card_transactions,
    "Expense_Reports": expense_reports,
    "Payroll_Transactions": payroll_transactions,
    "Fixed_Asset_Transactions": fixed_asset_transactions,
    "Opening_Balances": opening_balances,
    "Trial_Balance": trial_balance,
    "GST_Transactions": gst_transactions,
    "Monthly_Balances": monthly_balances,
    "AR_Aging": ar_aging,
    "AP_Aging": ap_aging,
    "Income_Statement": income_statement,
    "Revenue_by_Account": revenue_by_account,
    "Expense_Summary": expense_summary,
    "Expected_Results": expected_results,
    "Validation_Results": validation_results,
    "Data_Dictionary": data_dictionary,
    "README": readme,
}

with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
    for sheet_name, df in sheets.items():
        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

# Apply basic workbook formatting


wb = load_workbook(xlsx_path)
header_fill = PatternFill("solid", fgColor="1F4E78")
header_font = Font(color="FFFFFF", bold=True)

for ws in wb.worksheets:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for col_cells in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col_cells[0].column)
        for cell in col_cells[:200]:
            if cell.value is not None:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max(max_len + 2, 12), 28)

# Number/date formatting
for ws in wb.worksheets:
    headers = {cell.value: cell.column for cell in ws[1]}
    for field in ["Debit","Credit","Opening_Debit","Opening_Credit","Period_Debit","Period_Credit",
                  "Closing_Debit","Closing_Credit","Net_Amount","GST","Gross_Amount","Paid_Amount",
                  "Outstanding_Balance","Amount","Total_Amount","Unit_Price","Unit_Cost","Purchase_Cost",
                  "Standard_Price","Running_Balance","Budget_Revenue","Budget_Cost","Value","Rate"]:
        if field in headers:
            for row in range(2, ws.max_row + 1):
                ws.cell(row=row, column=headers[field]).number_format = '#,##0.00'
    for field in ["Posting_Date","Document_Date","Invoice_Date","Due_Date","Receipt_Date","Payment_Date",
                  "Order_Date","Transaction_Date","Date","Value_Date","Purchase_Date","Start_Date","End_Date",
                  "As_Of_Date","Month","Payroll_Period"]:
        if field in headers:
            for row in range(2, ws.max_row + 1):
                ws.cell(row=row, column=headers[field]).number_format = 'yyyy-mm-dd'

# Highlight validation results
if "Validation_Results" in wb.sheetnames:
    ws = wb["Validation_Results"]
    for row in range(2, ws.max_row + 1):
        if ws.cell(row=row, column=2).value is True:
            ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="C6EFCE")
        else:
            ws.cell(row=row, column=2).fill = PatternFill("solid", fgColor="FFC7CE")

wb.save(xlsx_path)

print(f"Created: {xlsx_path}")
print(f"Workbook sheets: {len(sheets)}")
print(f"GL lines: {len(gl_export):,}")
print(f"Journal entries: {len(journal_entries):,}")
print(f"AP invoices: {len(ap_invoices):,}")
print(f"AR invoices: {len(ar_invoices):,}")
print(f"Bank transactions: {len(bank_transactions):,}")
print(f"Credit-card transactions: {len(credit_card_transactions):,}")
print(f"Validation checks passed: {validation_results['Passed'].all()}")
