import pandas as pd

appeals = pd.read_csv("data/appeal.csv")
appeals['start_date'] = pd.to_datetime(appeals['start_date'], format='%Y-%m-%dT%H:%M:%SZ')
appeals = appeals[appeals["start_date"].dt.year == 2025]
appeals = appeals[["code", "start_date", "end_date"]]
ap_code = appeals["code"].tolist()

df = pd.read_csv("data/dref3_all_records.csv")
df = df[df["appeal_id"].isin(ap_code)]
df = df.groupby('appeal_id').tail(1).reset_index(drop=True)
cols = ["appeal_id", "pillar", "appeal_type", "allocation_type", "country", "country_iso3", "region", "disaster_definition", "disaster_name", "type_of_onset", "crisis_categorization", "total_approved", "operation_status", "people_affected", "people_targeted", "people_assisted", "population_disaggregation"]
cols.append("sector_community_engagement_and_accountability")
cols.append("sector_community_engagement_and_accountability_budget")
cols.append("sector_community_engagement_and_accountability_people_targeted")
df = df[cols]

df_merged = df.merge(appeals, left_on='appeal_id', right_on='code',how='left')

df_merged.to_csv("cea_2025.csv", index=False)

