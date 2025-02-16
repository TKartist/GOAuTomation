import ast
import json
import pandas as pd


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

df = pd.read_csv("csv_files/first_batch.csv")
df_1 = pd.read_csv("csv_files/second_batch.csv")
df_2 = pd.concat([df, df_1], ignore_index=True)
df_2.to_csv("csv_files/concat_batch.csv", index=False)