from memobase import MemoBaseClient, ChatBlob

PROJECT_URL = "http://localhost:8019"
PROJECT_TOKEN = "secret"

client = MemoBaseClient(
    project_url=PROJECT_URL,
    api_key=PROJECT_TOKEN,
)

assert client.ping(), "Your Memobase server is not running"

messages = [
    {
        "role": "user",
        "content": "Hello, I'm Gus",
    },
    {
        "role": "assistant",
        "content": "Hi, nice to meet you, Gus!",
    },
]

blob = ChatBlob(messages=messages)


uid = client.add_user()
u = client.get_user(uid)

bid = u.insert(blob)
print("User ID is", uid)
print("Blob ID is", bid)

print("Start processing...")
u.flush()

prompts = [m.describe for m in u.profile()]

print("Below is your profile:")
print("* " + "\n* ".join(sorted(prompts)))
