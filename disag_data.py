import pandas as pd

df = pd.read_excel("disaggregation_data.xlsx")
df = df[df['sector'] != 'Education']
grouped_df = df.groupby("sector").mean(numeric_only=True) * 100

s_disag = df["Sex Disaggregation Provided"].sum() / 61 * 100
a_disag = df["Age Disaggregation Provided"].sum() / 61 * 100
d_disag = df["Disability Disaggregation Provided"].sum() / 61 * 100
ru_disag = df["Rural/Urban Disaggregation Provided"].sum() / 61 * 100

new_row = {
    "sector": "Total",
    "Sex Disaggregation Provided": s_disag,
    "Age Disaggregation Provided": a_disag,
    "Disability Disaggregation Provided": d_disag,
    "Rural/Urban Disaggregation Provided": ru_disag
}

new_df = pd.DataFrame([new_row])  # ✅ Fix here

grouped_df = pd.concat([grouped_df.reset_index(), new_df], ignore_index=True)
grouped_df = grouped_df.round(1)
grouped_df = grouped_df.applymap(lambda x: f"{x:.1f}%" if isinstance(x, (int, float)) else x)
grouped_df.to_excel("disaggregation.xlsx", index=False)
