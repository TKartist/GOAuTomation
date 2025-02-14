import pdfplumber
import fitz
import ast
import requests as req

def get_older_file(mdrcode, iteration):
    base_url = "https://goadmin.ifrc.org/"
    api_endpoint = "api/v2/appeal_document/"
    parameters = {"search": mdrcode}
    link = base_url + api_endpoint

    try:
        res = req.get(link, params=parameters)
        bucket = res.json()
        if iteration == (len(bucket) - 2):
            return []
        doc_ele = bucket["results"][:- iteration]
        doc_link = ""
        if "document" in doc_ele:
            doc_link += doc_ele["document"]
        if "document_url" in doc_ele:
            doc_link += doc_ele["document_url"]
        res = req.get(link)
        if res.status_code == 200:
            with open(f"document_folder/{mdrcode}.pdf", "wb") as f:
                f.write(res.content)
                f.close()
            doc = fitz.open(f"document_folder/{mdrcode}.pdf")
        else:
            print(f"Failed fetching the data from {link}: {res.status_code}")
            doc = get_older_file(mdrcode, iteration + 1)
    except Exception as e:
        print(e)
        doc = get_older_file(mdrcode, iteration + 1)
    return doc
    
''''''

def extract_text_from_pdf(pdf_path):
    text = ''
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            pdf.close()

        with open('output/sample.txt', 'w') as f:
            f.write(text)
            f.close()
    except Exception as e:
        print("Error occured: ", e)
    return text

''''''

def pdf_to_text(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"Error loading {pdf_path}: {e}")
        doc = get_older_file(pdf_path.split("/")[1].split(".")[0], 1)
    
    bucket = []
    for page_num, page in enumerate(doc):

        for word in page.get_text("words"):
            x0, y0, x1, y1, text = word[:5]
            bucket.append([page_num, int(x0), int(y0), int(x1) - int(x0), int(y1) - int(y0), text])
    doc.close()
    return bucket


'''
idea is that I merge the elements which have the same y0 position (same line) and same height
honestly i don't see the point of width as long as we have the starting position so I am going
to probably delete the widths. Then store the list of starting positions and merge the strings of
matching height and y0 positional value; it should significantly reduce unnecessary information
'''

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



