import json
import ast
import pandas as pd


def quantitative_context_extraction():
    try:
        with open("output/sample.txt", "r") as f:
            text = f.read()
        f.close()
    except Exception as e:
        print("The error occured is: ", e)
        return
    
    text = text.split("Contact Information")[0].replace('\n', ' ')
    '''
    to avoid issues when checking a number, i am removing all ',' or '.' when reading
    the text
    '''

    list = []
    text = text.split(" ")
    r = len(text)
    print(r)
    cur = 0
    start = 0
    end = 0
    found = False
    distance = 5

    while cur < r:
        if found:
            if text[cur].replace(",", "").isdigit():
                end = cur
            elif cur - end > distance:
                found = False
                list.append(" ".join(text[max(start - distance, 0) : cur]))
        else:
            if text[cur].replace(",", "").isdigit():
                start = cur
                end = cur
                found = True
        cur += 1

    # restructure the output in the future
    word_length = 0
    for m in list:
        word_length += len(m.split(" "))
        # print(m)
    print(word_length)


def output_string_reader(path, output_file):
    text = ""
    try:
        with open(path, "r") as f:
            text = f.read()
            f.close()
    except Exception as e:
        print("Error found is ", e)
        return
    
    text = text.replace("```json", "").replace("```", "").replace("\n", " ")
    list_version = ast.literal_eval(text)
    json_objs = []
    for item in list_version:
        item = item.replace("\n", "")

        try:
            data = json.loads(item)
            json_objs.append(data)
        except Exception as e:
            print("Error parsing json: ", e)
            return
    
    df = pd.DataFrame(json_objs)
    df.to_csv(output_file)

