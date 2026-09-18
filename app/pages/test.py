import streamlit as st

from src.data_loader import data_loader

st.set_page_config(
    page_title="Data Columns",
    page_icon="🔍",
    layout="wide"
)

st.title("Data Dictionary — Sheet Columns")

data = data_loader()

for sheet_name, df in data.items():

    st.subheader(sheet_name)

    st.write(f"**Rows:** {len(df)}")
    st.write(f"**Columns:** {len(df.columns)}")

    for i, column in enumerate(df.columns, start=1):
        st.write(f"{i}. `{column}`")

    st.divider()