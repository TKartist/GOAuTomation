import openai
import os
import pandas as pd
import asyncio
import json
import time
# df = pd.read_csv("../captions_collected.csv")
# df = df.dropna(subset=['project_title'])

# captions = df['captions'].tolist()

def secret_extraction():
    dict = {}
    try:
        with open("../secret_info.txt", "r") as f:
            secrets = f.read().split("\n")
            for secret in secrets:
                key_val = secret.split(":")
                dict[key_val[0]] = ":".join(key_val[1:])
            f.close()
    except Exception as e:
        print("Error Occured: ", e)
    return dict

async def openai_extract_call(openai_api_key, secrets, content):
    deployment_name = secrets["Deployment name"]
    system_message = "You are a helpful assistant that extracts the main content from YouTube video captions. Please summarize the provided content in a concise manner."
    with open("system_message.txt", "r") as file:
        system_message = file.read()
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": content}
    ]
    try:
        async with openai.AsyncAzureOpenAI(
            api_key=openai_api_key,
            azure_endpoint=secrets["Target URI"],
            api_version="2025-01-01-preview"
        ) as client:
            response = await client.chat.completions.create(
                model=deployment_name,
                messages=messages,
                temperature=0.2
            )
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        message = {
            "Project Title": "Error due to API call failure",
            "Project Summary": "Error due to API call failure",
            "Sustainable Development Goal": "Error due to API call failure"
        }
        return json.dumps(message)
    return response.choices[0].message.content

if __name__ == "__main__":
    api_key = os.environ.get("OPENAI_API_KEY")
    df = pd.read_csv("../captions_collected.csv")
    df = df.dropna(subset=['project_title'])

    captions = df['captions'].tolist()  # Limit to first 10 captions for testing
    secrets = secret_extraction()
    title = []
    summary = []
    sdg = []

    for caption in captions:
        if caption == "No Caption Available" or caption == "No Video Available":
            title.append("No Title Available")
            summary.append("No Summary Available")
            sdg.append("No SDG Available")
            continue
        result = asyncio.run(openai_extract_call(api_key, secrets, caption))
        time.sleep(1)
        print("Caption:", caption)
        print("Extracted Summary:", result)
        print("===================================================================")
        output = json.loads(result)
        title.append(output.get("Project Title", "Title Not Given"))
        summary.append(output.get("Project Summary", "Summary Not Given"))
        sdg.append(output.get("Sustainable Development Goal", "SDG Not Given"))
    
    df['project_title'] = title
    df['project_summary'] = summary
    df['main_sdg'] = sdg
    df.to_csv("../captions_collected_with_summary.csv", index=False)

