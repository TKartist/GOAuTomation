from openai import OpenAI, AsyncOpenAI
import os

# send asynchronous request for response to OpenAI API
async def file_parse_prompt(long_stream, model="gpt-4o"):
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    stream_length = len(long_stream)
    call_count = stream_length % 2048
    if stream_length % 2048 != 0:
        call_count += 1
    prompt_list = [{
        "role" : "system",
        "content" : "You are a helpful assistant" # TO BE EDITED
    }]

    for i in range(call_count):
        prompt_list.append({
            "role": "user",
            "content" : long_stream[i * 2048 : min((i + 1) * 2048, stream_length)],
        })
    prompt_list.append({
        "role" : "user",
        "content" : "All good, please compile"
    })

    gpt_response = await client.chat.completions.create(
        messages=prompt_list,
        model="gpt-4o",
        temperature=1
    )

    gpt_response = gpt_response.choices[0].message.content
    return gpt_response