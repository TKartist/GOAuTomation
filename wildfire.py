import json
import pandas as pd
import requests
import ast

df = pd.read_csv("fire_emergencies_5_years.csv")
df["disaster_start_date"] = pd.to_datetime(df["disaster_start_date"])
print(f"From {df['disaster_start_date'].min().date()} to {df['disaster_start_date'].max().date()}, GO recorded {len(df)} wildfire emergencies and responded to {df['appeals.id'].nunique()} appeals.")

# appeals = []

# with requests.Session() as session:
#     for _, row in df.iterrows():
#         appeal_id = row["appeals.id"]
#         if not appeal_id:
#             continue
#         url = f"https://goadmin.ifrc.org/api/v2/appeal/?appeal_id={appeal_id}"
#         res = session.get(url)
#         if res.status_code == 200:
#             appeals.append(res.json()["results"][0])
    
# appeals_df = pd.DataFrame(appeals)
# appeals_df.to_csv("wildfire_appeals.csv", index=False)
# print(f"Collected {len(appeals_df)} appeals from GO API.")

appeals_df = pd.read_csv("wildfire_appeals.csv")

appeals_df["start_date"] = pd.to_datetime(appeals_df["start_date"])
appeals_df["year"] = appeals_df["start_date"].dt.year
yearly_counts = appeals_df.groupby("year").size().reset_index(name="appeal_count")
print("Yearly appeal counts:")
print(yearly_counts)

requested = appeals_df["amount_requested"].sum()
approved = appeals_df["amount_funded"].sum()

print(f"Total requested amount in last 5 years: {requested} CHF")
print(f"Total approved amount in last 5 years: {approved} CHF")
helped_people = appeals_df["num_beneficiaries"].sum()
print(f"Total people targeted for assistance in last 5 years: {helped_people}")

drefs = appeals_df[appeals_df["atype_display"] == "DREF"]
print(f"Out of {len(appeals_df)} appeals, {len(drefs)} were DREFs and 1 was an Emergency Appeal.")
print(f"On average, each {drefs["amount_funded"].mean():.2f} CHF was approved for DREF appeals.")
print(f"We have reached {drefs["amount_requested"].sum() / drefs["amount_funded"].sum() * 100}% funding requirements for DREF appeals originating from wildfires.")
appeals_df["region"] = appeals_df["region"].apply(lambda x: ast.literal_eval(x)["region_name"])
region_counts = appeals_df.groupby("region").size().reset_index(name="appeal_count")
print(region_counts)