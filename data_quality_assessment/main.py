import pandas as pd
import requests
import endpoints as ep
import semantic_validity as sv
import os
from dotenv import load_dotenv

def collecting_data(endpoint, headers):
    print(ep.ROOT)
    print(endpoint)
    url = ep.ROOT + endpoint
    dataset = []

    while url:
        try:
            print(f"Reading {url}")
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                bucket = response.json()
                dataset.extend(bucket["results"])
                # url = None
                url = bucket["next"]
            else:
                print("Invalid response statuse code received: ", response.status_code)
                return
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("Oops: Something Else", err)

    return dataset

def collecting_data_public(endpoint):
    return collecting_data(endpoint, None)

def collecting_data_private(endpoint):
    load_dotenv()
    GO_API_KEY = os.getenv("GO_API_KEY")
    headers = {
        "Authorization" : f"Token {GO_API_KEY}",
    }
    print(GO_API_KEY)
    return collecting_data(endpoint, headers)


def appeals_check(df):
    # Convert string datetime format to datetime objects for semantics check
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    df["modified_at"] = pd.to_datetime(df["modified_at"], errors="coerce")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    
    sv.date_semantics_check(df.copy())
    sv.numerical_semantics_check(df.copy())
    sv.unique_value_check(df.copy(), "aid")
    sv.unique_value_check(df.copy(), "id")
    sv.count_active(df.copy())
    
    dref3 = pd.read_csv("data/dref3_all_records.csv")
    sv.duplicate_operations(df.copy(), dref3)

def main():
    endpoint_name = input("Please enter the endpoint name you wish to test: ")
    endpoint_metadata = ep.ENDPOINT.get(endpoint_name)
    
    if endpoint_metadata is None:
        print(f"{endpoint_name} not found in endpoints.py file, please enter the metadata to the file and try again.")
    
    data_files = os.listdir("data")
    filename = endpoint_metadata.get("file_location", "")
    
    if endpoint_metadata.get("file_location", "") in data_files:
        print("Data already exists in the directory. Starting general test...")
        df = pd.read_csv(f"data/{filename}")
    else:
        target = endpoint_metadata.get("endpoint", "")
        if target != "":
            print(f"Collecting data from the {ep.ROOT}{target}...")
        else:
            print(f"Endpoint address missing for {endpoint_name}")
            return
        dataset = collecting_data_public(target) if endpoint_metadata.get("public", "False") else collecting_data_private(target)
        df = pd.DataFrame(dataset)
        df.to_csv(f"data/{filename}")
    
    if endpoint_name == "appeal":
        appeals_check(df)
    # appeals_check(df)
    

    


if __name__ == "__main__":
    main()

