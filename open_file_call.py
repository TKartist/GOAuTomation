import requests
from info_withdrawl import secret_extraction
import os

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
