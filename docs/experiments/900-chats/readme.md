>  Use a 900~ turns of chats from ShareGPT dataset to evaulate MemoBase

## Setup

- [ShareGPT dataset](https://huggingface.co/datasets/RyokoAI/ShareGPT52K/tree/main/old) `sg_90k_part1.json`, ID "7uOhOjo". Process to `./sharegpt_test_7uOhOjo.json`.
- Make sure you have [set up the MemoBase Backend](../../../src/server/readme.md)
- `pip install memobase rich`
- We use OpenAI **gpt-4o** as default model, make sure you have a OpenAI key. Place it to `config.yaml`
- Run `python run.py`, it will take a while.



## How much will you cost?

- We use tiktoken to count tokens (model `gpt-4o`)
- Number of Raw Messages' tokens is 63736 
- MemoBase will cost (in one test, may diff from your tests):
  - **#Input token: 202217**, ~3.3:1 to the raw input tokens. (<< mem0)
  - **#Output token: 7517**
- Based on the latest [pricing](https://openai.com/api/pricing/) of OpenAI, a user of 900 turns of chat will cost you 0.6$~. (*No counting Cached input or Batch API*)
- The whole insertion will spend 125 - 150  seconds (3 tests) (<< mem0)



## How will you get?

User profile is below (mask sensitive information as **):

```
* basic_info: language_spoken - User uses both English and Korean.
* basic_info: name - 오*영
* contact_info: email - s****2@cafe24corp.com
* demographics: marital_status - user is married
* education:  - User had an English teacher who emphasized capitalization...
```

You can view the full profile in [here](./full_profile.txt)

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

Wait, MemoBase said the user is married, **but the words married or marry never occur in the dataset**. let's find out if MemoBase is hallucinating. We can output this profiles' related blobs, below is the three related blobs' messages:

---

- user: 1 / 1You can do well from now on, right?
- assistant: <div><p>As an AI language model, I don't have feelings, but I'm always ready to assist you with your questions and concerns. If you have any further questions, please feel free to ask!</p></div>
- user: 1 / 1[check this sentences]
  <i></i>
- assistant: <div><p>**As an AI language model, I cannot know your wife's personal preferences.** You would know better than anyone else whether or not your wife would enjoy the special decoration for her birthday party. However, it's a thoughtful gesture to arrange for a special decoration to make her birthday celebration more memorable.</p></div>
- user: 1 / 1[check my sentence]
- assistant: <div><p>The sentence is grammatically correct.</p></div>

---

Sseem like this guy has a wife😂