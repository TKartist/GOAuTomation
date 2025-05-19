import os
# from text_extractor import organize_bucket, pdf_to_text
import ast
from openai_caller import conversation
import asyncio
import json
import pandas as pd
import fitz



def pdf_to_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error loading {pdf_path}: {e}")
        # doc = get_older_file(pdf_path.split("/")[1].split(".")[0], 1)
    
    bucket = []
    for page_num, page in enumerate(doc):

        for word in page.get_text("words"):
            x0, y0, x1, y1, text = word[:5]
            bucket.append([page_num, int(x0), int(y0), int(x1) - int(x0), int(y1) - int(y0), text])
    
    return bucket

def organize_bucket(bucket):
    cur_y0, p, l, page = 0, 0, len(bucket), 0
    pages = bucket[l - 1][0]
    new_bucket = [[] for _ in range(pages + 1)]
    while (p < l):
        if cur_y0 != bucket[p][2]:
            if page != bucket[p][0]:
                page = bucket[p][0]
            new_bucket[page].append([[bucket[p][1]], bucket[p][2],bucket[p][4], bucket[p][5]])
            cur_y0 = bucket[p][2]
        else:
            new_bucket[page][-1][0].append(bucket[p][1])
            new_bucket[page][-1][-1] += f" {bucket[p][-1]}"
        p += 1
    return new_bucket


def convert_pdf_to_text():
    pdf_list = os.listdir("document_folder")
    txt_list = os.listdir("output2")
    for pdf in pdf_list:
        if f"{pdf.split(".")[0]}.txt" in txt_list:
            continue
        bucket = pdf_to_text(f"document_folder/{pdf}")
        if bucket == []:
            continue
        new_bucket = organize_bucket(bucket)
        filename = pdf.split(".")[0]
        with open(f"output/{filename}.txt", "w") as f:
            f.write(str(new_bucket))
            f.close()
    print("Completed Conversion to Text Files")
    

# def check_update():
#     pdfs = os.listdir("document_folder")
#     texts = os.listdir("output")
#     for i in range(len(pdfs)):
#         if pdfs[i].split(".")[0] != texts[i].split(".")[0]:
#             return True
#     return False

def summarize(filename):
    try:
        with open(filename, "r") as f:
            text = f.read()
            f.close()
        pages = ast.literal_eval(text)
    except Exception as e:
        print(f"Found an error while loading {filename} to pass to OpenAI API:\n{e}")
        return
    doc_summary = asyncio.get_event_loop().run_until_complete(conversation(pages))
    return doc_summary


def main():
    '''
    Read documents from 'document_folder' and convert the pdf files to html
    proceed to organize them and store them in output folder
    '''
    convert_pdf_to_text()
    files = os.listdir("output")
    outputs = []
    for file in files:
        outputs.append(summarize(f"output/{file}"))
    with open("output_files/summary_file.txt", "w") as f:
        f.write(str(outputs))
        f.close()
    print("ALL FILES SUMMARIZED")

if __name__ == "__main__":
    main()