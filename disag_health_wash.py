import pandas as pd

df = pd.read_csv("dref3_data.csv")
print(len(df))
df_last = df.drop_duplicates(subset="appeal_id", keep="last")
print(len(df_last))
df_last = df_last.set_index("appeal_id")

total_budget = []
health_budget = []
wash_budget = []

df = pd.read_excel("docs_from_2022_12_1.xlsx", sheet_name="Sheet1", index_col="code")
for index, row in df.iterrows():
    if index in df_last.index:
        total_budget.append(df_last.loc[index, "total_approved"])
        health_budget.append(df_last.loc[index, "health_budget"])
        wash_budget.append(df_last.loc[index, "water_sanitation_and_hygiene_budget"])
    else:
        total_budget.append(-1)
        health_budget.append(-1)
        wash_budget.append(-1)

df["total_approved"] = total_budget
df["health_budget"] = health_budget
df["wash_budget"] = wash_budget

cols_to_fill = ["total_approved", "health_budget", "wash_budget"]
df[cols_to_fill] = df[cols_to_fill].fillna(-1)

cols = ["document_url", "total_approved", "health_budget", "wash_budget"]
df = df[cols + [col for col in df.columns if col not in cols]]

df.to_excel("docs_with_budget.xlsx", index=True)