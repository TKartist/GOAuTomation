import ast
import json
import pandas as pd
import requests as req

# with open("output_files/summary_file.txt", "r") as f:
#     text = f.read()
#     f.close()

# text = text.replace("```json", "").replace("```", "").replace("\n", " ")
# list_version = ast.literal_eval(text)
# json_objs = []
# for item in list_version:
#     item = "{" + "{".join(item.split("{")[1:])
#     item = "}".join(item.split("}")[:-1]) + "}"
#     item = item.replace("\n", "")

#     try:
#         data = json.loads(item)
#         json_objs.append(data)
#     except Exception as e:
#         print("Error parsing json: ", e)

# df = pd.DataFrame(json_objs)
# df.to_csv("csv_files/second_batch.csv")

# df = pd.read_csv("csv_files/first_batch.csv")
# df_1 = pd.read_csv("csv_files/second_batch.csv")
# df_2 = pd.concat([df, df_1], ignore_index=True)
# df_2.to_csv("csv_files/concat_batch.csv", index=False)

base_url = "https://goadmin.ifrc.org/"
api_endpoint = "api/v2/appeal_document/"
params = {"search" : "MDRBD003"}
appeals_list = []
link = base_url + api_endpoint

try:
    while link != None:
        print(f"Calling {link}...")
        res = req.get(link, params=params)
        bucket = res.json()
        appeals_list += bucket["results"]
        link = bucket["next"]
        params = None
    
except req.exceptions.HTTPError as errh:
    print ("Http Error:",errh)
except req.exceptions.ConnectionError as errc:
    print ("Error Connecting:",errc)
except req.exceptions.Timeout as errt:
    print ("Timeout Error:",errt)
except req.exceptions.RequestException as err:
    print ("Oops: Something Else", err)
    
df = pd.DataFrame(appeals_list)
df.to_csv(f"doc_from_MDRBD003.csv")

