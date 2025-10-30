import pandas as pd
import ast

df = pd.read_csv("dref3_data.csv")
print(len(df))
df_last = df.drop_duplicates(subset="appeal_id", keep="last")
print(len(df_last))
df_last = df_last.set_index("appeal_id")

total_budget = []
cea = []
cea_budget = []
counter = 0
df = pd.read_excel("docs_from_2022_7_1.xlsx", sheet_name="Sheet1", index_col="code")
df = df[df["atype_display"] == "DREF"]
for index, row in df.iterrows():
    if index in df_last.index:
        total_budget.append(df_last.loc[index, "total_approved"])
        cea.append(df_last.loc[index, "community_engagement_and_accountability"])
        cea_budget.append(df_last.loc[index, "community_engagement_and_accountability_budget"])
    else:
        counter += 1
        total_budget.append(-1)
        cea.append("none_existing")
        cea_budget.append(-1)

print(counter)
df["total_approved"] = total_budget
df["CEA_COMPONENT"] = cea
df["CEA_BUDGET"] = cea_budget

df = df[df["CEA_COMPONENT"] != "none_existing"]

cols = ["document_url", "name", "atype_display", "country", "region", "total_approved", "CEA_COMPONENT", "CEA_BUDGET", "dtype", "start_date", "end_date"]
df = df[cols]
df["country"] = df["country"].apply(lambda x: ast.literal_eval(x)["iso"])
df["region"] = df["region"].apply(lambda x: ast.literal_eval(x)["region_name"])
df = df.fillna(-1)
df.to_excel("docs_with_budget.xlsx", index=True)
