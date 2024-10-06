> This doc offers a overview of APIs between memobase client and server.

## Project URL and Access token

Any API requires you to pass the project URL and access token, 

### Self-managed Instances

If you're running self-managed instances, the project url depends on your machine (usually `http://localhost:8019`, port is 8019).

Access token can be setup by you in your memobase server `.env`.:

```
ACCESS_TOKEN_SECRET="YOUR TOKEN"
```

### Cloud service

If you're using the cloud service, a project url will be given to you in our [dashboard](https://dashboard.memobase.io) (something like `https://PROJECT_HASH.memobase.io`). The access token will be given, too.

### Access

If you're using APIs, pass the access token in your request header:

```shell
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" https://PROJECT_HASH.memobase.io/api/v1/...
```

If you're using python SDK:

```python
from memobase import MemoBaseClient

client = MemoBaseClient(
  project_url="https://PROJECT_HASH.memobase.io", 
  api_key=YOUR_ACCESS_TOKEN
)
```

## CURD of users

### Create

```python
user_id = client.add_user(**schema)
```

### Update

You don't need to update user's info manually. MemoBase will update it for you according to user's memory.

### Get

```python
user_data = client.get_user(user_id, want_fields={...})
```

### Delete

```python
client.delete_user(user_id)
```



## Memory management

### Insert

#### `Blob`

MemoBase serparates multiple sources of user data in order to achieve better performance:

- `ChatBlob`: you can pass your openai-style chatting message to this blob.
- `DocBlob`: Just a string doc for user.
- `TransctiptBlob`:  🚧
- `ImageBlob`:  🚧

```python
client.user(user_id).insert(blob)
```

### Query

#### `Blob` with `hits`

When you query a user's memory, MemoBase will return a list of revelant blobs, with hits.

What is hits? Suppose you upsert a long doc for user A:

```python
PARA1
...
PARAN
```

When you querying, only some of paragraphs will be revelant, that's hits. The returned blobs from memobase's query will have all the fields a blob will have, and also a `hits` field:

- For `ChatBlob`, `hits` is a list of openai-style messages.
- For `DocBlob`, `hits` is a list of two-int tuples. For each tuple, the first int is the start index in doc of this hit, the second int is the end index  in doc of this hit.
- For `TranscriptBlob`, `hits` is a list of two-int tuples. For each tuple, the first int is the start timestamp(in seconds) of this hit, the second int is the end timestamp of this hit
- For `ImageBlob`, `hits` is always None for near ROADMAP

```python
blobs = client.user(user_id).query("Who am I")
```

### Delete

Remove certain blobs from a user memory:

```python
client.user(user_id).delete(blob_id)
```

### Forget

Normally, you don't have to worry about operating this mechanism. Forgetting will happen when a user's memory is too large for MemoBase (right now is 3 million tokens per user).





## Define User schema 🚧

You can define what you want to extract from user's memory, for example:

```python
TODO
```

