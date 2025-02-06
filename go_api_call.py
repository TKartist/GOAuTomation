import requests as req
import pandas as pd
from datetime import datetime

def collect_appeals_docs(gt_date):
    base_url = "https://goadmin.ifrc.org/"
    api_endpoint = "api/v2/appeal_document/"
    parameters = {"created_at__gt": gt_date}
    doc_list = []
    link = base_url + api_endpoint

    try:
        while link != None:
            print(f"Calling {link}...")
            res = req.get(link, params=parameters)
            bucket = res.json()
            doc_list += bucket["results"]
            link = bucket["next"]
            parameters = None
                

    except req.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except req.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except req.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except req.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
    
    to_save = {}

    # saves only the most recent documents of the appeal
    for doc in doc_list:
        if doc["appeal"]["code"] in to_save:
            if doc["created_at"] > to_save[doc["appeal"]["code"]]["created_at"]:
                to_save[doc["appeal"]["code"]] = doc
        else:
            to_save[doc["appeal"]["code"]] = doc
    
    concat_docs = []
    for val in to_save.values():
        concat_docs.append(val)
    
    df = pd.DataFrame(concat_docs)
    df.to_csv(f"docs_from_{gt_date.year}_{gt_date.month}_{gt_date.day}.csv")


def collect_appeals_pdf(title, link):
    try:
        res = req.get(link)
        if res.status_code == 200:
            with open(f"{title}.pdf", "wb") as f:
                f.write(res.content)
                f.close()
        else:
            print(f"Failed fetching the data from {link}: {res.status_code}")
    except Exception as e:
        print(f"Error found: ", e)
    


gt_date = datetime(2022, 1, 1, 0, 0, 0)
collect_appeals_docs(gt_date=gt_date)