import requests as req
import pandas as pd
import ast
from datetime import datetime
import os
import json

df = pd.read_csv("first_batch.csv")
appeal_df = pd.read_csv("final_reports_from_2022_12_1.csv")
appeal_df["appeal"] = appeal_df["appeal"].apply(ast.literal_eval)
appeal_df = appeal_df.fillna("")

l = []
for _, row in appeal_df.iterrows():
    l.append(row["appeal"]["code"])

appeal_df["op_code"] = l
appeal_df.set_index("op_code", inplace=True)
df["operational_strategy"] = df["operational_strategy"].apply(ast.literal_eval)

list = []

for _, row in df.iterrows():
    code = row["doc_number"][:8]
    val = {
        "op_code" : code,
    }
    val["link"] = appeal_df["document"][code] + appeal_df["document_url"][code]
    val["name"] = appeal_df["appeal"][code]["event"]["name"]
    val["start_date"] = appeal_df["appeal"][code]["event"]["start_date"]
    val["region"] = row["region_of_disaster"]
    val["assisted"] = row["total_count"]
    disag = ""
    for strat in row["operational_strategy"]:
        for action in strat["executed_in"]:
            male = 0
            female = 0
            total = 0
            if "people_reached" not in action or action["people_reached"] == None or ("male" not in action["people_reached"] and "female" not in action["people_reached"]):
                continue
            if "male" in action["people_reached"]:
                male = action["people_reached"]["male"]
            if "female" in action["people_reached"]:
                female = action["people_reached"]["female"]
            total = male + female
            disag += f"{strat["action"]} action helped total of {total} people in {action["country"]}; Where {male} were men, and {female} were women.\n"
    val["disaggregation (strategy specific)"] = disag
    list.append(val)

output = pd.DataFrame(list)
output.set_index("op_code", inplace=True)
output.to_excel("sex_disaggregation_from_2022_12_1.xlsx", index="op_code")