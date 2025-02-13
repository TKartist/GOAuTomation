import requests as req
import pandas as pd
import ast
from datetime import datetime
import os

z = os.listdir("document_folder")
print(len(z))
# FINAL = "final"

# def collect_appeals_docs(gt_date):
#     base_url = "https://goadmin.ifrc.org/"
#     api_endpoint = "api/v2/appeal/"
#     parameters = {"start_date__gt": gt_date}
#     doc_list = []
#     link = base_url + api_endpoint

#     try:
#         while link != None:
#             print(f"Calling {link}...")
#             res = req.get(link, params=parameters)
#             bucket = res.json()
#             doc_list += bucket["results"]
#             link = bucket["next"]
#             parameters = None
                

#     except req.exceptions.HTTPError as errh:
#         print ("Http Error:",errh)
#     except req.exceptions.ConnectionError as errc:
#         print ("Error Connecting:",errc)
#     except req.exceptions.Timeout as errt:
#         print ("Timeout Error:",errt)
#     except req.exceptions.RequestException as err:
#         print ("OOps: Something Else", err)
#     df = pd.DataFrame(doc_list)
#     df.set_index("code", inplace=True)
#     df.to_csv("appeals.csv")
    
    
    
# year = 2025
# month = 1
# day = 1
# gt_date = datetime(year, month, day, 0, 0, 0)
# collect_appeals_docs(gt_date=gt_date)