import pandas as pd
from datetime import datetime
import ast

def date_semantics_check(df):
    print("Running semantic validity checks on date cols...")
    one_year_ago = pd.Timestamp.now(tz="UTC") - pd.DateOffset(years=1)
    
    # start_date needs to be the same day or before the created_at date
    df["cond_1"] = df["start_date"] > df["created_at"]
    
    # Check if start_date of appeal was before end_date
    df["cond_2"] = df["start_date"] > df["end_date"]

    # Flag active operations which has end_date was reached more than a year ago
    df["cond_3"] = (df["end_date"] < one_year_ago) & (df["status_display"] == "Active")

    flag_cols = ["cond_1", "cond_2", "cond_3"]


    rows_with_any_true = df[df[flag_cols].any(axis=1)]  


    rows_with_any_true.to_csv("date_semantics_check.csv")


def numerical_semantics_check(df):
    print("Running semantic validity checks on numerical cols...")

    df["cond_1"] = df["num_beneficiaries"] < 0
    df["cond_2"] = df["amount_requested"] < 0
    df["cond_3"] = df["amount_funded"] < 0

    flag_cols = ["cond_1", "cond_2", "cond_3"]

    rows_with_any_true = df[df[flag_cols].any(axis=1)]

    rows_with_any_true.to_csv("numerical_semantics_check.csv")




def count_active(df):
    alp = df[df["status_display"] == "Active"]
    print(len(alp))


# Assessments for duplication
# Counting duplication of ID and other UNIQUE fields
def unique_value_check(df, col):
    unique_count = df[col].nunique()
    if unique_count != len(df):
        print(f"{col} is a column with unique values but identified {unique_count} unique identifiers out of {len(df)} rows")
        for value, group in df.groupby(col):
            if len(group) >= 2:
                print(value)
                print(group)
                print("-" * 40)

# Looking for duplicate operations generated from multi-country appeals
def duplicate_operations(appeal, dref3):
    drefs = appeal[appeal["atype_display"] == "DREF"]
    drefs = drefs[(drefs["start_date"].dt.year > 2022) & (drefs["start_date"].dt.year < 2025)]
    # dict: {appeal_id: subset_dataframe}
    dref3_dict = {k: len(g) for k, g in dref3.groupby("appeal_id")}
    drefs["sufficient"] = drefs["code"].apply(lambda x: dref3_dict.get(x, 10) < 2)
    drefs = drefs[drefs["sufficient"]]
    drefs.to_csv("potential_multi_ops.csv")

        

