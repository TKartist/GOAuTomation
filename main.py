import os
from text_extractor import organize_bucket, pdf_to_text

def main():
    '''
    Read documents from 'document_folder' and convert the pdf files to html
    proceed to organize them and store them in output folder
    '''
    pdfs = os.listdir("document_folder")
    for pdf in pdfs:
        bucket = pdf_to_text(f"document_folder/{pdf}")
        clean_bucket = organize_bucket(bucket)
        with open(f"output/{pdf.split(".")[0]}.txt", "w") as f:
            f.write(str(clean_bucket))
            f.close()
    print("All PDF files are converted to coordinated texts and are stored in output")
    

if __name__ == "__main__":
    main()