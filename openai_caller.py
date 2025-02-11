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
        

async def conversation(pages):
    system_message = " ".join(collect_system_message().split("\n"))
    secrets = secret_extraction()
    prompt = [{
        "role" : "system",
        "content" : system_message
    }]
    deployment_name = secrets["Deployment name"]
    client = openai.AsyncAzureOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        azure_endpoint="https://ifrcorg-go.openai.azure.com/",
        api_version="2024-10-21"
    )
    for page in pages:
        prompt.append({
            "role" : "user",
            "content" : str(page)
        })
    prompt.append({
        "role" : "user",
        "content" : "ALL GOOD, PLEASE ANSWER THE QUESTION"
    })
    response = await client.chat.completions.create(
        model=deployment_name,
        messages=prompt,
        temperature=0.5
    )
    out = response.choices[0].message.content
    return out
        


