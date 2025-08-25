import pandas as pd


df3 = pd.read_excel("../captions_collected_with_summary_ver2.xlsx")
df = pd.read_csv("../captions_collected_with_summary.csv")
cols = df.columns.tolist()
df2 = pd.read_csv("../gym_1_net_sol_limitless_step1.csv", index_col=0)
df["project_title"] = df3["project_title"].tolist()
df["project_summary"] = df3["project_summary"].tolist()
df["youtube_link"] = df2["project_title"].tolist()
df["project_id"] = df2["project_id"].tolist()
df = df[["project_id", "youtube_link", "project_title", "project_summary", "all_sdg", "main_sdg", "meta_sdg", "fund", "project_type", "selection_year", "big_six_org"]]
df.to_csv("../captions_collected_with_summary.csv", index=False)