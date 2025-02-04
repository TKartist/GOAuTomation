import tiktoken
import ast

def calculate_token_count(text_stream):
    encoder = tiktoken.get_encoding("cl100k_base")
    encoded_text = encoder.encode(text_stream)
    print(f"Token count: {len(encoded_text)}")

with open("output/MDR43005fr.txt", "r") as f:
    text = f.read()
    f.close()


lists = ast.literal_eval(text)
page = 1
for list in lists:
    print(f"Page : {page}")
    calculate_token_count(str(list))
    page += 1
