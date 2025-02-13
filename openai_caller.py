import openai
from info_withdrawl import secret_extraction
import os


def collect_system_message(address):
    system_message = "You are a very helpful assistant"
    try:
        with open(address, "r") as f:
            system_message = f.read()
            f.close()
    except Exception as e:
        print("Error while reading the stored system message: ", e)
    return system_message



async def conversation(pages):
    system_message = " ".join(collect_system_message("system_message.txt").split("\n"))
    initial_iteration =  await call_openai(pages, system_message)
    system_message = f"{" ".join(collect_system_message("correcting_system_message.txt").split("\n"))}\n{initial_iteration}"
    new_iteration = await call_openai(pages, system_message)
    return new_iteration



async def call_openai(pages, system_message):
    secrets = secret_extraction()
    deployment_name = secrets["Deployment name"]

    messages = [
        {"role": "system", "content": system_message}
    ] + [{"role": "user", "content": str(page)} for page in pages] 

    messages.append({"role": "user", "content": "ALL GOOD, PLEASE ANSWER THE QUESTION"})

    async with openai.AsyncAzureOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        azure_endpoint="https://ifrcorg-go.openai.azure.com/",
        api_version="2024-10-21"
    ) as client:
        response = await client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            temperature=0.5
        )

    return response.choices[0].message.content
        


