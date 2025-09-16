import pandas as pd
import ast
import numpy as np

df_erp = pd.read_excel("erp_data.xlsx", header=0, index_col="Appeal ID")
df_go = pd.read_csv("all_appeals.csv", index_col="code")
df_go["start_date"] = pd.to_datetime(df_go["start_date"], utc=True)
df_master = pd.read_csv("dref_masterset.csv", index_col="Appeal ID")
df_master = df_master[~df_master.index.isnull()]
df_erp["Start date"] = pd.to_datetime(df_erp["Start date"], errors="coerce")
print(df_erp["Start date"].head)
df_master["Date of Approval EnC (start date)"] = pd.to_datetime(df_master["Date of Approval EnC (start date)"], format="%d/%m/%Y", errors="coerce")


# dupes = df_erp.index[df_erp.index.duplicated()]
# print("ERP")
# print(dupes)

# dupes = df_go.index[df_go.index.duplicated()]
# print("GO")
# print(dupes)
# dupes = df_master.index[df_master.index.duplicated()]
# print("Master")
# print(dupes)

'''
1st: ERP
2nd: GO
3rd: Master
'''

categorizations = [
    ["Earthquake", "Earthquake", "Earthquake"],
    ["Cholera", "Cholera", "Cholera"],
    ["Flood", "Flood", "Flood"],
    ["Extreme Winter", "Cold Wave", "Cold Wave"],
    ["Drought", "Drought", "Drought"],
    ["Meningitis", "Meningitis", "Meningitis"],
    ["Population Movement", "Population Movement", "Population Movement"],
    ["Other disasters", "Other", "Other"],
    ["Civil Unrest", "Civil Unrest", "Civil Unrest"],
    ["Typhoon", "Cyclone", "Cyclone"],
    ["Polio & Measles", "Polio & Measles", "Polio & Measles"],
    ["Hurricane", "Cyclone", "Cyclone"],
    ["Landslide", "Landslide", "Landslide"],
    ["Cyclone", "Cyclone", "Cyclone"],
    ["Volcano", "Volcanic Eruption", "Volcanic Eruption"],
    ["Yellow Fever", "Yellow Fever", "Yellow Fever"],
    ["Famine / Food", "Food Insecurity", "Food Insecurity"],
    ["Ebola", "Ebola", "Ebola"],
    ["Natural fire", "Fire", "Fire"],
    ["Miscellaneous Explos", "Other", "Other"],
    ["Tropical storm", "Other", "Cyclone"],
    ["Storm Surge", "Storm Surge", "Storm Surge"],
    ["Other epidemic", "Epidemic", "Epidemic"],
    ["Cold Wave", "Cold Wave", "Cold Wave"],
    ["Tsunami", "Tsunami", "Tsnuami"],
    ["Industrial Explosion", "Other", "Other"],
    ["Complex Emergency", "Complex Emergency", "Complex Emergency"],
    ["Chemical spill", "Chemical Emergency", "Chemical Emergency"],
    ["Avalanche", "Other", "Other"],
    ["Insect / Animal", "Insect Infestation", "Insect Infestation"],
    ["Other Industrial Acc", "Other", "Other"],
    ["Miscellaneous Collap", "Other", "Other"],
    ["Poisoning", "Biological Emergency", "Biological Emergency"],
    ["Radiation / Nuclear", "Other", "Other"],
    ["Dengue", "Epidemic", "Epidemic"],
    ["COVID-19", "COVID-19", "COVID-19"],
    ["Biological", "Other", "Other"],
    ["Zika", "Zika", "Zika"],
    ["Flash floods", "Pluvial/Flash Flood", "Pluvial/Flash Flood"],
    ["Other", "Other", "Other"],
    ["Heat Wave", "Heat Wave", "Heat Wave"],
    ["Local storm", "Other", "Other"],
    ["Epidemic", "Epidemic", "Epidemic"],
    ["Technical Fire", "Other", "Other"],
    ["Urban Fire", "Fire", "Fire"],
    ["Fire", "Fire", "Fire"],
    ["Meteorological", "Other", "Other"],
    ["Transport Accident", "Transport Accident", "Transport Accident"],
    ["Volcanic Eruption", "Volcanic Eruption", "Volcanic Eruption"],
    ["Rockfall", "Other", "Other"],
    ["Diarrhoea", "Other", "Other"],
    ["Industrial Collapse", "Other", "Other"],
    ["Lassa Fever", "Other", "Other"],
    ["Other Miscellaneous", "Other", "Other"]
]


df_go["dtype"] = df_go["dtype"].apply(ast.literal_eval)
df_go["Disaster_GO"] = df_go["dtype"].apply(lambda x: x["name"])
print("GO categorizations")
print(df_go["Disaster_GO"].unique())

df_erp = df_erp.rename(columns={"Disaster type": "Disaster_ERP"})
print("ERP categorizations")
print(df_erp["Disaster_ERP"].unique())
df_master = df_master.rename(columns={"Disaster Definition": "Disaster_Master"})
print("Master categorizations")
print(df_master["Disaster_Master"].unique())


erp = df_erp["Disaster_ERP"]
erp.name = "ERP"
go = df_go["Disaster_GO"]
go.name = "GO"

master = df_master["Disaster_Master"]
master = master.groupby(master.index).agg(set)
# print(df_master.head())
master.name = "Mastersheet"

def last_from_set(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, set) and val:
        return list(val)[-1]   # pick the last item as given by list()
    return val

merged = pd.concat([erp, go, master], axis=1)
# print(len(merged))

merged = merged.dropna(how="all")
print(merged.head())
merged["Master_last"] = merged["Mastersheet"].apply(last_from_set)
# print(len(merged))

# print(merged.columns)
# print(merged.head())

# merged.to_excel("disaster_type_comparison.xlsx", index=True)

cat_df = pd.DataFrame(categorizations, columns=["ERP", "GO", "Master"])
cat_df = cat_df.set_index("ERP")
print(cat_df.head())
marks = []
dates = []

for index, row in merged.iterrows():
    go = row["GO"]
    erp = row["ERP"]
    master = row["Master_last"]

    # use pd.notna on scalars
    if pd.notna(go) and pd.notna(erp) and pd.notna(master):
        temp = cat_df.loc[erp, "GO"] if erp in cat_df.index else np.nan
        marks.append(go == temp and master == temp)
        dates.append(df_erp["Start date"][index])
        continue

    if pd.notna(erp) and pd.notna(go):
        temp = cat_df.loc[erp, "GO"] if erp in cat_df.index else np.nan
        marks.append(go == temp)
        dates.append(df_erp["Start date"][index])
        continue

    if pd.notna(erp) and pd.notna(master):
        temp = cat_df.loc[erp, "GO"] if erp in cat_df.index else np.nan
        marks.append(master == temp)
        dates.append(df_erp["Start date"][index])
        continue

    if pd.notna(go) and pd.notna(master):
        marks.append(go == master)
        dates.append(df_go["start_date"][index])
        continue
    
    dates.append(pd.to_datetime("2025-09-10"))
    marks.append(True)

print(len(merged))
print(len(dates))
merged["Correct_cat"] = marks
merged["start_date"] = dates
merged["start_date"] = (
    pd.to_datetime(merged["start_date"], errors="coerce", utc=True)
      .dt.tz_convert(None)
)

merged = merged[merged["Correct_cat"] == False]
merged = merged.drop(columns=["Correct_cat"])
merged = merged.sort_values(by="start_date", ascending=False)
merged.to_excel("disaster_type_comparison.xlsx", index=True)

print(f"Potential Issue: {marks.count(False)}")


    
