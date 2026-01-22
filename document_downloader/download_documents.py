import requests
import pandas as pd
from datetime import datetime, timezone
import os

# To see what parameters can be used, refer to: https://goadmin.ifrc.org/api-docs/swagger-ui/#/api/api_v2_appeal_list
appeal_parameter = {
    "start_date__gte" : datetime(2025, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
}

# Filtering the dataset after fetching. "column_name" : "value"
appeal_filter = {}

appeals_endpoint = "https://goadmin.ifrc.org/api/v2/appeal/"
doc_link_endpoint = "https://goadmin.ifrc.org/api/v2/appeal_document/"


def get_appeals():
    with requests.Session() as session:
        res = session.get(appeals_endpoint, params=appeal_parameter)
        if res.status_code == 200:
            appeals = res.json()["results"]
            appeals_df = pd.DataFrame(appeals)
            while res.json().get("next"):
                print(res.json().get("next"))
                res = session.get(res.json().get("next"))
                appeals = res.json()["results"]
                appeals_df = pd.concat([appeals_df, pd.DataFrame(appeals)], ignore_index=True)
            for key, value in appeal_filter.items():
                appeals_df = appeals_df[appeals_df[key] == value]
            return appeals_df
        else:
            print(f"Failed to fetch appeals: {res.status_code}")
            return pd.DataFrame()


def get_document_links(appeals_df):
    appeal_ids = appeals_df["id"].tolist()
    docs = []
    with requests.Session() as session:
        for appeal_id in appeal_ids:
            params = {"appeal": appeal_id}
            res = session.get(doc_link_endpoint, params=params)
            if res.status_code == 200:
                docs.extend(res.json()["results"])
            else:
                print(f"Failed to fetch documents for appeal ID {appeal_id}: {res.status_code}")
    
    docs_df = pd.DataFrame(docs)
    docs_df["code"] = docs_df["appeal"].apply(lambda x: x["code"])
    docs_df["start_date"] = docs_df["appeal"].apply(lambda x: x["start_date"])
    docs_df = docs_df[docs_df["type"].str.contains("DREF", na=False)]
    docs_df = docs_df[["code", "type", "start_date", "description", "document_url"]]
    return docs_df


def download_document(url, save_path):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(res.content)
            print(f"Downloaded document from {url} to {save_path}")
        else:
            print(f"Failed to download document from {url}: {res.status_code}")
    except Exception as e:
        print(f"Error downloading document from {url}: {e}")

def main():
    print("Downloading documents from GO API...")
    appeals = get_appeals()
    appeals = appeals[appeals["atype_display"] == "DREF"]
    appeals.to_csv("fetched_appeals.csv", index=False)
    if appeals.empty:
        print("No appeals found with the specified parameters.")
        return
    documents = get_document_links(appeals)
    if documents.empty:
        print("No documents found for the fetched appeals.")
        return
    documents.to_csv("appeal_documents.csv", index=False)
    dirs = os.listdir("./")
    if "documents" not in dirs:
        os.mkdir("documents")
    for _, row in documents.iterrows():
        title = f"{row['code']}_{row['type'].replace(' ', '_')}.pdf"
        download_document(row["document_url"], f"documents/{title}")

    

    


if __name__ == "__main__":
    main()