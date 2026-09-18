import streamlit as st
import pandas as pd


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="General Journal",
    page_icon="📓",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

from src.data_loader import data_loader

data = data_loader()

journal_entries = data["journal_entries"].copy()
gl = data["gl"].copy()

journal_entries.columns = journal_entries.columns.str.strip()
gl.columns = gl.columns.str.strip()


# ============================================================
# CLEAN DATA
# ============================================================

journal_entries["Total_Debit"] = pd.to_numeric(
    journal_entries["Total_Debit"],
    errors="coerce"
).fillna(0)

journal_entries["Total_Credit"] = pd.to_numeric(
    journal_entries["Total_Credit"],
    errors="coerce"
).fillna(0)

gl["Debit"] = pd.to_numeric(
    gl["Debit"],
    errors="coerce"
).fillna(0)

gl["Credit"] = pd.to_numeric(
    gl["Credit"],
    errors="coerce"
).fillna(0)

journal_entries["Posting_Date"] = pd.to_datetime(
    journal_entries["Posting_Date"],
    errors="coerce"
)

gl["Posting_Date"] = pd.to_datetime(
    gl["Posting_Date"],
    errors="coerce"
)


# ============================================================
# JOURNAL BALANCE CHECK
# ============================================================

journal_entries["Balance_Difference"] = (
    journal_entries["Total_Debit"]
    - journal_entries["Total_Credit"]
).abs()


# ============================================================
# PAGE TITLE
# ============================================================

st.title("General Journal")

st.caption(
    "Review posted journal entries and their underlying debit and credit lines."
)


# ============================================================
# JOURNAL ENTRY REGISTER
# ============================================================

st.subheader("Journal Entry Register")


# ------------------------------------------------------------
# Filters
# ------------------------------------------------------------

col1, col2, col3 = st.columns([2, 1, 1])

with col1:

    search = st.text_input(
        "Search",
        placeholder="Entry, source, batch, or description..."
    )

with col2:

    document_types = (
        ["All"]
        + sorted(
            journal_entries["Document_Type"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    selected_document_type = st.selectbox(
        "Document Type",
        document_types
    )

with col3:

    statuses = (
        ["All"]
        + sorted(
            journal_entries["Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    selected_status = st.selectbox(
        "Status",
        statuses
    )


col1, col2, col3 = st.columns([1, 1, 2])

with col1:

    years = (
        ["All"]
        + sorted(
            journal_entries["Posting_Date"]
            .dt.year
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )
    )

    selected_year = st.selectbox(
        "Year",
        years
    )

with col2:

    balance_filter = st.selectbox(
        "Balance",
        ["All", "Balanced", "Unbalanced"]
    )

with col3:

    source_filter = st.text_input(
        "Source ID",
        placeholder="e.g. OPEN-2025 or AR-2025-00001"
    )


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_je = journal_entries.copy()


if search:

    search_columns = [
        "Journal_Entry_ID",
        "Source_ID",
        "Batch_ID",
        "Description"
    ]

    search_mask = pd.Series(
        False,
        index=filtered_je.index
    )

    for column in search_columns:

        if column in filtered_je.columns:

            search_mask |= (
                filtered_je[column]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            )

    filtered_je = filtered_je[search_mask]


if selected_document_type != "All":

    filtered_je = filtered_je[
        filtered_je["Document_Type"].astype(str)
        == selected_document_type
    ]


if selected_status != "All":

    filtered_je = filtered_je[
        filtered_je["Status"].astype(str)
        == selected_status
    ]


if selected_year != "All":

    filtered_je = filtered_je[
        filtered_je["Posting_Date"].dt.year
        == selected_year
    ]


if source_filter:

    filtered_je = filtered_je[
        filtered_je["Source_ID"]
        .astype(str)
        .str.contains(
            source_filter,
            case=False,
            na=False
        )
    ]


if balance_filter == "Balanced":

    filtered_je = filtered_je[
        filtered_je["Balance_Difference"] < 0.01
    ]

elif balance_filter == "Unbalanced":

    filtered_je = filtered_je[
        filtered_je["Balance_Difference"] >= 0.01
    ]


# ============================================================
# REGISTER
# ============================================================

st.write(
    f"**{len(filtered_je):,}** journal entries"
)


register_columns = [
    "Journal_Entry_ID",
    "Posting_Date",
    "Document_Type",
    "Description",
    "Total_Debit",
    "Total_Credit",
    "Status"
]

register_columns = [
    column
    for column in register_columns
    if column in filtered_je.columns
]

register_df = filtered_je[
    register_columns
].copy()


st.dataframe(
    register_df,
    use_container_width=True,
    hide_index=True,
    height=280,

    column_config={

        "Journal_Entry_ID":
            st.column_config.TextColumn(
                "Journal Entry"
            ),

        "Posting_Date":
            st.column_config.DateColumn(
                "Date",
                format="MMM D, YYYY"
            ),

        "Document_Type":
            st.column_config.TextColumn(
                "Type"
            ),

        "Description":
            st.column_config.TextColumn(
                "Description"
            ),

        "Total_Debit":
            st.column_config.NumberColumn(
                "Debit",
                format="$%,.2f"
            ),

        "Total_Credit":
            st.column_config.NumberColumn(
                "Credit",
                format="$%,.2f"
            ),

        "Status":
            st.column_config.TextColumn(
                "Status"
            )
    }
)


# ============================================================
# SELECT JOURNAL ENTRY
# ============================================================

st.divider()

st.subheader("Journal Entry")


if len(filtered_je) == 0:

    st.info(
        "No journal entries match the selected filters."
    )

    st.stop()


# ------------------------------------------------------------
# Entry selector
# ------------------------------------------------------------

je_options = (
    filtered_je["Journal_Entry_ID"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_je_id = st.selectbox(
    "Open Journal Entry",
    je_options
)


selected_je = filtered_je[
    filtered_je["Journal_Entry_ID"].astype(str)
    == selected_je_id
].iloc[0]


# ============================================================
# JOURNAL HEADER
# ============================================================

st.markdown("### General Journal")

st.caption(
    f"Journal Entry: {selected_je['Journal_Entry_ID']}"
)


# ------------------------------------------------------------
# Header information
# ------------------------------------------------------------

header_col1, header_col2, header_col3, header_col4 = st.columns(4)

with header_col1:

    st.markdown("**Date**")

    if pd.notna(selected_je["Posting_Date"]):

        st.write(
            selected_je["Posting_Date"].strftime(
                "%B %d, %Y"
            )
        )

    else:

        st.write("—")


with header_col2:

    st.markdown("**Document Type**")

    st.write(
        selected_je["Document_Type"]
    )


with header_col3:

    st.markdown("**Source**")

    st.write(
        selected_je["Source_ID"]
    )


with header_col4:

    st.markdown("**Status**")

    st.write(
        selected_je["Status"]
    )


# ------------------------------------------------------------
# Description
# ------------------------------------------------------------

st.markdown("**Description**")

st.write(
    selected_je["Description"]
)


# ============================================================
# FIND THE CORRECT GL LINES
# ============================================================

source_id = str(
    selected_je["Source_ID"]
).strip()

batch_id = str(
    selected_je["Batch_ID"]
).strip()


# ------------------------------------------------------------
# First choice:
# Match Source_ID to Document_ID
#
# This prevents something like:
# JE-OPEN-2025
# from pulling every transaction in BATCH-2025-01.
# ------------------------------------------------------------

source_lines = gl[
    gl["Document_ID"]
    .astype(str)
    .str.strip()
    == source_id
].copy()


# ------------------------------------------------------------
# If no source match exists, use Batch_ID.
# ------------------------------------------------------------

if len(source_lines) > 0:

    je_lines = source_lines

else:

    je_lines = gl[
        gl["Batch_ID"]
        .astype(str)
        .str.strip()
        == batch_id
    ].copy()


# ============================================================
# ACCOUNTING LINES
# ============================================================

st.divider()

st.markdown("#### Accounting Lines")


if len(je_lines) == 0:

    st.warning(
        "No GL lines were found for this journal entry."
    )

else:

    # --------------------------------------------------------
    # Prepare display
    # --------------------------------------------------------

    accounting_df = pd.DataFrame({

        "Account":
            je_lines["Account_ID"].astype(str),

        "Account Name":
            je_lines["Account_Name"].astype(str),

        "Description":
            je_lines["Description"]
            .fillna("")
            .astype(str),

        "Debit":
            je_lines["Debit"],

        "Credit":
            je_lines["Credit"]
    })


    # --------------------------------------------------------
    # Use indentation for the account name
    # --------------------------------------------------------

    accounting_df["Account"] = (
        accounting_df["Account"]
        + "  —  "
        + accounting_df["Account Name"]
    )


    accounting_df = accounting_df[
        [
            "Account",
            "Description",
            "Debit",
            "Credit"
        ]
    ]


    # --------------------------------------------------------
    # Create accounting-style display
    # --------------------------------------------------------

    st.dataframe(
        accounting_df,
        use_container_width=True,
        hide_index=True,

        column_config={

            "Account":
                st.column_config.TextColumn(
                    "Account",
                    width="large"
                ),

            "Description":
                st.column_config.TextColumn(
                    "Description",
                    width="large"
                ),

            "Debit":
                st.column_config.NumberColumn(
                    "Debit",
                    format="$%,.2f",
                    width="medium"
                ),

            "Credit":
                st.column_config.NumberColumn(
                    "Credit",
                    format="$%,.2f",
                    width="medium"
                )
        }
    )


    # ========================================================
    # TOTALS
    # ========================================================

    line_debits = je_lines["Debit"].sum()
    line_credits = je_lines["Credit"].sum()

    difference = abs(
        line_debits - line_credits
    )


    st.markdown("")


    # --------------------------------------------------------
    # Totals displayed like an accounting journal
    # --------------------------------------------------------

    total_col1, total_col2 = st.columns(
        [2, 1]
    )

    with total_col1:

        st.markdown(
            "**TOTAL**"
        )

    with total_col2:

        debit_total_col, credit_total_col = st.columns(2)

        with debit_total_col:

            st.markdown(
                f"**${line_debits:,.2f}**"
            )

        with credit_total_col:

            st.markdown(
                f"**${line_credits:,.2f}**"
            )


    st.divider()


    # ========================================================
    # BALANCE
    # ========================================================

    if difference < 0.01:

        st.success(
            "✓ Balanced — Total Debits equal Total Credits."
        )

    else:

        st.error(
            f"Out of Balance — Difference: "
            f"${difference:,.2f}"
        )


# ============================================================
# ENTRY INFORMATION
# ============================================================

with st.expander("Entry Information"):

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Journal Entry:** "
            f"{selected_je['Journal_Entry_ID']}"
        )

        st.write(
            f"**Posting Date:** "
            f"{selected_je['Posting_Date']}"
        )

        st.write(
            f"**Document Type:** "
            f"{selected_je['Document_Type']}"
        )

        st.write(
            f"**Source ID:** "
            f"{selected_je['Source_ID']}"
        )

    with col2:

        st.write(
            f"**Batch ID:** "
            f"{selected_je['Batch_ID']}"
        )

        st.write(
            f"**Status:** "
            f"{selected_je['Status']}"
        )

        st.write(
            f"**GL Lines:** "
            f"{len(je_lines):,}"
        )

        st.write(
            f"**Header Debit:** "
            f"${selected_je['Total_Debit']:,.2f}"
        )

        st.write(
            f"**Header Credit:** "
            f"${selected_je['Total_Credit']:,.2f}"
        )
