import pdfplumber

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


pdf_path = 'document_folder/sample.pdf'
text = extract_text_from_pdf(pdf_path)


