from memobase import MemoBaseClient
from openai import OpenAI
from memobase.patch.openai import openai_memory

stream = True


# 1. Patch the OpenAI client to use MemoBase
client = OpenAI()
mb_client = MemoBaseClient(
    project_url="http://localhost:8019",
    api_key="secret",
)
client = openai_memory(client, mb_client)
# ------------------------------------------


def chat(message, close_session=False):
    # 2. Use OpenAI client as before 🚀
    r = client.chat.completions.create(
        messages=[
            {"role": "user", "content": message},
        ],
        model="gpt-4o",
        stream=stream,
        # 3. Add an unique user string here will trigger memory.
        # Comment this line and this call will just like a normal OpenAI ChatCompletion
        user_id="test",
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
        client.flush("test")


chat("I'm Gus, how are you?", close_session=True)
chat("What's my name?")

print(client.get_profile("test"))