import os
from text_extractor import organize_bucket, pdf_to_text
import ast
from openai_caller import conversation

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
        conversation(pages)

    except Exception as e:
        print(f"Found an error while loading {filename} to pass to OpenAI API:\n{e}")
        return

def main():
    '''
    Read documents from 'document_folder' and convert the pdf files to html
    proceed to organize them and store them in output folder
    '''
    if check_update():
        pdfs = os.listdir("document_folder")
        for pdf in pdfs:
            bucket = pdf_to_text(f"document_folder/{pdf}")
            clean_bucket = organize_bucket(bucket)
            with open(f"output/{pdf.split(".")[0]}.txt", "w") as f:
                f.write(str(clean_bucket))
                f.close()
        print("All PDF files are converted to coordinated texts and are stored in output")
    summarize("secret_info.txt")

if __name__ == "__main__":
    main()