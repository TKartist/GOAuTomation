import tiktoken
import ast

def calculate_token_count(text_stream):
    encoder = tiktoken.get_encoding("cl100k_base")
    encoded_text = encoder.encode(text_stream)
    return len(encoded_text)

with open("output/MDRZW021.txt", "r") as f:
    text = f.read()
    f.close()


lists = ast.literal_eval(text)
count = 0
for list in lists:
    count += calculate_token_count(str(list))

print(count)
