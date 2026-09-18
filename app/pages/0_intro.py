import streamlit as st


st.set_page_config(
    page_title="Vida's Oil & Gas Company",
    page_icon="📊",
    layout="wide",
)


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>
        .hero {
            background: linear-gradient(
                135deg,
                #0f172a,
                #1e3a5f,
                #2563eb
            );
            padding: 2.5rem 3rem;
            border-radius: 18px;
            color: white;
            margin-bottom: 1.5rem;
        }

        .hero h1 {
            font-size: 2.8rem;
            margin: 0 0 0.5rem 0;
        }

        .hero p {
            font-size: 1.1rem;
            color: #dbeafe;
            margin: 0.25rem 0;
        }

        .stat {
            text-align: center;
            padding: 1rem;
            border-radius: 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
        }

        .stat-number {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e3a5f;
        }

        .stat-label {
            color: #64748b;
            font-size: 0.9rem;
        }

        .tech-card {
            padding: 1.2rem;
            border-radius: 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            height: 100%;
        }

        .tech-card h4 {
            margin: 0 0 0.4rem 0;
            color: #0f172a;
        }

        .tech-card p {
            margin: 0;
            color: #64748b;
            font-size: 0.9rem;
        }

        .flow {
            text-align: center;
            padding: 1.2rem;
            background: #eff6ff;
            border-radius: 12px;
            color: #1e3a5f;
            font-weight: 600;
            font-size: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HERO — ALL IMPORTANT TEXT AT THE TOP
# =========================================================

st.title("📊 Peak Accounting System")

st.subheader("A complete accounting workflow built with Python")

st.write(
    """
    This application was built to demonstrate the accounting process
    from transaction entry through reconciliation, month-end close,
    financial reporting, analysis, and audit.
    """
)

st.write(
    """
    It uses a large sample accounting dataset with 20,000+ general
    ledger transactions and data across customers, vendors, AP, AR,
    banking, expenses, payroll, fixed assets, GST, and more.
    """
)

st.caption(
    "Built with Python, Pandas, Streamlit, and Excel • Sample data for demonstration"
)

st.divider()



# =========================================================
# QUICK STATS
# =========================================================

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        """
        <div class="stat">
            <div class="stat-number">20K+</div>
            <div class="stat-label">GL Transactions</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="stat">
            <div class="stat-number">30+</div>
            <div class="stat-label">Accounting Tables</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        """
        <div class="stat">
            <div class="stat-number">8</div>
            <div class="stat-label">Accounting Areas</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        """
        <div class="stat">
            <div class="stat-number">2</div>
            <div class="stat-label">Years of Sample Data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.write("")


# =========================================================
# ACCOUNTING FLOW
# =========================================================

st.markdown(
    """
    <div class="flow">
        Transactions
        &nbsp; → &nbsp;
        General Ledger
        &nbsp; → &nbsp;
        Reconciliation
        &nbsp; → &nbsp;
        Month-End Close
        &nbsp; → &nbsp;
        Financial Statements
        &nbsp; → &nbsp;
        Analysis
        &nbsp; → &nbsp;
        Audit
    </div>
    """,
    unsafe_allow_html=True,
)


st.write("")


# =========================================================
# TECHNOLOGY
# =========================================================

st.subheader("Built With")

t1, t2, t3, t4 = st.columns(4)

with t1:
    st.markdown(
        """
        <div class="tech-card">
            <h4>🐍 Python</h4>
            <p>Core programming language and accounting logic.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with t2:
    st.markdown(
        """
        <div class="tech-card">
            <h4>📊 Pandas</h4>
            <p>Data loading, transformation, calculations and analysis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with t3:
    st.markdown(
        """
        <div class="tech-card">
            <h4>🎈 Streamlit</h4>
            <p>Interactive application and user interface.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with t4:
    st.markdown(
        """
        <div class="tech-card">
            <h4>📗 Excel</h4>
            <p>Source workbook containing the sample accounting data.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DATA NOTE
# =========================================================

st.write("")

st.caption(
    "Sample data only • Created for demonstration and presentation purposes. Created by Vida Padua 2026."
)