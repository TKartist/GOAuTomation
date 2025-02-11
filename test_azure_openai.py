import os
from pathlib import Path 
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    azure_endpoint="https://ifrcorg-go.openai.azure.com/",
    api_version="2024-10-21"
)


assistant = client.beta.assistants.create(
    name="Data Extractor",
    instructions=f"You are a helpful AI assistant who extracts information." 
    f"You have access to a sandboxed environment for writing and testing code."
    f"When you are asked to create a visualization you should follow these steps:"
    f"1. Write the code."
    f"2. Anytime you write new code display a preview of the code to show your work."
    f"3. Run the code to confirm that it runs."
    f"4. If the code is successful display the visualization."
    f"5. If the code is unsuccessful display the error message and try to revise the code and rerun going through the steps from above again.",
    tools=[],
    model="gpt-4-1106-preview" #You must replace this value with the deployment name for your model.
)
print(x)