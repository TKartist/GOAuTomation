import pandas as pd

col_names = {
    "Risk Reduction, Climate Adaptation And Recovery": "sector_risk_reduction_climate_adaption_and_recovery",
    "Livelihoods and Basic Needs": "sector_livelihoods",
    "Multi-purpose Cash": "sector_multi_purpose_cash",
    "National Society Strengthening": "sector_national_society_strengthening",
    "Health": "sector_health",
    "Secretariat Services": "sector_secretariat_services",
    "Community Engagement And Accountability": "sector_community_engagement_and_accountability",
    "Water, Sanitation, And Hygiene": "sector_water_sanitation_and_hygiene",
    "Protection, Gender And Inclusion": "sector_protection_gender_and_inclusion"
}

df = pd.read_csv("csv_files/disags_mdrmn017.csv")
df["sector"] = df["sector"].map(lambda x: col_names.get(x, x))
print(df["sector"].tolist())

dref3_data = pd.read_csv("dref3_export.csv")
cols = dref3_data.columns.tolist()
count = df['mdrcode'].unique().tolist()
l = []
for i in (count):
    d_df = df[df["mdrcode"] == i]
    line = {}
    for col in cols:
        line[col] = None
        if col.startswith("sector_") and col.endswith("_budget"):
            line[col] = 0
            continue
        if col.startswith("sector_") and col.endswith("_targeted"):
            line[col] = 0
            continue
        if col.startswith("sector_"):
            line[col] = False
        
        
    for index, row in d_df.iterrows():
        if row["sector"] in cols:
            print(row["sector"])
            line[row["sector"]] = True
            line[f"{row["sector"]}_budget"] = row["budget (CHF)"]
            line[f"{row["sector"]}_targeted"] = row["targeted_all"]

    line["id"] = 0
    line["stage"] = "Final Report"
    line["pillar"] = "Response"
    line["allocation_type"] = "DREF"
    line["country"] = d_df["country"].unique()[0]
    line["appeal_id"] = i
    l.append(line)
dummy = pd.DataFrame(l)
dummy.to_csv("csv_files/dref3_mdrmn017_sector_update.csv", index=False)
