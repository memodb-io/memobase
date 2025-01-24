"""Read the docs of how this patch works: https://docs.memobase.io/features/openai"""

from memobase import MemoBaseClient
from openai import OpenAI
from memobase.patch.openai import openai_memory
from time import sleep

stream = True
user_name = "test35"

# 1. Patch the OpenAI client to use MemoBase
client = OpenAI()
mb_client = MemoBaseClient(
    project_url="http://localhost:8019",
    api_key="secret",
)
client = openai_memory(client, mb_client)
# ------------------------------------------


def chat(message, close_session=False, use_users=True):
    print("Q: ", message)
    # 2. Use OpenAI client as before 🚀
    r = client.chat.completions.create(
        messages=[
            {"role": "user", "content": message},
        ],
        model="gpt-4o",
        stream=stream,
        # 3. Add an unique user string here will trigger memory.
        # Comment this line and this call will just like a normal OpenAI ChatCompletion
        user_id=user_name if use_users else None,
    )
    # Below is just displaying response from OpenAI
    if stream:
        for i in r:
            if not i.choices[0].delta.content:
                continue
            print(i.choices[0].delta.content, end="", flush=True)
        print()
    else:
        print(r.choices[0].message.content)

    # 4. Once the chat session is closed, remember to flush to keep memory updated.
    if close_session:
        sleep(0.1)  # Wait for the last message to be processed
        client.flush(user_name)


print("--------Use OpenAI without memory--------")
chat("I'm Gus, how are you?", use_users=False)
chat("What's my name?", use_users=False)

print("--------Use OpenAI with memory--------")
chat("I'm Gus, how are you?", close_session=True)
print("User Profiles:", [p.describe for p in client.get_profile(user_name)])
chat("What's my name?")
