import requests as req
import pandas as pd
import ast
from datetime import datetime
import os
import json


def aggregate_appeal_information():
    df = pd.read_csv("csv_files/concat_batch.csv")
    df["operational_strategy"] = df["operational_strategy"].apply(ast.literal_eval)
    df = df.fillna({})

    appeal_df = pd.read_csv("csv_files/docs_from_2022_12_1.csv")
    appeal_df["appeal"] = appeal_df["appeal"].apply(ast.literal_eval)
    appeal_df = appeal_df.fillna("")

    ap_df = pd.read_csv("csv_files/appeals_from_2022_12_1.csv", index_col="code")
    ap_df["country"] = ap_df["country"].apply(ast.literal_eval)
    
    op_code_list = []
    
    for _, row in appeal_df.iterrows():
        op_code_list.append(row["appeal"]["code"])

    appeal_df["op_code"] = op_code_list
    appeal_df.set_index("op_code", inplace=True)

    sheet_one = []
    sheet_two_list = []
    for _, row in df.iterrows():
        code = row["doc_number"][:8]
        val = {
            "mdrcode" : code,
        }
        val["name"] = ap_df["name"][code]
        val["country"] = ap_df["country"][code]["name"]
        val["appeal type"] = ap_df["atype_display"][code]
        val["start_date"] = str(ap_df["start_date"][code])[:10]
        val["funding_requested"] = ap_df["amount_requested"][code]
        val["funding_received"] = ap_df["amount_funded"][code]
        val["num_beneficiaries"] = ap_df["num_beneficiaries"][code]
        if ap_df["status_display"][code] == "Closed":
            val["document_type"] = "Final Report"
        else:
            val["document_type"] = "DREF Operations"
        val["link"] = appeal_df["document"][code] + appeal_df["document_url"][code]
        val["start_date"] = ap_df["start_date"][code]
        val["region"] = row["region_of_disaster"]
        val["assisted"] = row["total_count"]
        
        for strat in row["operational_strategy"]:
            for action in strat["executed_in"]:
                sheet_two = {
                    "mdrcode" : code,
                    "document_type" : val["document_type"],
                    "document_url" : val["link"],
                    "country" : ap_df["country"][code]["name"],
                    "sector" : strat["action"],
                }
                male = 0
                female = 0
                total = 0
                budget = 0
                targeted_population = 0
                if "people_targeted" in action and action["people_targeted"] != None and "total" in action["people_targeted"]:
                    targeted_population = action["people_targeted"]["total"]
                if "funding_used" in action:
                    budget = action["funding_used"]
                if "people_reached" not in action or action["people_reached"] == None:
                    sheet_two["budget (CHF)"] = budget
                    sheet_two["targeted_all"] = targeted_population
                    sheet_two["assisted_all"] = total
                    sheet_two["assisted_male"] = male
                    sheet_two["assisted_female"] = female
                    sheet_two["narrative"] = ""
                    sheet_two_list.append(sheet_two)
                    continue
                if "male" in action["people_reached"]:
                    male = action["people_reached"]["male"]
                if "female" in action["people_reached"]:
                    female = action["people_reached"]["female"]
                if "total" in action["people_reached"]:
                    total = action["people_reached"]["total"]
                else:
                    total = male + female
                disag = f"{strat["action"]} action helped total of {total} people in {action["country"]}; Where {male} were men, and {female} were women. Funding spent is/was {budget}\n"
                sheet_two["budget (CHF)"] = budget
                sheet_two["targeted_all"] = targeted_population
                sheet_two["assisted_all"] = total
                sheet_two["assisted_male"] = male
                sheet_two["assisted_female"] = female
                sheet_two["narrative"] = disag
                sheet_two_list.append(sheet_two)


        sheet_one.append(val)


    output_one = pd.DataFrame(sheet_one)
    output_two = pd.DataFrame(sheet_two_list)
    output_one.set_index("mdrcode", inplace=True)
    with pd.ExcelWriter("csv_files/disaggregation.xlsx", engine='xlsxwriter') as writer:
        output_one.to_excel(writer, sheet_name='appeal_list')
        output_two.to_excel(writer, sheet_name='aggregation', index=False)
