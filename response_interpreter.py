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



def verify_extract():
    df = pd.read_csv("csv_files/concat_batch.csv", index_col="doc_number")
    df["operational_strategy"] = df["operational_strategy"].apply(ast.literal_eval)

    df2 = pd.read_csv("csv_files/final_report_details.csv", index_col="mdrcode")
    df2["actions"] = df2["actions"].apply(ast.literal_eval)
    ind = df2.index
    l = []
    for i in ind:
        if i not in df.index:
            continue
        extract_list = []
        record_list = []

        for op in df["operational_strategy"][i]:
            for action in op["executed_in"]:
                extract_list.append({
                    "mdrcode" : i,
                    "action (extracted)" : op.get("action", ""),
                    "total_reached (extracted)" : (action and action.get("people_reached", {}) or {}).get("total", 0),  
                    "total_male (extracted)" : (action and action.get("people_reached", {}) or {}).get("male", 0),  
                    "total_female (extracted)" : (action and action.get("people_reached", {}) or {}).get("female", 0),
                    "fund (extracted)" : action.get("funding_used", 0),  
                })
        for list in df2["actions"][i]:
            record_list.append({
                "mdrcode" : i,
                "action (doc)" : list.get("title_display", ""),
                "total_reached (doc)" : list.get("person_assisted", 0),
                "total_male (doc)" : list.get("male", 0),
                "total_female (doc)" : list.get("female", 0),
                "fund (doc)" : list.get("budget", 0),
            })
        sorted_extracted_list = sorted(extract_list, key=lambda x: x["action (extracted)"])
        sorted_record_list = sorted(record_list, key=lambda x: x["action (doc)"])
        length = 0
        if len(sorted_extracted_list) > len(sorted_record_list):
            length = len(sorted_record_list)
        else:
            length = len(sorted_extracted_list)
        for j in range(length):
            l.append({
                "mdrcode" : i,
                "action (extracted)" : sorted_extracted_list[j]["action (extracted)"],
                "total_reached (extracted)" : sorted_extracted_list[j]["total_reached (extracted)"],
                "total_male (extracted)" : sorted_extracted_list[j]["total_male (extracted)"],
                "total_female (extracted)" : sorted_extracted_list[j]["total_female (extracted)"],
                "fund (extracted)" : sorted_extracted_list[j]["fund (extracted)"],
                "action (doc)" : sorted_record_list[j]["action (doc)"],
                "total_reached (doc)" : sorted_record_list[j]["total_reached (doc)"],
                "total_male (doc)" : sorted_record_list[j]["total_male (doc)"],
                "total_female (doc)" : sorted_record_list[j]["total_female (doc)"],
                "fund (doc)" : sorted_record_list[j]["fund (doc)"],
            })
        if len(sorted_extracted_list) > len(sorted_record_list):
            for j in range(length, len(sorted_extracted_list)):
                l.append({
                    "mdrcode" : i,
                    "action (extracted)" : sorted_extracted_list[j]["action (extracted)"],
                    "total_reached (extracted)" : sorted_extracted_list[j]["total_reached (extracted)"],
                    "total_male (extracted)" : sorted_extracted_list[j]["total_male (extracted)"],
                    "total_female (extracted)" : sorted_extracted_list[j]["total_female (extracted)"],
                    "fund (extracted)" : sorted_extracted_list[j]["fund (extracted)"],
                    "action (doc)" : "",
                    "total_reached (doc)" : 0,
                    "total_male (doc)" : 0,
                    "total_female (doc)" : 0,
                    "fund (doc)" : 0,

                })
        else:
            for j in range(length, len(sorted_record_list)):    
                l.append({
                    "mdrcode" : i,
                    "action (extracted)" : "",
                    "total_reached (extracted)" : 0,
                    "total_male (extracted)" : 0,
                    "total_female (extracted)" : 0,
                    "fund (extracted)" : 0,
                    "action (doc)" : sorted_record_list[j]["action (doc)"],
                    "total_reached (doc)" : sorted_record_list[j]["total_reached (doc)"],
                    "total_male (doc)" : sorted_record_list[j]["total_male (doc)"],
                    "total_female (doc)" : sorted_record_list[j]["total_female (doc)"],
                    "fund (doc)" : sorted_record_list[j]["fund (doc)"],
                })
        df3 = pd.DataFrame(l)
        with pd.ExcelWriter("csv_files/disags.xlsx", mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            df3.to_excel(writer, sheet_name='verification', index=False)

verify_extract()