import pdfplumber
import fitz
import ast

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


def pdf_to_text(pdf_path):
    doc = fitz.open(pdf_path)
    bucket = []
    pprev, prev, bucket = "", "", []
    
    for page_num, page in enumerate(doc):

        for word in page.get_text("words"):
            x0, y0, x1, y1, text = word[:5]
            bucket.append([page_num, int(x0), int(y0), int(x1) - int(x0), int(y1) - int(y0), text])
            if f"{prev} {text}" == "Contact Information" or f"{pprev} {prev} {text}" == "How we work":
                doc.close()
                return bucket[:-3]        
            pprev = prev
            prev = text
    doc.close()
    return bucket


'''
idea is that I merge the elements which have the same y0 position (same line) and same height
honestly i don't see the point of width as long as we have the starting position so I am going
to probably delete the widths. Then store the list of starting positions and merge the strings of
matching height and y0 positional value; it should significantly reduce unnecessary information
'''

def organize_bucket(bucket):
    cur_y0, p, l, new_bucket, page = 0, 0, len(bucket), [[]], 0
    while (p < l):
        if cur_y0 != bucket[p][2]:
            if page != bucket[p][0]:
                new_bucket.append([])
                page = bucket[p][0]
            new_bucket[page].append([[bucket[p][1]], bucket[p][2],bucket[p][4], bucket[p][5]])
            cur_y0 = bucket[p][2]
        else:
            new_bucket[page][-1][0].append(bucket[p][1])
            new_bucket[page][-1][-1] += f" {bucket[p][-1]}"
        p += 1
    return new_bucket



