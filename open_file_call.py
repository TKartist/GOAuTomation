import requests
from info_withdrawl import secret_extraction
import os
from dotenv import load_dotenv, set_key

# using requests to openai due to connection with azure
AZURE_ENDPOINT = "https://ifrc-go.openai.azure.com"
API_KEY = os.environ.get("OPENAI_API_KEY")


headers = {
    "Authorization": f"Bearer {API_KEY}",
    "api-version": "2024-08-01-preview"
}

def collect_assistant_message():
    assistant_message = "You are an AI assistant specialized in processing PDF documents."
    try:
        with open("assistant_msg.txt", "r") as f:
            assistant_message = f.read()
            f.close()
    except Exception as e:
        print("Error while reading the stored assistant message: ", e)
    return assistant_message

def openai_file_upload(address):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "api-version": "2024-08-01-preview"
    }

    files = {
        "file" : open(address, "rb")
    }

    response = requests.post(
        f"{AZURE_ENDPOINT}/openai/files",
        headers=headers,
        files=files,
        params = {"purpose" : "assistants"}
    )

    file_id = response.json().get("id")

    return file_id

def delete_file(file_id):
    response = requests.delete(
        f"{AZURE_ENDPOINT}/openai/files/{file_id}",
        headers=headers
    )

    if response.status_code == 204:
        print("File deleted successfully")
    else:
        print(f"Failed to delete file. status code : {response.status_code}, message: {response.text}")


def create_assistant():
    secrets = secret_extraction()

    assistant_payload = {
        "name" : "PDF Information Extractor",
        "instruction" : collect_assistant_message,
        "model" : secrets["Deployment name"],
        "tools" : [{"type" : "code_interpreter"}]
    }
    response = requests.post(
        f"{AZURE_ENDPOINT}/openai/assistants",
        headers=headers,
        json=assistant_payload
    )

    assistant_id = response.json().get("id")
    return assistant_id

def run_openai_thread(file_id, assistant_id):
    response = requests.post(
        f"{AZURE_ENDPOINT}/openai/threads",
        headers=headers
    )
    thread_id = response.json().get("id")

    message_payload = {
        "role" : "user",
        "content" : "Extract key information from this PDF",
        "file_ids" : [file_id]
    }

    requests.post(
        f"{AZURE_ENDPOINT}/openai/threads/{thread_id}/message",
        headers=headers, 
        json=message_payload
    )

    run_payload = {"assistant_id" : assistant_id}
    run_response = requests.post(
        f"{AZURE_ENDPOINT}/openai/threads/{thread_id}/runs",
        headers=headers,
        json=run_payload
    )

    run_id = run_response.json().get("id")
    print("Processing request...")
    return run_id


def upload_all_files():
    files = os.listdir("document_folder")
    for file in files:
        filename = f"document_folder/{file}"
        openai_file_upload(filename)
    print("upload completed")


def get_files():
    response = requests.get(
        f"{AZURE_ENDPOINT}/openai/files",
        headers=headers
    )
    file_ids = []
    if response.status_code == 200:
        files = response.json().get("data", [])
        if files:
            print("Uploaded files:")
            for file in files:
                file_ids.append(file["id"])
    else:
        print(f"Failed fetching files. Status code: {response.status_code}. Message: {response.text}")


def delete_file_all():
    file_ids = get_files()
    for file_id in file_ids:
        delete_file(file_id)
    print("All files deleted")


def compile_openai_request():
    load_dotenv()
    assistant_id = os.getenv("ASSISTANT_ID")
    if assistant_id is None:
        assistant_id = create_assistant()
        set_key(".env", "ASSISTANT_ID", assistant_id)
    
    
    

