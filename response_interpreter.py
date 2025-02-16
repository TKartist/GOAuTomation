import requests as req
import pandas as pd
import ast
from datetime import datetime
import os
import json


def aggregate_appeal_information():
    df = pd.read_csv("first_batch.csv")
    appeal_df = pd.read_csv("docs_from_2022_12_1.csv")
    appeal_df["appeal"] = appeal_df["appeal"].apply(ast.literal_eval)
    appeal_df = appeal_df.fillna("")

    ap_df = pd.read_csv("appeals_from_2022_12_1.csv", index_col="code")
    ap_df["country"] = ap_df["country"].apply(ast.literal_eval)
    op_code_list = []
    for _, row in appeal_df.iterrows():
        op_code_list.append(row["appeal"]["code"])

    appeal_df["op_code"] = op_code_list
    appeal_df.set_index("op_code", inplace=True)
    df["operational_strategy"] = df["operational_strategy"].apply(ast.literal_eval)

    sheet_one = []

    for _, row in df.iterrows():
        code = row["doc_number"][:8]
        val = {
            "mdrcode" : code,
        }
        val["name"] = appeal_df["appeal"][code]["event"]["name"]
        val["country"] = ap_df["country"][code]["name"]
        val["appeal type"] = ap_df["atype_display"][code]
        val["start_date"] = str(ap_df["start_date"][code])[:10]
        val["funding_requested"] = ap_df["amount_requested"][code]
        val["funding_received"] = ap_df["amount_funded"][code]
        val["num_beneficiaries"] = ap_df["num_beneficiaries"][code]
        if ap_df["status_display"] == "Closed":
            val["document_type"] = "Final Report"
        else:
            val["document_type"] = "DREF Operations"
        val["link"] = appeal_df["document"][code] + appeal_df["document_url"][code]

        sheet_one.append(val)
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

    output_one = pd.DataFrame(sheet_one)
    output_one.set_index("op_code", inplace=True)
    with pd.ExcelWriter("disaggregation.xlsx", engine='xlsxwriter') as writer:
        output_one.to_excel(writer, sheet_name='appeal_list', index=False)
        # df2.to_excel(writer, sheet_name='aggregation', index=False)

