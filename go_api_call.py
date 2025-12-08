import requests
import pandas as pd
import ast
from datetime import datetime
import os
from dotenv import load_dotenv

FINAL = "final"
CONTRIBUTIONS = "contributions"
DONOR = "donor"
base_url = "https://goadmin.ifrc.org"
load_dotenv()



def collect_dref_final_reports():
    GO_API_KEY = os.getenv("GO_API_KEY")
    headers = {
        "Authorization" : f"Token {GO_API_KEY}",
    }
    api_endpoint = "/api/v2/dref-final-report/"
    '''
        Refer to 'planned_interventions' key for specific details
    '''
    final_report_details = []
    link = base_url + api_endpoint
    try:
        while link != None:
            print(f"Calling {link}...")
            res = requests.get(link, headers=headers)
            if res.status_code == 200:
                bucket = res.json()
                temp = bucket["results"]
                for item in temp:
                    final_report_details.append({
                        "mdrcode" : item["appeal_code"],
                        "actions" : item["planned_interventions"]
                    })
                link = bucket["next"]
            else:
                print("Invalid response statuse code received: ", res.status_code)
                return
    
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)
    
    final_reports = pd.DataFrame(final_report_details)
    # final_reports.set_index("mdrcode", inplace=True)
    
    final_reports.to_csv("csv_files/final_report_details.csv", index=True)
    

# collect_dref_final_reports()


def collect_dref3():
    GO_API_KEY = os.getenv("GO_API_KEY")
    headers = {
        "Authorization" : f"Token {GO_API_KEY}",
    }
    api_endpoint = "/api/v2/dref3/"
    final_report_details = []
    link = base_url + api_endpoint
    try:
        while link != None:
            print(f"Calling {link}...")
            res = requests.get(link, headers=headers)
            if res.status_code == 200:
                bucket = res.json()
                final_report_details = bucket
                
                link = None
            else:
                print("Invalid response statuse code received: ", res.status_code)
                return
    
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)

    final_reports = pd.DataFrame(final_report_details)
    # final_reports.set_index("mdrcode", inplace=True)
    
    final_reports.to_csv("csv_files/dref3_data.csv", index=True)


def collect_appeals(gt_date, ls_date=None):
    api_endpoint = "/api/v2/appeal/"
    params = {
        "start_date__gt" : gt_date,
        "start_date__lt" : ls_date if ls_date else datetime.now()
    }
    appeals_list = []
    link = base_url + api_endpoint

    try:
        while link != None:
            print(f"Calling {link}...")
            res = requests.get(link, params=params)
            if res.status_code == 200:
                bucket = res.json()
                appeals_list += bucket["results"]
                link = bucket["next"]
                params = None
            else:
                print("Invalid response statuse code received: ", res.status_code)
                return
            
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)
    
    df = pd.DataFrame(appeals_list)
    df.set_index("code", inplace=True)
    df.to_csv(f"appeals_from_{gt_date.year}_{gt_date.month}_{gt_date.day}.csv")
    return df


def collect_all_appeals():
    api_endpoint = "/api/v2/appeal/"
    appeals_list = []
    link = base_url + api_endpoint

    try:
        while link != None:
            print(f"Calling {link}...")
            res = requests.get(link)
            if res.status_code == 200:
                bucket = res.json()
                appeals_list += bucket["results"]
                link = bucket["next"]
            else:
                print("Invalid response statuse code received: ", res.status_code)
                return
            
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)
    
    df = pd.DataFrame(appeals_list)
    df.set_index("code", inplace=True)
    df.to_csv(f"all_appeals.csv")
    return df

# collect_all_appeals()

def collect_appeals_docs(gt_date, ls_date=None):
    appeals_df = collect_appeals(gt_date, ls_date)
    api_endpoint = "/api/v2/appeal_document/"
    parameters = {"created_at__gt": gt_date}
    doc_list = []
    link = base_url + api_endpoint

    try:
        while link != None:
            print(f"Calling {link}...")
            res = requests.get(link, params=parameters)
            if res.status_code == 200:
                bucket = res.json()
                doc_list += bucket["results"]
                link = bucket["next"]
                parameters = None
            else:
                print("Invalid response statuse code received: ", res.status_code)
                return
            
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
    
    to_save = {}

    # saves most recent doc when
    for doc in doc_list:
        if doc["appeal"]["code"] not in appeals_df.index:
            continue
        if "type" in doc:
            desc = f"{doc["type"]} {doc["description"]} {doc["name"]}".lower()
        else:
            desc = f"{doc["description"]} {doc["name"]}".lower()

        if doc["appeal"]["code"] in to_save:
            if CONTRIBUTIONS not in desc and DONOR not in desc and doc["created_at"] >= to_save[doc["appeal"]["code"]]["created_at"]:
                to_save[doc["appeal"]["code"]] = doc
        else:
            to_save[doc["appeal"]["code"]] = doc
            

    concat_docs = []
    for val in to_save.values():
        concat_docs.append(val)
    
    df = pd.DataFrame(concat_docs)
    df = df.fillna("")
    df["code"] = df["appeal"].apply(lambda x: x["code"])
    df.set_index("code", inplace=True)
    doc_urls = df["document_url"]
    appeals_df["document_url"] = doc_urls
    appeals_df = appeals_df[["document_url"] + [col for col in appeals_df.columns if col != "document_url"]]
    appeals_df.to_excel(f"docs_from_{gt_date.year}_{gt_date.month}_{gt_date.day}.xlsx", index=True)


def collect_appeals_pdf(title, link):
    docs = os.listdir("document_folder")
    if f"{title}.pdf" in docs:
        return
    try:
        res = requests.get(link)
        if res.status_code == 200:
            with open(f"{title}.pdf", "wb") as f:
                f.write(res.content)
                f.close()
        else:
            print(f"Failed fetching the data from {link}: {res.status_code}")
    except Exception as e:
        print(f"Error found: ", e)

def main():
    year = 2022
    month = 7
    day = 1
    gt_date = datetime(year, month, day, 0, 0, 0)
    collect_appeals_docs(gt_date=gt_date)

    # df = pd.read_csv(f"docs_from_{year}_{month}_{day}.csv")
    # df = df.fillna("")
    # for _, row in df.iterrows():
    #     link = row["document_url"]
    #     title = ast.literal_eval(row["appeal"])["code"]
    #     if link == "":
    #         link = row["document"]
    #     collect_appeals_pdf(f"document_folder/{title}", link)
    

    


if __name__ == "__main__":
    main()

