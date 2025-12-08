import pandas as pd

df = pd.read_csv("dref3_data.csv")
clean_df = df.groupby("appeal_id").tail(1).reset_index(drop=True).set_index("appeal_id")
disasters = clean_df["disaster_definition"].unique()

clean_df = clean_df[["country", "region", "disaster_definition", "water_sanitation_and_hygiene"]]
clean_df["water_sanitation_and_hygiene"] = clean_df["water_sanitation_and_hygiene"].apply(lambda x: 1 if x == "Yes" else 0)
print(len(clean_df))
clean_df = clean_df[clean_df["region"] == "Africa"]
print(len(clean_df))

appeal = pd.read_csv("appeals_from_2022_7_1.csv")
appeal["start_date"] = pd.to_datetime(appeal["start_date"])
appeal = appeal[appeal["start_date"] >= pd.Timestamp("2023-01-01", tz='UTC')]
clean_df = clean_df[clean_df.index.isin(appeal["code"])]

out = (
    clean_df.groupby(["country", "disaster_definition"]).agg(
        total_count = ("water_sanitation_and_hygiene", "count"),
        wash_included_in = ("water_sanitation_and_hygiene", "sum"),
        mdr_with_wash=(
            "water_sanitation_and_hygiene",
            lambda s: s.index[s == 1].tolist()
        ),
        mdr_without_wash=(
            "water_sanitation_and_hygiene",
            lambda s: s.index[s == 0].tolist()
        )
    ).reset_index()
)
out.to_excel("africa_wash_from_2023.xlsx", index=False)