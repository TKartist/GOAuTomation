import tiktoken
import ast
import os


def calculate_token_count(text_stream):
    encoder = tiktoken.get_encoding("cl100k_base")
    encoded_text = encoder.encode(text_stream)
    return len(encoded_text)



x = "123, [421, 11, 12, 41], 21, hello my friend go"
k = "123, 321"
l = ""
z = calculate_token_count(x)
print(z)
# l = os.listdir("output")
# for i in l:
#     with open(f"output/{i}", "r") as f:
#         text = f.read()
#         f.close()

#     lists = ast.literal_eval(text)
#     count = 0
#     for list in lists:
#         count += calculate_token_count(str(list))
#     if count > 100000:
#         print(i)
#         print(count)

