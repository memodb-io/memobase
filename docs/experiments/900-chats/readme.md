>  Use a 900~ turns of chats from ShareGPT dataset to evaulate MemoBase

## Setup

- We choose the longest chats from [ShareGPT dataset](https://huggingface.co/datasets/RyokoAI/ShareGPT52K/tree/main/old) (`sg_90k_part1.json`)
  - ID "7uOhOjo". Check the chats in this file: `./sharegpt_test_7uOhOjo.json`.

- Make sure you have [set up the MemoBase Backend](../../../src/server/readme.md)
- `pip install memobase rich`
- We use OpenAI **gpt-4o-mini** as default model, make sure you have a OpenAI key. Place it to `config.yaml`
- Run `python run.py`, it will take a while.
- For a reference, we also compare with a greate memory layer solution [mem0](https://github.com/mem0ai/mem0) (version 0.1.2), the code is `./run_mem0.py`, its default model is also gpt-4o-mini.
  - Welcome to raise issues about `run_mem0.py`, we write this script based on the [basic docs](https://docs.mem0.ai/open-source/quickstart) and maybe not the best practice. Nevertheless, we keep the process of MemoBase as basic as possible for a fair comparison.

- To simulate the real results, we pack one user+assistant chat as a turn to insert to both MemoBase and Mem0.



## How much will you cost?

- We use `tiktoken` to count tokens (model `gpt-4o`)
- Number of Raw Messages' tokens is 63736 

#### MemoBase

- MemoBase will cost:
  - #Input token: 220000~
  - #Output token: 15000~
- Based on the DashBoard results of OpenAI, a user of 900 turns of chat will cost you **0.042$**(llm)
- The whole insertion will spend **125 - 150  seconds** (3 tests)

#### Mem0

- Based on the DashBoard results of OpenAI, a user of 900 turns of chat will cost you **0.24$**(llm) + **<0.01$**(embedding)
- The whole insertion will spend **1683 seconds** (1 tests)



## Why

- Mem0 uses hot-path update, that means each update will trigger a memory flush. When using `Memory.add` of Mem0, you should manually manage how many data you should insert so that the memory flush won't happen too many times. MemoBase has a buffer zone to automatically manage your inserted data, so you don't need to worry about this.
  - This leads to Mem0 calls LLM much more than MemoBase, so it will be slower and cost more.
- Also, Mem0 computes embeddings for each memory and retrieve them on each time you insert, while MemoBase doesn't use embeddings for user memory. We use dynamic profiling to generate first and secondary index for users, when we retrieve memories for updating, we only use SQL.



## How will you get?

#### MemoBase

User profile is below (mask sensitive information as **):

```
* basic_info: language_spoken - User uses both English and Korean.
* basic_info: name - 오*영
* contact_info: email - s****2@cafe24corp.com
* demographics: marital_status - user is married
* education:  - User had an English teacher who emphasized capitalization...
```

You can view the full profile in [here](./full_memobase.txt)

Take a look at a more structured profiles:

```python
[
  UserProfile(
      updated_at=datetime.datetime(2024, 11, 16, 9, 10, 45, 554319),
      topic='demographics',
      sub_topic='marital_status',
      content='user is married',
      related_blob_ids=[
          'f948a3a4-8a0d-4258-bfe6-69e22d34f3ba',
          'd5723cdc-601e-4054-9ba5-891cba1b5adb',
          '3fc817be-4453-439e-965b-98974baf05d9'
      ]
  )
  ...
]
```

#### Mem0

We list some of the memories below(`Memory.get_all`):

```python
- The restaurant is awesome
- User is interested in the lyrics of 'Home Sweet Home' by Motley Crue
- In Korea, people use '^^' to express smile
- Reservation for a birthday party on March 22
- Did not decide the menu...
```

The full results is in [here](./full_mem0.txt).



## Does MemoBase hallucinate?

One thing is worse than no memory is wrong memory, we can't guarantee the absolute right of the profiles(because we rely on LLM), but MemoBase left a chance to correct it because we save links between a memory and its raw sources.

In the above section, MemoBase said the user is married, **but the words "married" or "marry" never occur in this dataset**. let's find out if MemoBase is hallucinating. We can output this profiles' related blobs, below is the three related blobs' messages:

---

- user: 1 / 1You can do well from now on, right?
- assistant: <div><p>As an AI language model, I don't have feelings, but I'm always ready to assist you with your questions and concerns. If you have any further questions, please feel free to ask!</p></div>
- user: 1 / 1[check this sentences]
  <i></i>
- assistant: <div><p>**As an AI language model, I cannot know your wife's personal preferences.** You would know better than anyone else whether or not your wife would enjoy the special decoration for her birthday party. However, it's a thoughtful gesture to arrange for a special decoration to make her birthday celebration more memorable.</p></div>
- user: 1 / 1[check my sentence]
- assistant: <div><p>The sentence is grammatically correct.</p></div>

---

Seem like this guy has a wife😂 and he/she does get married.
