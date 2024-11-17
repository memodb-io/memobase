"""Using Mem0 0.1.2, https://github.com/mem0ai/mem0"""

import json
from typing import cast
from rich import print as pprint
from rich.progress import track
import tiktoken
from time import time, sleep
from mem0 import Memory


ENCODER = tiktoken.encoding_for_model("gpt-4o")
with open("./sharegpt_test_7uOhOjo.json") as f:
    data = json.load(f)


messages = [
    {"role": "user" if d["from"] == "human" else "assistant", "content": d["value"]}
    for d in data["conversations"]
]

m0 = Memory()

start = time()
for message in track(messages):
    m0.add([message], user_id="me_test")

print("Total time (seconds)", time() - start)
all_memos = m0.get_all(user_id="me_test")
print("- " + "\n- ".join([m["memory"] for m in all_memos]))
