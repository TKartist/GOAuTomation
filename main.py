import os
from text_extractor import organize_bucket, pdf_to_text
import ast
from openai_caller import conversation
import asyncio
import json
import pandas as pd


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
    

def check_update():
    pdfs = os.listdir("document_folder")
    texts = os.listdir("output")
    for i in range(len(pdfs)):
        if pdfs[i].split(".")[0] != texts[i].split(".")[0]:
            return True
    return False

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