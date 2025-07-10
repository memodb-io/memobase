<div align="center">
    <a href="https://memobase.io">
    <picture>
      <img alt="Shows the Memobase logo" src="./assets/images/logo.png" width="80%">
    </picture>
  </a>
  <h1>Memobase</h1>
  <p>
    <a href="https://pypi.org/project/memobase/">
      <img src="https://img.shields.io/pypi/v/memobase.svg">
    </a>
    <a href="https://www.npmjs.com/package/@memobase/memobase">
      <img src="https://img.shields.io/npm/v/@memobase/memobase.svg?logo=npm&logoColor=fff&style=flat&labelColor=2C2C2C&color=28CF8D">
    </a>
    <a href="https://jsr.io/@memobase/memobase">
      <img src="https://img.shields.io/jsr/v/@memobase/memobase.svg?logo=jsr&logoColor=fff&style=flat&labelColor=2C2C2C&color=28CF8D" />
    </a>
    <a href="https://pkg.go.dev/github.com/memodb-io/memobase/src/client/memobase-go">
      <img src="https://img.shields.io/badge/go-reference-blue?logo=go&logoColor=fff&style=flat&labelColor=2C2C2C&color=28CF8D" />
    </a>
    <a href="./src/mcp">
       <img src="https://img.shields.io/badge/MCP-Memobase-green">
    </a>
  </p>
  <p>
    <a href="https://github.com/memodb-io/memobase/actions/workflows/publish.yaml">
      <img src="https://github.com/memodb-io/memobase/actions/workflows/publish.yaml/badge.svg">
    </a>
        <a href="https://github.com/orgs/memodb-io/packages?repo_name=memobase">
    <img src="https://img.shields.io/github/v/tag/memodb-io/memobase">
    </a>
  </p>
  <p>
    <a href="https://app.memobase.io/playground">
       <img src="https://img.shields.io/badge/Memobase-Playground-blue">
    </a>
    <a href="https://discord.gg/YdgwU4d9NB">
      <img src="https://dcbadge.limes.pink/api/server/YdgwU4d9NB?style=flat">
    </a>
    <a href="https://github.com/memodb-io/memobase/issues/61">
       <img src="https://img.shields.io/badge/群聊-wechat-green">
    </a>
  </p>
</div>








Memobase is a **user profile-based memory system** designed to bring long-term user memory to your Generative AI (GenAI) applications. Whether you're building virtual companions, educational tools, or personalized assistants, Memobase empowers your AI to **remember**,  **understand**, and **evolve** with your users.



Memobase can provide you structured profiles of users, check out the [result](./docs/experiments/900-chats/readme.md) (compared with [mem0](https://github.com/mem0ai/mem0)) from a 900-turns real-world chatting:



<details>
<summary>Partial Profile Output</summary>



```python
{
  "basic_info": {
    "language_spoken": ["English", "Korean"],
    "name": "오*영"
  },
  "demographics": {
    "marital_status": "married"
  },
  "education": {
    "notes": "Had an English teacher who emphasized capitalization rules during school days",
    "major": "국어국문학과 (Korean Language and Literature)"
  },
  "interest": {
    "games": 'User is interested in Cyberpunk 2077 and wants to create a game better than it',
    'youtube_channels': "Kurzgesagt",
    ...
  },
  "psychological": {...},
  'work': {'working_industry': ..., 'title': ..., },
  ...
}
```

</details>



## Table of Contents

- [Table of Contents](#table-of-contents)
- [Core Features](#core-features)
- [Get Started](#get-started)
- [Step-by-step break down](#step-by-step-break-down)
  - [1. Make sure you're connected](#1-make-sure-youre-connected)
  - [2. Manage Users](#2-manage-users)
  - [3. Insert Data](#3-insert-data)
  - [4. Get your Memory](#4-get-your-memory)
  - [5. Integrate memory into your prompt](#5-integrate-memory-into-your-prompt)
- [What's next?](#whats-next)
- [Why/Where should I use Memobase?](#whywhere-should-i-use-memobase)
  - [Remember the users](#remember-the-users)
  - [User analysis and tracking](#user-analysis-and-tracking)
  - [Sell something to your customers.](#sell-something-to-your-customers)
- [Documentation](#documentation)
- [Stay Updated](#stay-updated)
- [Support](#support)
- [Contribute](#contribute)
- [License](#license)

## Core Features

**🎯 Memory for User, not Agent**

Define and control exactly what user information your AI captures. 

📈 **SOTA**

check out performance on [public benchmark](./docs/experiments/locomo-benchmark) against mem0, langmem, zep...

📅 **Time-aware Memory**

Memobase has more than user profiles, it also records [user event](https://docs.memobase.io/features/event/event). User event is essiential to answer time-related question, see how we can [improve temporal memory much better](./docs/experiments/locomo-benchmark/README.md#Result) than other memory solutions.

**🖼️ Contorllable Memory**

Among all types of memory, only some may enhance your product experience. Memobase offers a flexible configuration for you to [design the profile](https://docs.memobase.io/features/profile/profile).

**🔌 Easy Integration**

Minimal code changes to integrate with your existing LLM stack with [API](https://docs.memobase.io/api-reference/overview), [Python](https://pypi.org/project/memobase/)/[Node](./src/client/memobase-ts/README.md)/[Go](./src/client/memobase-go/README.md) SDK.

**⚡️ Batch-Process**:

Memobase offers every user a buffer to batch processing the chats after the conversation. Fast & Cheap.

**🚀 Production Ready**

Memobase is building with FastAPI, Postgres and Redis, supporting request caching, authing, telemetry... [Fully dockerized](./src/server/readme.md).



<div align="center">
    <picture>
      <img alt="Shows the Memobase Workflow" src="./assets/images/starter.png" width="80%">
    </picture>
  <p>How Memobase works?</p>
</div>




## Get Started

> [!NOTE]
>
> Try [Memobase Playground](https://app.memobase.io/playground) to see how profile-based memory works — no setup needed.
> * **Visualize** how user profiles and memory events evolve over time.
> * **Interact** with the memory mechanism directly.
> * **Explore** key features and concepts in a live environment.
> Watch the demo below — see how memory evolves around user profiles.

https://github.com/user-attachments/assets/eb2eea30-48bc-4714-9706-e417ae1931df




1. [Start your Memobase server locally](./src/server/readme.md). If you don't want to be bothered, Memobase Cloud provides [a free tier](https://www.memobase.io/en/login) enough for your testing
2. You should have the below two things to continue:
   1. A project url. (local: `http://localhost:8019` , cloud `https://api.memobase.dev`)
   2. A project token. (local: `secret` , cloud `sk-proj-xxxxxx`)
3. Install the Python SDK: `pip install memobase`
4. Below tutorial is for Python User. For other language and API, check [this](https://docs.memobase.io/quickstart).



## Step-by-step break down

> [!TIP]
>
> - You can just run this equivalent [quickstart script](./assets/quickstart.py)
>
> - Or you can keep things super easy by using [OpenAI SDK with Memobase.](https://docs.memobase.io/practices/openai), [Ollama with Memobase](./assets/tutorials/ollama+memobase).
>
> - Looking for [MCP](https://github.com/modelcontextprotocol)? Memobase-MCP is also [available](./src/mcp)

### 1. Make sure you're connected

 ```python
 from memobase import MemoBaseClient, ChatBlob
 
 client = MemoBaseClient(
     project_url=PROJECT_URL,
     api_key=PROJECT_TOKEN,
 )
 assert client.ping()
 ```

### 2. Manage Users

```python
uid = client.add_user({"any_key": "any_value"})
client.update_user(uid, {"any_key": "any_value2"})
u = client.get_user(uid)
print(u)

# client.delete_user(uid)
```

### 3. Insert Data

> In Memobase, all types of data are blobs to a user that can insert, get and delete:

```python
messages = [
  {
      "role": "user",
      "content": "Hello, I'm Gus",
  },
  {
      "role": "assistant",
      "content": "Hi, nice to meet you, Gus!",
  }
]
bid = u.insert(ChatBlob(messages=messages))
print(u.get(bid)) # not found once you flush the memory.

# u.delete(bid)
```

> Be default, Memobase will remove the blobs once they're processed. This means that apart from the relevant memory, your data will not be stored with Memobase. You can persist the blobs by adjusting the [configuration file](https://docs.memobase.io/features/customization/full#storage-config).

### 4. Get your Memory

```python
u.flush(sync=True)
```
> By default, Memobase will flush the buffer asynchronously. You can set `sync=True` to wait for the buffer to be processed.

And what will you get?

```python
print(u.profile(need_json=True))

# results
{
  "basic_info": {
    "name": {
      "content": "Gus",
      "id": ...,
      "created_at": ...
    }
  }
}
```

`u.profile()` will return structured profiles that are learned from this user, including `topic`, `sub_topic` and `content`. As you insert more blobs, the profile will become better.

<details>
<summary> Why need a flush?</summary>

In Memobase, we don't memoize users in [hot path](https://langchain-ai.github.io/langgraph/concepts/memory/#writing-memories-in-the-hot-path). We use buffer zones for the recent inserted blobs.

When the buffer zone becomes too large (e.g., 1024 tokens) or remains idle for an extended period (e.g., 1 hour), Memobase will flush the entire buffer into memory.  Alternatively, you can use `flush()` manually decide when to flush, such as when a chat session is closed in your app.
</details>



### 5. Integrate memory into your prompt

Memobase has a `context` api to pack everything you need into a simple string, where you can insert it into your prompt directly:

```python
print(u.context(max_token_size=500, prefer_topics=["basic_info"]))
```

Something like:

```
# Memory
Unless the user has relevant queries, do not actively mention those memories in the conversation.
## User Background:
- basic_info:name: Gus
...

## Latest Events:
...
```

Checkout the detail params [here](https://docs.memobase.io/api-reference/prompt/get_context).

## What's next?

- **Run script**: Checkout the [quickstart script](./assets/quickstart.py) for more details
- **Design your profile!**: You may want to explore the [customization](https://docs.memobase.io/features/profile/profile) of Memobase to make sure the system works as your expectation.
- **Full-stack Chatbot with Memobase**: Check [Memobase-Playground](https://github.com/memodb-io/memobase-playground). An open-source, full-stack template AI Chatbot with long-term memory. [live-demo](https://app.memobase.io/playground)
- **Web UI for Memobase**: Check [Memobase-Inspector](https://github.com/memodb-io/memobase-inspector). An open-source UI for your Memobase project with user table, usage chart and test playground. [live-demo](https://app.memobase.io/inspector)



## Why/Where should I use Memobase?

### Remember the users 

By placing profiles into your AI (*e.g.* system prompt).

<details>
<summary>Demo</summary>


```python
PROFILES = "\n".join([p.describe for p in u.profile()])

print(PROFILES)
# basic_info: name - Gus
# basic_info: age - 25
# ...
# interest: foods - Mexican cuisine
# psychological: goals - Build something that maybe useful
# ...
```

</details>

### User analysis and tracking

Too much information is hidden in the conversations between users and AI, that's why you need a new data tracking method to record user preference and behavior.

<details>
<summary>Demo</summary>


```python
PROFILES = u.profile()

def under_age_30(p):
  return p.sub_topic == "age" and int(p.content) < 30

def love_cat(p):
  return p.topic == "interest" and p.sub_topic == "pets" and "cat" in p.content

is_user_under_30 = (
    len([p for p in profiles if under_age_30(p)]) > 0
)
is_user_love_cat = (
  len([p for p in profiles if love_cat(p)]) > 0
)                       
...
```
</details>

### Sell something to your customers.  

Not everyone is looking for Grammarly, it's always nice to sell something your users might want. 

<details>
<summary>Demo</summary>


```python
def pick_an_ad(profiles):
  work_titles = [p for p in profiles if p.topic=="work" and p.sub_topic=="title"]
  if not len(work_titles):
    return None
  wt = work_titles[0].content
  if wt == "Software Engineer":
    return "Deep Learning Stuff"
  elif wt == "some job":
    return "some ads"
  ...
```
</details>



## Documentation

For detailed usage instructions, visit the [documentation](https://docs.memobase.io/). 



## Stay Updated

Star Memobase on Github to support and receive instant notifications!

![click_star](./assets/images/click.gif)



## Support

Join the community for support and discussions:

-  [Join our Discord](https://discord.gg/YdgwU4d9NB) 👻 

- [Follow us on Twitter](https://x.com/memobase_io) 𝕏 

Or Just [email us](mailto:contact@memobase.io) ❤️





## Contribute

- Check out our [Changelog](./Changelog.md) first, make sure the feature you want has not been developed or is currently being planned.:)
- Go through [Contributing](./CONTRIBUTING.md) document to setup and contribute to Memobase.



## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/memodb-io/memobase/blob/main/LICENSE) file for details.
