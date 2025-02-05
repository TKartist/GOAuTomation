import openai
from info_withdrawl import secret_extraction
import os


def collect_system_message():
    system_message = "You are a very helpful assistant"
    try:
        with open("system_message.txt", "r") as f:
            system_message = f.read()
            f.close()
    except Exception as e:
        print("Error while reading the stored system message: ", e)
    return system_message
        


def asking_openai(prompt, secrets):
    openai.api_type = "azure"

    # Azure OpenAI endpoint
    openai.api_base = secrets["Target URI"]

    # Use environment variables for security
    openai.api_key = os.environ.get("OPENAI_API_KEY")  
    openai.api_version = secrets["Model version"] 
    # Deployment name
    deployment_name = secrets["Deployment name"]
    """Send a prompt to Azure OpenAI ChatGPT API"""
    response = openai.ChatCompletion.create(
        engine=deployment_name,  
        messages=[
            {"role": "system", "content": "you are a helpful assistant"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        # temperature decides whether if the response is more literal or creative
        # lower is more literal, and higher is more creative answer
        # some contexts may require derivation so I chose the middle value
        temperature=0.5 
    )
    return response["choices"][0]["message"]["content"]

def request_answer():
    return ""


def conversation(pages):
    system_message = collect_system_message()
    for page in pages:
        asking_openai(str(page), secrets)
    response = request_answer()
    return response
        


secrets = secret_extraction()
