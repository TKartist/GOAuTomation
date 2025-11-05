'''
testing staged API endpoint
'''
import pandas as pd

def split_by_appeal(df: pd.DataFrame, appeal_col: str = "appeal_id") -> dict:
    if appeal_col not in df.columns:
        raise KeyError(f"Column '{appeal_col}' not found in DataFrame.")
    # Split the DataFrame into multiple smaller ones, one per appeal_id
    return {aid: group.copy() for aid, group in df.groupby(appeal_col, sort=False)}


df = pd.read_csv("dref3_data_staged.csv")
df["amount_approved"] = df["amount_approved"].fillna(0.0)
df["total_approved"] = df["total_approved"].fillna(0.0)
breakdown = split_by_appeal(df, "appeal_id")

allocations = ["First", "Second", "Third", "Fourth"]

for appeal_id, ops in breakdown.items():
    count = len(ops)
    alloc_count = 0
    onset_count = ops["type_of_onset"].nunique()
    if onset_count > 1:
        print(f"Appeal {appeal_id} has multiple onsets ({onset_count})")
    
    stage_count = ops["stage"].nunique()
    if stage_count > len(ops["appeal_id"]):
        print(f"Appeal {appeal_id} has more recorded stages ({stage_count}) than actual count ({len(ops)})")
    
    def_count = ops["disaster_definition"].nunique()
    if def_count > 1:
        print(f"Appeal {appeal_id} has multiple disaster definitions ({def_count})")
    # for i in range(count):
        
    #     if ops.iloc[i]["allocation"] == "No allocation":
    #         if ops.iloc[i]["amount_approved"] > 0:
    #             print(f"  ERROR: No allocation but amount approved > 0 for operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
    #         else:
    #             if i == 0 and ops.iloc[i]["total_approved"] > 0:
    #                 print(f"  ERROR: No allocation but total approved > 0 for first operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
    #             if i > 0 and ops.iloc[i]["total_approved"] != ops.iloc[i-1]["total_approved"]:
    #                 print(f"  ERROR: No allocation but total approved changed for operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
    #     else:
    #         if ops.iloc[i]["allocation"] != allocations[alloc_count]:
    #             print(f"  ERROR: Unknown allocation '{ops.iloc[i]['allocation']}' for operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
    #         else:
    #             alloc_count += 1
    #             if ops.iloc[i]["amount_approved"] <= 0:
    #                 print(f"  ERROR: Allocation given but amount approved <= 0 for operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
    #             if alloc_count == 1 and ops.iloc[i]["total_approved"] != ops.iloc[i]["amount_approved"]:
    #                 print(f"  ERROR: First allocation total approved does not match amount approved for operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
    #             if alloc_count > 1:
    #                 prev_total = ops.iloc[i-1]["total_approved"]
    #                 expected_total = prev_total + ops.iloc[i]["amount_approved"]
    #                 if ops.iloc[i]["total_approved"] != expected_total:
    #                     print(f"  ERROR: Total approved does not match expected value for operation {ops.iloc[i]['appeal_id']} in stage {ops.iloc[i]['stage']}")
