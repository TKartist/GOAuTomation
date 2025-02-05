import openai
from info_withdrawl import secret_extraction
import os

def ask_azure_openai(prompt, secrets):
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
        temperature=0.1
    )
    return response["choices"][0]["message"]["content"]


secrets = secret_extraction()
response = ask_azure_openai("How are you doing?", secrets)
print(response)