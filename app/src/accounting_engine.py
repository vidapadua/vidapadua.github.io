import pandas as pd


def accounting_engine(
    gl: pd.DataFrame,
    accounts: pd.DataFrame
) -> pd.DataFrame:

    balances = (
        gl.groupby("Account_ID", as_index=False)
        .agg(
            Total_Debit=("Debit", "sum"),
            Total_Credit=("Credit", "sum")
        )
    )

    balances["Balance"] = (
        balances["Total_Debit"] -
        balances["Total_Credit"]
    )

    return balances.merge(
        accounts[
            ["Account_ID", "Account_Number", "Account_Name", "Account_Type"]
        ],
        on="Account_ID",
        how="left"
    )