'''
testing staged API endpoint
'''

import pandas as pd
import requests

url = "https://goadmin-stage.ifrc.org/api/v2/dref3/?offset=0&limit=50"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)
    print(len(df))
    print(df.head())
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")

df.to_csv("dref3_data_staged.csv", index=False)