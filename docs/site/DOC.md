=== api-reference/blobs/delete_blob.mdx ===
---
title: 'Delete Blob'
openapi: delete /api/v1/blobs/{user_id}/{blob_id}
---

Delete a specific memory blob from a user's storage. This operation permanently removes the blob data from the system. 

=== api-reference/blobs/get_all_data.mdx ===
---
title: 'Get User Blobs'
openapi: get /api/v1/users/blobs/{user_id}/{blob_type}
---

Retrieve all memory blobs of a specific type for a user. This endpoint supports pagination to manage large sets of memory data efficiently.

Query Parameters:
- page: Page number (default: 0)
- page_size: Number of items per page (default: 10)


=== api-reference/blobs/get_blob.mdx ===
---
title: 'Get Blob'
openapi: get /api/v1/blobs/{user_id}/{blob_id}
---

Retrieve a specific memory blob for a user. This endpoint returns the detailed content and metadata of a single memory blob. 

=== api-reference/blobs/insert_data.mdx ===
---
title: 'Insert Data to a User'
openapi: post /api/v1/blobs/insert/{user_id}
---

Insert new memory data (blob) for a specific user. This endpoint handles the storage of memory data and automatically updates the user's memory buffer.

The inserted data will be processed and integrated into the user's long-term memory profile.

Memobase plans to support the following blob types:  
- `ChatBlob`: ✅ [supported](/api-reference/blobs/modal/chat).  
- `DocBlob`: 🚧 in progress  
- `ImageBlob`: 🚧 in progress  
- `CodeBlob`: 🚧 in progress  
- `TranscriptBlob`: 🚧 in progress  

=== api-reference/blobs/modal/chat.mdx ===
---
title: 'ChatBlob'
---

ChatBlob is for user/AI messages. 
Memobase will automatically understand and extract the messages into structured profiles.

An example of ChatBlob is below:

<Accordion title="Example to insert ChatBlob">
<CodeGroup>
```python Python
from memobase import ChatBlob

b = ChatBlob(messages=[
    {"role": "user", "content": "Hello, how are you?"},
    {
        "role": "assistant", 
        "content": "I'm fine, thank you!", 
        "alias": "Her", 
        "created_at": "2025-01-01"
    },
])


u.insert(b)
```
```bash https
curl -X POST "$PROJECT_URL/api/v1/blobs/insert/{uid}" \
     -H "Authorization: Bearer $PROJECT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{ "blob_type": "chat", "blob_data": { "messages": [ {"role": "user","content": "Hi, Im here again"}, {"role": "assistant", "content": "Hi, Gus! How can I help you?", "alias": "Her", "created_at": "2025-01-01"}] }}'
```
</CodeGroup>
</Accordion>

The message format is OpenAI Message format:
```json
{
  "role": "user" | "assistant",
  "content": "string",
  "alias": "string, optional",
  "created_at": "string, optional"
}
```
- `role`: user or assistant
- `content`: message content
- `alias`: optional. You can set the name of the character(user or assistant), it will reflect in the memory profile.
- `created_at`: optional. You can set the date of the message.


=== api-reference/buffer/flush.mdx ===
---
title: 'Flush Buffer'
openapi: post /api/v1/users/buffer/{user_id}/{buffer_type}
---

Flush the memory buffer for a specific user and buffer type. This endpoint ensures all pending memory operations are processed and committed to long-term storage.


=== api-reference/buffer/size.mdx ===
---
title: 'Get Buffer Ids'
openapi: get /api/v1/users/buffer/capacity/{user_id}/{buffer_type}
---

Get the ids of the buffer for a specific user and buffer type. This endpoint returns buffer ids.


=== api-reference/events/delete_event.mdx ===
---
title: 'Delete User Event'
openapi: delete /api/v1/users/event/{user_id}/{event_id}
---

Delete a user event.



=== api-reference/events/get_events.mdx ===
---
title: 'Get User Recent Events'
openapi: get /api/v1/users/event/{user_id}
---


Returns a list of the user's most recent events, ordered by recency.



=== api-reference/events/search_event_gists.mdx ===
---
title: 'Search Event Gists'
openapi: get /api/v1/users/event_gist/search/{user_id}
---
Search event gists by query.
Event gist is a fraction of User Event. For example, if a user event has the `event_tips`:
```
- A // info
- B // schedule
- C // reminder
```
The event gists will be 
- `- A // info`
- `- B // schedule`
- `- C // reminder`



=== api-reference/events/search_events.mdx ===
---
title: 'Search Events'
openapi: get /api/v1/users/event/search/{user_id}
---
Search events by query.



=== api-reference/events/update_event.mdx ===
---
title: 'Update User Event'
openapi: put /api/v1/users/event/{user_id}/{event_id}
---

Update a user event with data.



=== api-reference/experimental/import_memory.mdx ===
---
title: 'Import Memory from Text'
openapi: POST /api/v1/users/profile/import/{user_id}
---


=== api-reference/experimental/proactive_topic.mdx ===
---
title: 'Proactive Topics'
openapi: "POST /api/v1/users/roleplay/proactive/{user_id}"
---


=== api-reference/overview.mdx ===
# Memobase API Overview

Memobase provides a powerful set of APIs for integrating user profile-based memory capabilities into your GenAI applications. Our APIs are designed to help your AI remember users through efficient memory management and profile generation.

## Key Features

- **User Memory Management**: Create, retrieve, update, and delete user memories with ease
- **Profile Generation**: Automatically generate user profiles from conversations and interactions
- **Buffer System**: Efficient memory processing with buffer zones for recent interactions
- **Customizable Profiles**: Define the aspects you want Memobase to collect about your users
- **Secure Authentication**: API token-based access control for your data

## API Structure

Our API is organized into several main categories:

1. **User APIs**: Manage user entities and their data
   - Create and manage users
   - Update user information
   - Delete user accounts

2. **Data APIs**: Handle data operations
   - Insert blobs
   - Get blobs
   - Delete blobs
   - Get all blobs

3. **Profile APIs**: Access and manage user profiles
   - Get user profiles
   - Delete specific profiles
   - Customize profile generation

## Authentication

All API requests require authentication using Bearer token authentication. Include your API token in the Authorization header of each request:

```http
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## Getting Started

To begin using the Memobase API, you'll need to:

1. Set up your Memobase backend server
   - Default URL: `http://localhost:8019`
   - Default token: `secret`

2. Make your first API call:
   ```python
   from memobase import MemoBaseClient
   
   mb = MemoBaseClient("http://localhost:8019", "secret")
   assert mb.ping()
   ```

3. Start exploring the APIs!


## Data Processing

By default, Memobase processes and removes raw memory blobs after generating profiles. This ensures:
- Efficient storage usage
- Privacy-focused data handling
- Relevant information extraction

You can customize this behavior through configuration settings.

For detailed API endpoint documentation, explore the specific API sections in this documentation.


=== api-reference/profiles/add_profile.mdx ===
---
title: 'Add User Profile'
openapi: post /api/v1/users/profile/{user_id}
---
This endpoint allows you to add new profile entries to a user's long-term memory.


=== api-reference/profiles/delete_profile.mdx ===
---
title: 'Delete User Profile'
openapi: delete /api/v1/users/profile/{user_id}/{profile_id}
---

Delete a specific profile from a user's long-term memory. This endpoint allows you to remove individual profile entries that are no longer needed.


=== api-reference/profiles/profile.mdx ===
---
title: 'Get User Profile'
openapi: get /api/v1/users/profile/{user_id}
---

Retrieve the real-time user profiles for long-term memory. This endpoint provides access to the consolidated profile information generated from user's memory data.


=== api-reference/profiles/update_profile.mdx ===
---
title: 'Update User Profile'
openapi: put /api/v1/users/profile/{user_id}/{profile_id}
---
Update a specific profile in a user's long-term memory.


=== api-reference/project/get_profile_config.mdx ===
---
title: 'Get Current Profile Config'
openapi: get /api/v1/project/profile_config
---


Returns the current profile config, Empty if using the default profile config in `config.yaml`.



=== api-reference/project/get_usage.mdx ===
---
title: 'Get Project Daily Usage'
openapi: get /api/v1/project/usage
---

Get the daily usage statistics of a project over the last N days.

This endpoint provides detailed usage metrics including:
- Total blob insertions per day
- Successful blob insertions per day  
- Input tokens consumed per day
- Output tokens consumed per day

The data is returned as a time series for the specified number of days, allowing you to track usage patterns and project activity over time. 

=== api-reference/project/get_users.mdx ===
---
title: 'Get Project Users'
openapi: get /api/v1/project/users
---

Get the users of a project with various filtering and ordering options.

This endpoint allows you to:
- Search users by username
- Order results by different fields (updated_at, profile_count, event_count)
- Control sort direction (ascending or descending)
- Paginate results with limit and offset

The response includes user data along with their profile count and event count for better project insights. 

=== api-reference/project/update_profile_config.mdx ===
---
title: 'Update Current Profile Config'
openapi: post /api/v1/project/profile_config
---


Updates the current profile config. Checkout more details in [Profile Config](/features/customization/profile#understand-the-user-profile-slots).

Below is an example of your profile config:

```yaml
overwrite_user_profiles:
  - topic: "User Basic Information"
    sub_topics:
      - name: "Name"
      - name: "Gender"
      - name: "Age"
      - name: "Occupation"
        description: "For example, a programmer"
      - name: "City"
  - topic: "User Pet Information"
    sub_topics:
      - name: "Purpose of Pet Ownership"
      - name: "Attitude Towards Pet Ownership"
        description: "whether they like to play with the pet"
      - name: "Pet Medical Habits"
        description: "Whether they are accustomed to finding medicine themselves"
...
``` 

Your profile config will not as strong as the `config.yaml` you used to start Memobase server,
it only affect the profile slots.

=== api-reference/prompt/get_context.mdx ===
---
title: 'Get User Personalized Context'
openapi: get /api/v1/users/context/{user_id}
---


Return a string of the user's personalized context you can directly insert it into your prompt.

Format:
```
<memory>
# Below is the user profile:
{profile}

# Below is the latest events of the user:
{event}
</memory>
Please provide your answer using the information within the <memory> tag at the appropriate time.
```


=== api-reference/users/create_user.mdx ===
---
title: 'Create User'
openapi: post /api/v1/users
---

Create a new user in the memory system with additional user-specific data. This endpoint initializes a new user entity that can store and manage memories.


=== api-reference/users/delete_user.mdx ===
---
title: 'Delete User'
openapi: delete /api/v1/users/{user_id}
---

Remove a user and all associated data from the memory system. This operation permanently deletes the user's profile and memories.


=== api-reference/users/get_user.mdx ===
---
title: 'Get User'
openapi: get /api/v1/users/{user_id}
---

Retrieve user information and associated data. This endpoint returns the user's profile and configuration data.


=== api-reference/users/update_user.mdx ===
---
title: 'Update User'
openapi: put /api/v1/users/{user_id}
---

Update an existing user's data. This endpoint allows you to modify user-specific information and settings.


=== api-reference/utility/healthcheck.mdx ===
---
title: 'Health Check'
openapi: get /api/v1/healthcheck
---

Check if your memobase server is set up correctly and all required services (database, Redis) are available and functioning properly. 

=== api-reference/utility/usage.mdx ===
---
title: 'Get Project Usage'
openapi: get /api/v1/project/billing
---

Get the usage of your project.


=== cost.mdx ===
---
title: Performance and Cost
---

## Overview

Memobase is designed for high performance and cost-efficiency.

-   **Query Performance**: Queries are extremely fast because Memobase returns a pre-compiled user profile, eliminating the need for on-the-fly analysis.
-   **Controllable Costs**: You can manage costs by controlling the size of user profiles. This is done by configuring the number of profile slots and the maximum token size for each.
    -   Learn to design profile slots [here](/features/profile/profile_config).
    -   Learn to control token limits [here](/references/cloud_config).
-   **Insertion Efficiency**: New data is added to a buffer and processed in batches. This approach amortizes the cost of AI analysis, making insertions fast and inexpensive.
    -   Learn to configure the buffer [here](/references/cloud_config).

## Comparison vs. Other Solutions

#### Memobase vs. [mem0](https://github.com/mem0ai/mem0)

-   **Cost**: Memobase is approximately 5x more cost-effective.
-   **Performance**: Memobase is roughly 5x faster.
-   **Memory Quality**: mem0 provides gist-based memories, while Memobase delivers structured and organized profiles for more predictable recall.

The full technical report is available [here](https://github.com/memodb-io/memobase/tree/docs/docs/experiments/900-chats).

=== features.mdx ===
---
title: Features
---

## 🚀 What is Memobase?
- **AI-Powered Backend**: Memobase is a backend service designed to manage dynamic user profiles for your AI applications.
- **Automated Profile Building**: It analyzes user interactions to build rich, structured profiles, capturing everything from basic demographics to specific user preferences.
- **Personalized Experiences**: Leverage these detailed profiles to create highly personalized and engaging user experiences.
- **Scalable & Fast**: Built for performance, Memobase efficiently handles user data at any scale.

## 🖼️ User Profiles as Memory
- **Custom Memory Slots**: Define what your AI should remember. Whether it's a user's favorite color, their dog's name, or professional background, you can create custom fields for any data point.
- **Structured & Predictable**: User profiles are organized into a clear topic/subtopic structure (e.g., `interests/movies`), making them easy to parse and use in your AI logic.
- **Simple & Powerful**: This human-readable format is robust enough to store a lifetime of user memories.

## 👌 Core Use Cases
- **Long-Term Memory**: Give your AI the ability to remember past interactions and user details.
- **User Analysis**: Gain deep insights into user behavior and preferences to enhance your application.
- **Targeted Content**: Deliver personalized content, recommendations, and promotions that resonate with your users.

## 🤔 How It Works
- **Data Blobs**: Memobase stores user data in flexible "blobs." You can insert, retrieve, and delete these data chunks as needed.
- **Buffering System**: Recent data is held in a temporary buffer before being processed and integrated into the long-term user profile. This flush can be triggered automatically or manually.
- **Profile Evolution**: Over time, Memobase constructs comprehensive user profiles that enable your application to deliver truly personalized experiences.

## 💰 Performance and Cost
For details on performance benchmarks and pricing, see our [Cost page](/cost).

=== features/async_insert.mdx ===
---
title: Asynchronous Operations
---

Memobase supports asynchronous operations for inserting and flushing data. Offloading these tasks to background processes improves your application's performance and responsiveness by preventing memory operations from blocking the main thread.

When you perform an asynchronous insert or flush, the data is queued for processing, and the method returns immediately. This allows your application to continue executing while Memobase handles the data in the background.

### SDK Examples

Here’s how to use both synchronous and asynchronous operations in our SDKs:

<CodeGroup>
```python Python
from memobase import MemoBaseClient
from memobase.core.blob import ChatBlob

client = MemoBaseClient(project_url='YOUR_PROJECT_URL', api_key='YOUR_API_KEY')
user = client.get_user('some_user_id')

# Create a data blob
blob = ChatBlob(messages=[
    {"role": "user", "content": "Hi, I'm here again"},
    {"role": "assistant", "content": "Hi, Gus! How can I help you?"}
])

# Asynchronous insert (default behavior)
blob_id = user.insert(blob)

# Asynchronous flush (default behavior)
user.flush()

# Synchronous flush (waits for completion)
user.flush(sync=True)
```

```javascript JavaScript
import { MemoBaseClient, Blob, BlobType } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

// Asynchronous insert
const blobId = await user.insert(Blob.parse({
  type: BlobType.Enum.chat,
  messages: [
    { role: 'user', content: 'Hi, I\'m here again' },
    { role: 'assistant', content: 'Hi, Gus! How can I help you?' }
  ]
}));

// Asynchronous flush
await user.flush(BlobType.Enum.chat);
```

```go Go
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/blob"
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    client, err := core.NewMemoBaseClient("YOUR_PROJECT_URL", "YOUR_API_KEY")
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    user, err := client.GetUser("EXISTING_USER_ID", false)
    if err != nil {
        log.Fatalf("Failed to get user: %v", err)
    }

    chatBlob := &blob.ChatBlob{
        Messages: []blob.OpenAICompatibleMessage{
            {Role: "user", Content: "Hello, I am Jinjia!"},
            {Role: "assistant", Content: "Hi there! How can I help you today?"},
        },
    }

    // Asynchronous insert (sync=false)
    blobID, err := user.Insert(chatBlob, false)
    if err != nil {
        log.Fatalf("Failed to insert blob: %v", err)
    }
    fmt.Printf("Successfully queued blob for insertion with ID: %s\n", blobID)

    // Asynchronous flush (sync=false)
    err = user.Flush(blob.ChatType, false)
    if err != nil {
        log.Fatalf("Failed to flush buffer: %v", err)
    }
    fmt.Println("Successfully queued buffer for flushing")

    // Synchronous flush (sync=true)
    err = user.Flush(blob.ChatType, true)
    if err != nil {
        log.Fatalf("Failed to flush buffer: %v", err)
    }
    fmt.Println("Successfully flushed buffer synchronously")
}
```
</CodeGroup>

For more details, see the API reference for [flush](/api-reference/buffer/flush) and [insert](/api-reference/blobs/insert_data).


=== features/context.mdx ===
---
title: Retrieving the Memory Prompt
---

Memobase automatically extracts and structures various types of memories from user interactions, including:
-   **User Profile**: Key-value attributes describing the user (e.g., name, location, preferences).
-   **User Events**: Significant occurrences and interactions from the user's history.

This collection of memories forms a user's personalized context. Memobase provides a powerful `context()` API to retrieve this information as a structured string, ready to be injected directly into your LLM prompts.

### Basic Usage

The simplest way to get a user's context is to call the `context()` method on a user object.

<CodeGroup>
```python Python
from memobase import MemoBaseClient, ChatBlob

# Initialize client and get/create a user
client = MemoBaseClient(api_key="your_api_key")
user = client.get_user(client.add_user(profile={"name": "Gus"}))

# Insert data to generate memories
user.insert(
    ChatBlob(
        messages=[
            {"role": "user", "content": "I live in California."},
            {"role": "assistant", "content": "Nice, I've heard it's sunny there!"}
        ]
    )
)

# Retrieve the default context prompt
user_context = user.context()
print(user_context)
```

```txt Output
# Memory
Unless the user has relevant queries, do not actively mention these memories in the conversation.

## User Background:
- basic_info:name: Gus
- basic_info:location: California

## Latest Events:
- User mentioned living in California.
```
</CodeGroup>

### Context-Aware Retrieval

To make the retrieved context more relevant to the ongoing conversation, you can provide recent chat messages. Memobase will perform a semantic search to prioritize the most relevant historical events, rather than simply returning the most recent ones.

<CodeGroup>
```python Python
# Continuing from the previous example...
recent_chats = [
    {"role": "user", "content": "What is my name?"}
]

# Get context relevant to the recent chat
relevant_context = user.context(chats=recent_chats)
print(relevant_context)
```

```txt Output
# Memory
...
## User Background:
- basic_info:name: Gus
- basic_info:location: California

## Latest Events:
- User stated their name is Gus.
- User previously mentioned being called John.
```
</CodeGroup>

### Controlling Context Size

You can manage the size and cost of your prompts by limiting the token count of the retrieved context using the `max_tokens` parameter.

<CodeGroup>
```python Python
# Get a condensed context with a token limit
compact_context = user.context(max_tokens=20)
print(compact_context)
```

```txt Output
# Memory
...
## User Background:
- basic_info:name: Gus

## Latest Events:
- User mentioned living in California.
```
</CodeGroup>

**Note**: The `max_tokens` limit applies to the profile and event content, not the final formatted string. If you use a large custom prompt template, the final output may still exceed the limit.

### Advanced Filtering

The `context()` API offers several parameters for fine-grained control:

-   `prefer_topics`, `only_topics`: Prioritize or exclusively include certain profile topics.
-   `max_subtopic_size`: Limit the number of sub-topics returned per topic.
-   `profile_event_ratio`: Adjust the balance between profile and event information.
-   `time_range_in_days`: Filter events to a specific time window.
-   `customize_context_prompt`: Provide a custom template for the final output string.

For a full list of parameters, refer to the [API Reference for `get_context`](/api-reference/prompt/get_context).


=== features/event/event.mdx ===
---
title: Event Fundamentals
---

Memobase automatically tracks key events and memories from user interactions, creating a chronological record of their experiences.

```python
from memobase import MemoBaseClient, ChatBlob

# Initialize the client
client = MemoBaseClient(api_key="your_api_key")

# Create a user and insert a chat message
user = client.get_user(client.add_user())
user.insert(
    ChatBlob(
        messages=[{"role": "user", "content": "My name is Gus"}]
    )
)

# Retrieve the user's events
print(user.event())
```

## Event Structure

Each event object contains the following information:

-   **Event Summary** (Optional): A concise summary of the user's recent interaction. Learn more about [Event Summaries](/features/event/event_summary).
-   **Event Tags** (Optional): Semantic tags that categorize the event (e.g., `emotion::happy`, `goal::buy_a_house`). Learn how to [design custom tags](/features/event/event_tag).
-   **Profile Delta** (Required): The specific profile slots that were created or updated during this event.
-   **Created Time** (Required): The timestamp of when the event occurred.

A detailed description of the event format can be found in the [API Reference](/api-reference/events/get_events).



=== features/event/event_search.mdx ===
---
title: Searching Events
---

User events in Memobase are stored as a sequence of experiences, each enriched with [tags](/features/event/event_tag). By default, events are retrieved in chronological order, but Memobase also provides a powerful search function to find events based on a query.

## Semantic Search

You can perform a semantic search to find events related to a specific topic or concept.

```python
# To use the Python SDK, first install the package:
# pip install memobase

from memobase import MemoBaseClient

client = MemoBaseClient(project_url='YOUR_PROJECT_URL', api_key='YOUR_API_KEY')
user = client.get_user('some_user_id')

# Search for events related to the user's emotions
events = user.search_event("Anything about my emotions")
print(events)
```

This query will return events where the user discussed their emotions, events that were automatically [tagged](/features/event/event_tag) with an `emotion` tag, or events that updated profile slots related to emotion.

For a detailed list of search parameters, please refer to the [API documentation](/api-reference/events/search_events).

## Search Event Gists

A user event is a group of user infos happened in a period of time.
So when you need to search for specific facts or infos, you may need a more fine-grained search.

In Memobase, we call it `event_gist`. `event_gist` is a fraction of `user_event` that only contains one fact, schedule, or reminder of user.

So if you want to search particular things of user, without the context of other infos, you can use `search_event_gist` to conduct a search:
<CodeGroup>
```python Python
# To use the Python SDK, install the package:
# pip install memobase
from memobase import MemoBaseClient
from memobase.core.blob import ChatBlob

client = MemoBaseClient(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
u = client.get_user(UID)

events = u.search_event_gist('Car')
print(events)
```
```txt Output
- user bought a car [mentioned at 2025-01]
- user drove to the car dealership [mentioned at 2025-06]
- user likes BMW [mentioned at 2024-08]
...
```
</CodeGroup>

For detail API, please refer to [Search Event Gists](/api-reference/events/search_event_gists).

=== features/event/event_summary.mdx ===
---
title: Customizing Event Summaries
---

For each event, Memobase generates a concise summary of the recent user interaction. This summary serves as the primary input for the subsequent extraction of profile updates and event tags, making its quality crucial for the overall effectiveness of the memory system.

Memobase allows you to customize the prompt used for generating these summaries, giving you greater control over the focus and quality of the extracted information.

## Customizing the Summary Prompt

You can add a custom instruction to the summary generation process via the `event_theme_requirement` field in your `config.yaml` file. For example, if you want the summary to focus on the user's personal information rather than their instructions to the AI, you can configure it as follows:

```yaml config.yaml
event_theme_requirement: "Focus on the user's personal information and feelings, not their direct commands or questions."
```

This allows you to fine-tune the event summaries to better suit the specific needs of your application.

=== features/event/event_tag.mdx ===
---
title: Using Event Tags
---

Event tags are a powerful feature for automatically categorizing user events with semantic attributes. You can use them to enrich event data and track user behavior over time across various dimensions, such as:

-   Emotion (`happy`, `frustrated`)
-   Life Goals (`buying_a_house`, `learning_a_skill`)
-   Relationships (`new_friend`, `family_mention`)

## Configuring Event Tags

By default, no event tags are recorded. You must define the tags you want to track in your `config.yaml` file:

```yaml config.yaml
event_tags:
  - name: "emotion"
    description: "Records the user's current emotional state."
  - name: "romance"
    description: "Tracks any mention of romantic relationships or feelings."
```

Once configured, Memobase will automatically analyze interactions and apply these tags to events when relevant. The `description` field is crucial for helping the AI accurately understand when to apply each tag.

## Retrieving Event Tags

Event tags are returned as part of the event object when you retrieve a user's event history.

```python
from memobase import MemoBaseClient

client = MemoBaseClient(project_url='YOUR_PROJECT_URL', api_key='YOUR_API_KEY')
user = client.get_user('some_user_id')

events = user.event()
for event in events:
    print(event.event_data.event_tags)
```

## Searching Events by Tag

You can also search for events that have specific tags applied.

```python
from memobase import MemoBaseClient

client = MemoBaseClient(project_url='YOUR_PROJECT_URL', api_key='YOUR_API_KEY')
user = client.get_user('some_user_id')

# Find all events tagged with 'emotion'
events = user.search_event(tags=["emotion"])
print(events)
```

For more details, see the [API Reference](/api-reference/events/search_events).

=== features/message.mdx ===
---
title: Customizing Chat Messages
---

Memobase builds user memories from the chat interactions you provide. However, simple `user` and `assistant` roles are not always sufficient to capture the full context. Memobase allows you to add custom metadata to your messages to handle more complex scenarios.

## Custom Timestamps

It's important to distinguish between two types of timestamps in Memobase:

-   **External Timestamp**: The time a memory is stored or updated in the database.
-   **Internal Timestamp**: The time an event actually occurred according to the content of the memory itself (e.g., a birthday, a travel date).

The internal timestamp is often more critical as it directly influences the AI's understanding and responses. By default, Memobase assumes the insertion time is the time the message occurred. You can override this by providing a `created_at` field.

This is useful for importing historical data or for applications set in fictional timelines.

```python
from memobase import MemoBaseClient, ChatBlob

client = MemoBaseClient(api_key="your_api_key")
user = client.get_user(client.add_user())

# This message occurred in a fictional future year
messages = ChatBlob(messages=[
    dict(role="user", content="I am starting a rebellion.", created_at="Year 32637")
])

user.insert(messages)
```

Memobase will process this chat according to the provided timestamp, resulting in a memory like: `"In the year 32637, the user started a rebellion."`

You can use any date or time format; Memobase will extract the time at the appropriate granularity.

## Character Aliases

For more complex interactions, such as multi-character role-playing, you can assign names or `alias` values to the `user` and `assistant` roles.

```python
messages = ChatBlob(messages=[
    dict(role="user", content="I wish to declare war.", alias="The Emperor"),
    dict(role="assistant", content="Perhaps you should rest instead.", alias="The Advisor")
])
```

By providing aliases, you give Memobase the context to create more accurate and personalized memories, such as: `"The Emperor wished to declare war, but The Advisor suggested rest instead."`

=== features/profile/profile.mdx ===
---
title: Profile Fundamentals
---

Memobase serves as a [user profile backend](/features#user-profile-as-memory) for LLM applications, enabling them to track and update specific user attributes over time.

<Frame caption="A sample user profile in Memobase, showing structured data slots.">
  <img src="/images/profile_demo.png" />
</Frame>

By default, Memobase includes a set of built-in profile slots for common use cases, but it also offers full customization to control the specific memories your application collects.

### Locating the `config.yaml` File

Memobase uses a `config.yaml` file for backend configuration. You can find this file at `src/server/api/config.yaml` in your self-hosted instance. A typical configuration looks like this:

```yaml
max_chat_blob_buffer_token_size: 1024
buffer_flush_interval: 3600
llm_api_key: sk-...
best_llm_model: gpt-4o-mini
# ... other settings
```

## Understanding Profile Slots

Memobase comes with a default schema of profile slots, such as:

```markdown
- basic_info
    - name
    - gender
- education
    - school
    - major
```

You can extend this schema by adding custom slots under the `additional_user_profiles` field in `config.yaml`:

```yaml
additional_user_profiles:
    - topic: "Gaming"
      description: "Tracks the user's gaming preferences and achievements."
      sub_topics:
        - name: "FPS"
          description: "First-person shooter games like CSGO, Valorant, etc."
        - name: "LOL"
    - topic: "Professional"
      sub_topics:
        - name: "Industry"
        - name: "Role"
```

Memobase will then track these additional slots and update the user profile accordingly. If you need to define a completely custom schema, use the `overwrite_user_profiles` field instead.

For detailed instructions on formatting profile slots, see [Profile Slot Configuration](/features/profile/profile_desc).

=== features/profile/profile_config.mdx ===
---
title: Profile Validation and Strictness
---

## Auto-Validation

By default, Memobase validates all new profile information before saving it. This process serves two main purposes:

1.  **Ensures Meaningful Data**: It filters out low-quality or irrelevant information that the LLM might generate, such as "User has a job" or "User did not state their name."
2.  **Maintains Schema Adherence**: It verifies that the extracted information aligns with the descriptions you have defined for your [profile slots](/features/profile/profile_desc).

However, if you find that too much information is being filtered out, you can disable this feature by setting `profile_validate_mode` to `false` in your `config.yaml`:

```yaml config.yaml
profile_validate_mode: false
```

Disabling validation will result in more data being saved, but it may also lead to less accurate or less relevant profile information.

## Strict Mode

By default, Memobase operates in a flexible mode, allowing the AI to extend your defined profile schema with new, relevant sub-topics it discovers during conversations. For example, if your configuration is:

```yaml config.yaml
overwrite_user_profiles:
    - topic: "work"
      sub_topics:
        - "company"
```

Memobase might generate a more detailed profile like this:

```json Possible Profile Output
{
    "work": {
        "company": "Google",
        "position": "Software Engineer",
        "department": "Engineering"
    }
}
```

This is often useful, as it's difficult to anticipate all the valuable information your users might provide. However, if you require that **only** the profile slots you have explicitly defined are saved, you can enable strict mode:

```yaml config.yaml
profile_strict_mode: true
```

In strict mode, Memobase will adhere rigidly to the schema in your `config.yaml`.



=== features/profile/profile_desc.mdx ===
---
title: Configuring Profile Slots
---

Memobase allows for detailed customization of how profile slots are created and updated.

## Instructing Profile Creation

Memobase uses a `topic` and `sub_topics` structure to define a profile slot. For example:

```yaml
overwrite_user_profiles:
    - topic: "work"
      sub_topics:
        - "company"
        - "position"
        - "department"
```

While this structure is often sufficient, you can provide additional `description` fields to give the AI more context and ensure it tracks the information you need with greater accuracy.

```yaml
overwrite_user_profiles:
    - topic: "work"
      sub_topics:
        - name: "start_date"
          description: "The user's start date at their current job, in YYYY-MM-DD format."
```

The `description` field is optional but highly recommended for achieving precise data extraction.

## Instructing Profile Updates

Memobase not only creates profile slots but also maintains them over time. When a user provides new information, Memobase must decide how to update the existing data.

For example, if a user mentions a new job, the `work/start_date` slot needs to be updated:

-   **Old Value**: `2020-01-01`
-   **New Information**: User starts a new job in 2021.
-   **Default Update**: The value is replaced with `2021-01-01`.

You can control this update behavior by adding an `update_description` to the profile slot. For instance, if you wanted to keep a record of the user's *first-ever* job start date, you could configure it like this:

```yaml
overwrite_user_profiles:
    - topic: "work"
      sub_topics:
        - name: "start_date"
          description: "The user's start date at their current job, in YYYY-MM-DD format."
          update_description: "Always keep the oldest start date. Do not update if a date already exists."
```

With this instruction, Memobase will preserve the original `start_date` instead of overwriting it.







=== features/profile/profile_filter.mdx ===
---
title: Filtering Profiles at Retrieval
---

Memobase tracks and models a comprehensive profile for each user. You can use this profile in your [AI prompts](/features/context) to provide a global understanding of the user.

While user profiles are generally concise, it is good practice to control the final size of the context you inject into your prompts. Memobase provides several parameters to help you filter profiles at retrieval time.

## Rule-Based Filtering

You can pass rules to the Memobase API to filter profiles based on specific criteria:

-   `max_token_size`: Sets the maximum token size for the entire profile context.
-   `prefer_topics`: Ranks specified topics higher, making them more likely to be included in the final output.
-   `only_topics`: Includes *only* the specified topics, filtering out all others.

Detailed parameter descriptions can be found in the [API documentation](/api-reference/profiles/profile).

## Context-Aware Filtering

Memobase also offers a powerful semantic filtering capability. By passing the latest chat messages to the API, you can retrieve only the most "contextual" or relevant profiles for the current conversation.

This is more advanced than a simple embedding-based search. Memobase uses the LLM to reason about which profile attributes would be most helpful for generating the next response.

For example, if a user says, "Find some restaurants for me," Memobase will intelligently rank profiles like `contact_info::city`, `interests::food`, and `health::allergies` higher in the results.

<CodeGroup>
```python Python
from memobase import MemoBaseClient

client = MemoBaseClient(project_url='YOUR_PROJECT_URL', api_key='YOUR_API_KEY')
user = client.get_user('some_user_id')

# Retrieve profile context relevant to the last message
contextual_profile = user.profile(
    chats=[{"role": "user", "content": "Find some restaurants for me"}],
    need_json=True
)

print(contextual_profile)
```
```json Output
{
  "contact_info": {
    "city": "San Francisco"
  },
  "interests": {
    "food": "Loves Italian and Japanese cuisine"
  },
  "health": {
    "allergies": "None"
  }
}
```
</CodeGroup>

For more details on contextual search, see the [Profile Search documentation](/features/profile/profile_search).

=== features/profile/profile_search.mdx ===
---
title: Context-Aware Profile Search
---

While Memobase is designed to provide a comprehensive, global [context](/features/context) for each user with very low latency, there are times when you need to search for specific information within a user's profile.

Memobase provides a powerful, context-aware search method to filter out irrelevant memories and retrieve only what's needed for the current turn of the conversation.

## How Profile Search Works

Unlike simple keyword or semantic matching, Memobase's profile search uses the LLM to perform a feature-based analysis. It reasons about what aspects of a user's profile are relevant to their latest query.

For example, if a user asks, "Can you recommend a good restaurant?", Memobase doesn't just search for the term "restaurant." Instead, it identifies key features that would help answer the question, such as:

-   `basic_info::location`: To determine the city for the restaurant search.
-   `interests::food`: To understand the user's cuisine preferences.
-   `health::allergies`: To know what ingredients to avoid.

This intelligent, feature-based approach results in a much more relevant and helpful set of memories than traditional search methods.

<CodeGroup>
```python Python
# Assume 'user' is an initialized MemoBaseUser object
contextual_profile = user.profile(
    chats=[{"role": "user", "content": "Find some restaurants for me"}],
    need_json=True
)

print(contextual_profile)
```
```json Output
{
    "basic_info": {
        "location": "San Francisco",
        "allergies": "peanuts"
    },
    "interests": {
        "food": "User enjoys trying new ramen shops."
    }
}
```
</CodeGroup>

See the [API Reference](/api-reference/profiles/profile#parameter-chats-str) for more details.

### Important Considerations

-   **Latency**: Profile search is a powerful but computationally intensive operation. It can add **2-5 seconds** to your response time, depending on the size of the user's profile. Use it judiciously.
-   **Cost**: Each profile search consumes Memobase tokens (roughly 100-1000 tokens per call), which will affect your usage costs.




=== introduction.mdx ===
---
title: What is Memobase?
---

Struggling with short-term memory in your AI applications? Memobase is the solution.

It's a fast, scalable, long-term **user memory backend** for your AI, helping you build applications that remember and understand their users.

<Frame caption="Memobase Architecture Overview">
  <img src="/images/starter.png" />
</Frame>

We currently support the following user memory types from chat interactions:
- [x] [Profile Memory](./features/profile/) - Understand who the user is.
- [x] [Event Memory](./features/event/) - Track what has happened in the user's life.
- [ ] Schedule Memory - Manage the user's calendar (Coming Soon).
- [ ] Social Memory - Map the user's relationships (Coming Soon).

Memobase is under active development, and we are looking for early adopters to become our design partners.

[Get in touch](https://github.com/memodb-io/memobase?tab=readme-ov-file#support) if you're interested in shaping the future of AI memory.

## Get Started

<CardGroup cols={3}>
  <Card
    title="Quickstart"
    icon="rocket"
    href="/quickstart"
  >
    Integrate Memobase with just a few lines of code.
  </Card>
  <Card
    title="Why Memobase"
    icon="question"
    href="/features"
  >
    Learn what makes Memobase unique.
  </Card>
  <Card
    title="API Reference"
    icon="square-terminal"
    href="/api-reference"
  >
    Explore our comprehensive API documentation.
  </Card>
</CardGroup>


## Vision
Our vision is to provide a powerful **second brain** for AI applications, enabling them to build lasting and meaningful user relationships.

=== practices/bad.mdx ===
---
title: Troubleshooting Common Issues
---

## Issue: Too Much Useless Information is Saved

If your user profiles are cluttered with irrelevant data, follow these steps:

1.  **Define Profile Scope**: Start by clearly defining what information each user profile should contain.
2.  **Refine Slot Descriptions**: Provide clear and specific descriptions for each profile slot in your `config.yaml`. This guides the AI on what to extract. [Learn more](/features/profile/profile_desc).
3.  **Enable Strict Mode**: If the issue persists, enable [strict mode](/features/profile/profile_config#strict-mode) to ensure the AI only saves information that directly matches your defined profile slots.

## Issue: Relevant Information is Not Being Saved

If the AI fails to extract important details, try the following:

1.  **Simplify Descriptions**: Your profile descriptions might be too complex for the LLM to interpret. Try simplifying them to be more direct.
2.  **Disable Validation**: If information is still not being captured, you can disable [profile validation](/features/profile/profile_config#profile-validate-mode) to allow for more flexible data extraction.

## Issue: Profile Data is Inaccurate or Wrong

To improve the accuracy of the information stored in profiles:

1.  **Add Detail to Descriptions**: Enhance your [profile descriptions](/features/profile/profile_desc) with more context and examples to ensure the AI understands the data format and meaning correctly.
2.  **Use Update Instructions**: For each profile slot, add an [update description](/features/profile/profile_desc#instruct-memobase-to-update-a-profile-slot). This tells Memobase how to intelligently merge new information with existing data, which helps maintain accuracy over time.



=== practices/openai.mdx ===
---
title: Using Memobase with the OpenAI API
---

<Frame caption="Diagram of OpenAI API with Memory Integration">
  <img src="/images/openai_client.png" />
</Frame>

Memobase integrates with the OpenAI API, allowing you to add long-term memory to chat completions without altering your existing code. This patch works with the official OpenAI SDK and any other OpenAI-compatible provider.

## Setup

1.  **Install SDKs**: Ensure both the Memobase and OpenAI Python SDKs are installed.
    ```bash
    pip install memobase openai
    ```

2.  **Initialize Clients**: Create instances of both the OpenAI and Memobase clients.
    ```python
    from openai import OpenAI
    from memobase import MemoBaseClient

    client = OpenAI()
    mb_client = MemoBaseClient(
        project_url=YOUR_PROJECT_URL,
        api_key=YOUR_API_KEY,
    )
    ```
    You can find your `project_url` and `api_key` after [setting up your backend](/quickstart#memobase-backend).

## Patch Memory

Apply the Memobase memory patch to your OpenAI client instance with a single function call.

```python
from memobase.patch.openai import openai_memory

client = openai_memory(client, mb_client)
```

## Usage

1.  To enable memory, simply add a `user_id` to your standard API call. The client will automatically handle the memory context.

    <CodeGroup>
    ```python OpenAI (Original)
    client.chat.completions.create(
        messages=[
            {"role": "user", "content": "My name is Gus"},
        ],
        model="gpt-4o"
    )
    ```
    ```python OpenAI with Memory
    client.chat.completions.create(
        messages=[
            {"role": "user", "content": "My name is Gus"},
        ],
        model="gpt-4o",
        user_id="test_user_123",
    )
    ```
    </CodeGroup>

2.  If no `user_id` is passed, the client functions exactly like the original OpenAI client.

3.  By default, memory processing is not immediate. User interactions are collected in a buffer to optimize performance. You can manually trigger processing using the `flush` method:
    ```python
    client.flush("test_user_123")
    ```

## Verifying Memory Retention

Once a user's information is captured, it can be recalled in subsequent, separate conversations.

<CodeGroup>
```python OpenAI (No Memory)
# In a new session
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What is my name?"},
    ],
    model="gpt-4o"
)
# Assistant: "I'm sorry, I don't have access to personal information..."
```
```python OpenAI with Memory
# In a new session
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "What is my name?"},
    ],
    model="gpt-4o",
    user_id="test_user_123",
)
# Assistant: "Your name is Gus."
```
</CodeGroup>

## How It Works

The `openai_memory` function wraps the OpenAI client with two key actions:

1.  **Before Request**: It retrieves the user's memory context from Memobase and injects it into the prompt.
2.  **After Response**: It saves only the **latest** user query and assistant response to the memory buffer.

For example, if your message history is:
```json
[
    {"role": "user", "content": "My name is Gus"},
    {"role": "assistant", "content": "Hello Gus! How can I help you?"},
    {"role": "user", "content": "What is my name?"}
]
```
And the final response is `Your name is Gus.`, Memobase will only store the last exchange. This is equivalent to:
```python
u.insert(
    ChatBlob(messages=[
        {"role": "user", "content": "What is my name?"},
        {"role": "assistant", "content": "Your name is Gus."},
    ])
)
```
This design ensures you can manage short-term conversation history within your API calls as usual, while Memobase prevents duplicate entries in the long-term memory.

The full implementation script is available [here](https://github.com/memodb-io/memobase/blob/main/assets/openai_memory.py).

## Advanced Usage

### Custom Parameters

You can pass additional arguments to `openai_memory` to customize its behavior:

-   `max_context_size`: Controls the maximum token size of the injected memory context. Defaults to `1000`.
    ```python
    client = openai_memory(client, mb_client, max_context_size=500)
    ```
-   `additional_memory_prompt`: Provides a meta-prompt to guide the LLM on how to use the memory.
    ```python
    # Example: Encourage personalization
    prompt = "Always use the user's memory to provide a personalized answer."
    client = openai_memory(client, mb_client, additional_memory_prompt=prompt)
    ```

### Patched Methods

The patched client includes new helper methods:

-   `client.get_memory_prompt("user_id")`: Returns the current memory prompt that will be injected for a given user.
-   `client.flush("user_id")`: Immediately processes the memory buffer for a user. Call this if you need to see memory updates reflected instantly.








=== practices/tips.mdx ===
---
title: Best Practices & Tips
---

This guide provides tips for effectively using Memobase in your applications.

## Configuring User Memory

You can define the structure of user profiles by configuring topics and sub-topics in your `config.yaml` file. This tells Memobase what kind of information to track.

```yaml
- topic: "Gaming"
  description: "Tracks the user's gaming preferences and achievements."
  sub_topics:
      - name: "FPS"
      - name: "LOL"
- topic: "Professional"
  description: "Tracks the user's professional background."
  sub_topics:
    - name: "Industry"
    - name: "Role"
```

Memobase uses this configuration to generate structured user profiles. Learn more about customization at [Profile Configuration](/features/profile/profile_config).

## Integrating Memory into Prompts

There are two primary ways to retrieve and use a user's memory.

### Method 1: Profile API (Manual Assembly)

The [Profile API](/api-reference/profiles/profile) returns a structured JSON object containing the user's profile data. You are responsible for formatting this JSON into a string and inserting it into your prompt.

**Key Considerations:**
-   **Context Length**: Control the token count of the memory context to manage cost and performance. Use `max_token_size` to set a hard limit and `max_subtopic_size` to limit the number of sub-topics per topic.
-   **Topic Filtering**: Use `only_topics` to retrieve specific profile sections or `prefer_topics` to prioritize the most important information.

### Method 2: Context API (Automated Assembly)

The [Context API](/api-reference/prompt/get_context) returns a pre-formatted string containing both the user's profile and recent events, ready to be injected directly into your system prompt. It uses a template like this:

```text
<memory>
# User Profile:
{profile}

# Recent Events:
{event}
</memory>
Use the information in the <memory> tag when relevant.
```

## Flushing the Memory Buffer

Memobase uses a buffer to collect user interactions. A `flush` operation processes this buffer and updates the long-term memory. Flushing occurs automatically when:

-   The buffer exceeds a certain size.
-   The buffer has been idle for a set period.

You can also trigger it manually with the `flush` API. It is best practice to call `flush` at the end of a user session or conversation.

## User ID Management

A single user in your application can correspond to multiple Memobase users. This is useful for creating segmented memories.

-   **Example: AI Role-Playing**: If a user interacts with multiple AI agents (e.g., a history tutor and a creative writer), you can create a separate Memobase user for each agent. This keeps the memories for each role distinct.

We recommend designing your system with a one-to-many mapping between your application's user ID and Memobase user IDs.

## Enriching Conversation Data

You can add metadata to the messages you insert to provide more context for memory extraction.

-   **Speaker Alias**: Use `alias` to specify the name of the AI assistant in the conversation.
    ```json
    {
        "role": "assistant",
        "content": "Hi, nice to meet you, Gus!",
        "alias": "HerAI"
    }
    ```
-   **Timestamps**: Provide a `created_at` timestamp for each message so Memobase can build a timeline of events.
    ```json
    {
        "role": "user",
        "content": "Hello, I'm Gus",
        "created_at": "2025-01-14T10:00:00Z"
    }
    ```

See a full implementation in our [demo script](https://github.com/memodb-io/memobase/blob/main/assets/quickstart.py).

=== quickstart.mdx ===
---
title: 'Quickstart'
---

Ready to give your AI a memory boost? Here’s how to get started.

<CardGroup cols={2}>
  <Card title="Patch OpenAI" icon="webhook" href="practices/openai">
    Upgrade your existing OpenAI setup with Memobase memory.
  </Card>
  <Card title="Client-Side" icon="code-branch" href="#memobase-client">
    Use our SDKs or APIs to connect your app to a Memobase backend.
  </Card>
  <Card title="Server-Side" icon="chart-simple" href="#memobase-backend">
    Deploy your own Memobase backend. It's easier than assembling IKEA furniture.
  </Card>
</CardGroup>


## Memobase Client

### Step 1: Get Prepped

<AccordionGroup>
<Accordion title="Install the SDK">
<CodeGroup>
```bash pip
pip install memobase
```
```bash npm
npm install @memobase/memobase
```
```bash deno
deno add jsr:@memobase/memobase
```

```bash go
go get github.com/memodb-io/memobase/src/client/memobase-go@latest
```

```bash http
# Living on the edge with cURL? Skip to the next step.
```
</CodeGroup>
</Accordion>
<Accordion title="Find Your Project URL and Token">
You'll get these when you set up your [backend](#memobase-backend). Keep them handy.
</Accordion>
</AccordionGroup>

### Step 2: Connect to the Backend

<AccordionGroup>
<Accordion title="Instantiate the Client">
<CodeGroup>
```python Python
from memobase import MemoBaseClient

client = MemoBaseClient(
    project_url=YOUR_PROJECT_URL,
    api_key=YOUR_API_KEY,
)
```
```typescript Node
import { MemoBaseClient, Blob, BlobType } from '@memobase/memobase';

const client = new MemoBaseClient(process.env['MEMOBASE_PROJECT_URL'], process.env['MEMOBASE_API_KEY'])
```

```go Go
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    projectURL := "YOUR_PROJECT_URL"
    apiKey := "YOUR_API_KEY"
    // Initialize the client
    client, err := core.NewMemoBaseClient(
        projectURL,
        apiKey,
    )
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }
}
```
</CodeGroup>
</Accordion>
<Accordion title="Test the Connection (Ping!)">
<CodeGroup>

```python Python
assert client.ping()
```
```typescript Node
const ping = await client.ping()
```
```go Go
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    projectURL := "YOUR_PROJECT_URL"
    apiKey := "YOUR_API_KEY"
    // Initialize the client
    client, err := core.NewMemoBaseClient(
        projectURL,
        apiKey,
    )
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    // Ping the server
    if !client.Ping() {
        log.Fatal("Failed to connect to server")
    }
    fmt.Println("Successfully connected to server")
}
```

```bash cURL
curl -H "Authorization: Bearer $YOUR_API_KEY" "$YOUR_PROJECT_URL/api/v1/healthcheck"
```

```json Output
{"data":null,"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>
</AccordionGroup>

### Step 3: User Management

Create, read, update, and delete users.

<AccordionGroup>
<Accordion title="Create a User">
<CodeGroup>

```python Python
uid = client.add_user({"name": "Gustavo"})
```
```typescript Node
const userId = await client.addUser({name: "Gustavo"})
```
```go Go
import "github.com/google/uuid"

userID := uuid.New().String()
_, err := client.AddUser(map[string]interface{}{"name": "Gustavo"}, userID)
```
```bash cURL
curl -X POST "$YOUR_PROJECT_URL/api/v1/users" \
     -H "Authorization: Bearer $YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"data": {"name": "Gustavo"}}'
```

```json Output
{"data":{"id":"some-unique-user-id"},"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

<Accordion title="Update a User">
<CodeGroup>

```python Python
client.update_user(uid, {"status": "caffeinated"})
```
```typescript Node
await client.updateUser(userId, {status: "caffeinated"})
```
```go Go
_, err = client.UpdateUser(userID, map[string]interface{}{"status": "caffeinated"})
```
```bash cURL
curl -X PUT "$YOUR_PROJECT_URL/api/v1/users/{uid}" \
     -H "Authorization: Bearer $YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"data": {"status": "caffeinated"}}'
```

```json Output
{"data":{"id": "some-unique-user-id"},"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

<Accordion title="Get a User">
<CodeGroup>

```python Python
u = client.get_user(uid)
```

```typescript Node
const user = await client.getUser(userId)
```

```go Go
user, err := client.GetUser(userID, false)
```

```bash cURL
curl -X GET "$YOUR_PROJECT_URL/api/v1/users/{uid}" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```json Output
{"data":{"data":{"name":"Gustavo", "status": "caffeinated"}, ... },"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

<Accordion title="Delete a User">
<CodeGroup>

```python Python
client.delete_user(uid)
```

```typescript Node
await client.deleteUser(userId)
```

```go Go
err = client.DeleteUser(userID)
```

```bash cURL
curl -X DELETE "$YOUR_PROJECT_URL/api/v1/users/{uid}" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```json Output
{"data":null,"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>
</AccordionGroup>

### Step 4: Manage User Data

Now that you have a user, let's give them some memories.

<AccordionGroup>
<Accordion title="Insert Data (e.g. Chats)">
<CodeGroup>

```python Python
from memobase import ChatBlob
b = ChatBlob(messages=[
    {"role": "user", "content": "Hi, I'm here again"},
    {"role": "assistant", "content": "Hi, Gus! How can I help you?"}
])
u = client.get_user(uid)
bid = u.insert(b)
```

```typescript Node
const blobId = await user.insert(Blob.parse({
    type: BlobType.Enum.chat,
    messages: [{
        role: 'user',
        content: 'Hello, how are you?'
    }]
}))
```

```go Go
chatBlob := &blob.ChatBlob{
    Messages: []blob.OpenAICompatibleMessage{
        {Role: "user", Content: "Hello, I am Jinjia!"},
        {Role: "assistant", Content: "Hi there! How can I help you today?"},
    },
}
blobID, err := user.Insert(chatBlob, false)
```

```bash cURL
curl -X POST "$YOUR_PROJECT_URL/api/v1/blobs/insert/{uid}" \
     -H "Authorization: Bearer $YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{ "blob_type": "chat", "blob_data": { "messages": [ {"role": "user","content": "Hi, Im here again"}, {"role": "assistant", "content": "Hi, Gus! How can I help you?"}] }}'
```

```json Output
{"data":{"id":"some-unique-blob-id"},"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

<Accordion title="Get Data">
<CodeGroup>

```python Python
b = u.get(bid)
```

```typescript Node
const blob = await user.get(blobId)
```

```go Go
blob, err := user.Get(blobID)
```

```bash cURL
curl -X GET "$YOUR_PROJECT_URL/api/v1/blobs/{uid}/{bid}" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```json Output
{"data":{"blob_type":"chat", "blob_data":{...}},"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

<Accordion title="Delete Data">
<CodeGroup>

```python Python
u.delete(bid)
```

```typescript Node
await user.delete(blobId)
```

```go Go
err := user.Delete(blobID)
```

```bash cURL
curl -X DELETE "$YOUR_PROJECT_URL/api/v1/blobs/{uid}/{bid}" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```json Output
{"data":null,"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>
</AccordionGroup>

### Step 5: Memory Operations

This is where the magic happens. Memobase extracts and stores memories for each user.

1.  **`flush`**: User data is held in a buffer. If the buffer gets too large or remains idle, it gets processed. You can also trigger this manually.

<Accordion title="Flush (e.g., after a chat session ends)">
<CodeGroup>

```python Python
u.flush()
```

```typescript Node
await user.flush(BlobType.Enum.chat)
```

```go Go
err := user.Flush(blob.ChatType, false)
```

```bash cURL
curl -X POST "$YOUR_PROJECT_URL/api/v1/users/buffer/{uid}/chat" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```json Output
{"data":null,"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

2.  **`profile`**: Get the memory profile of a user.

<Accordion title="Get User Profile">
<CodeGroup>

```python Python
u.profile()
```

```typescript Node
const profiles = await user.profile()
```

```go Go
profiles, err := user.Profile(nil)
```

```bash cURL
curl -X GET "$YOUR_PROJECT_URL/api/v1/users/profile/{uid}" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```json Output
{"data":{"profiles":[ {"content":"Gus", "attributes":{}}, ... ]},"errno":0,"errmsg":""}
```
</CodeGroup>
</Accordion>

3.  **Form a [personalized memory prompt](/features/context)**:

<Accordion title="Example Personalized Prompt">
<CodeGroup>

```python Python
u.context()
```

```typescript Node
const context = await user.context();
```

```go Go
context, err := user.Context(nil)
```

```bash cURL
curl -X GET "$YOUR_PROJECT_URL/api/v1/users/context/{uid}" \
     -H "Authorization: Bearer $YOUR_API_KEY"
```

```txt Output
# Memory
Unless the user has relevant queries, do not actively mention those memories in the conversation.
## User Background:
- basic_info:name: Gus
- basic_info:location: San Francisco
...

## Latest Events:
- Gus went to the gym [mentioned on 2024-01-02]
- Gus had a coffee with his friend [mentioned on 2024-01-01]
...
```
</CodeGroup>
</Accordion>


## Memobase Backend
We offer an [open-source solution](https://github.com/memodb-io/memobase) with a Docker backend to launch your own instance.
You can use `docker-compose` to launch the backend [in one command](https://github.com/memodb-io/memobase/blob/main/src/server/readme.md#get-started).


## Memobase Cloud
We also offer a [hosted cloud service](https://www.memobase.io/), with free tier and nice dashboard.

<Frame caption="Memobase Cloud Dashboard">
  <video
  autoPlay
  muted
  loop
  playsInline
  src="https://github.com/user-attachments/assets/eb2eea30-48bc-4714-9706-e417ae1931df"
></video>
</Frame>

=== references/async_client.mdx ===
---
title: Async Python Client
---

Memobase also provides an async client in `python` SDK, it just the same as the sync client, but every method is async:
```python
from memobase import AsyncMemobaseClient

client = AsyncMemobaseClient(api_key="your_api_key")

async def main():
    assert await client.ping()
    #...
    
    # get user context
    u = await client.get_user(UID)
    print(await u.context())

    # get user profile
    print(await u.profile())

    # get user events
    print(await u.event(topk=10, max_token_size=1000))
```

=== references/cloud_config.mdx ===
---
title: Cloud Configuration
---

If you're using Memobase on cloud, you can refer to those sections to configure your memory backend:
- [User Profile](/features/profile)
- [User Event](/features/event)


In Memobase Cloud, we don't accept any LLM/Embedding model configuration for security reasons, all the LLM/Embedding costs are counted into [Memobase Tokens](https://www.memobase.io/pricing).

=== references/local_config.mdx ===
---
title: Self-Hosted Configuration
---
If you develop Memobase locally, you can use a `config.yaml` file to configure Memobase Backend.
## Full Explanation of `config.yaml`
We use a single `config.yaml` file as the source to configure Memobase Backend. An example is like this:

```yaml
# Storage and Performance
persistent_chat_blobs: false
buffer_flush_interval: 3600
max_chat_blob_buffer_token_size: 1024
max_profile_subtopics: 15
max_pre_profile_token_size: 128
cache_user_profiles_ttl: 1200

# Timezone
use_timezone: "UTC"

# LLM Configuration
language: "en"
llm_style: "openai"
llm_base_url: "https://api.openai.com/v1/"
llm_api_key: "YOUR-KEY"
best_llm_model: "gpt-4o-mini"
summary_llm_model: null

# Embedding Configuration
enable_event_embedding: true
embedding_provider: "openai"
embedding_api_key: null
embedding_base_url: null
embedding_dim: 1536
embedding_model: "text-embedding-3-small"
embedding_max_token_size: 8192

# Profile Configuration
additional_user_profiles:
  - topic: "gaming"
    sub_topics:
      - "Soul-Like"
      - "RPG"
profile_strict_mode: false
profile_validate_mode: true

# Summary Configuration
minimum_chats_token_size_for_event_summary: 256
```

## Configuration Categories

### Storage and Performance
- `persistent_chat_blobs`: boolean, default to `false`. If set to `true`, the chat blobs will be persisted in the database.
- `buffer_flush_interval`: int, default to `3600` (1 hour). Controls how frequently the chat buffer is flushed to persistent storage.
- `max_chat_blob_buffer_token_size`: int, default to `1024`. This is the parameter to control the buffer size of Memobase. Larger numbers lower your LLM cost but increase profile update lag.
- `max_profile_subtopics`: int, default to `15`. The maximum subtopics one topic can have. When a topic has more than this, it will trigger a re-organization.
- `max_pre_profile_token_size`: int, default to `128`. The maximum token size of one profile slot. When a profile slot is larger, it will trigger a re-summary.
- `cache_user_profiles_ttl`: int, default to `1200` (20 minutes). Time-to-live for cached user profiles in seconds.
- `llm_tab_separator`: string, default to `"::"`. The separator used for tabs in LLM communications.

### Timezone Configuration
- `use_timezone`: string, default to `null`. Options include `"UTC"`, `"America/New_York"`, `"Europe/London"`, `"Asia/Tokyo"`, and `"Asia/Shanghai"`. If not set, the system's local timezone is used.

### LLM Configuration
- `language`: string, default to `"en"`, available options `{"en", "zh", "ja"}`. The prompt language of Memobase.
- `llm_style`: string, default to `"openai"`, available options `{"openai", "doubao_cache"}`. The LLM provider style.
- `llm_base_url`: string, default to `null`. The base URL of any OpenAI-Compatible API.
- `llm_api_key`: string, required. Your LLM API key.
- `llm_openai_default_query`: dictionary, default to `null`. Default query parameters for OpenAI API calls.
- `llm_openai_default_header`: dictionary, default to `null`. Default headers for OpenAI API calls.
- `best_llm_model`: string, default to `"gpt-4o-mini"`. The AI model to use for primary functions.
- `summary_llm_model`: string, default to `null`. The AI model to use for summarization. If not specified, falls back to `best_llm_model`.
- `system_prompt`: string, default to `null`. Custom system prompt for the LLM.

### Embedding Configuration
- `enable_event_embedding`: boolean, default to `true`. Whether to enable event embedding.
- `embedding_provider`: string, default to `"openai"`, available options `{"openai", "jina"}`. The embedding provider to use.
- `embedding_api_key`: string, default to `null`. If not specified and provider is OpenAI, falls back to `llm_api_key`.
- `embedding_base_url`: string, default to `null`. For Jina, defaults to `"https://api.jina.ai/v1"` if not specified.
- `embedding_dim`: int, default to `1536`. The dimension size of the embeddings.
- `embedding_model`: string, default to `"text-embedding-3-small"`. For Jina, must be `"jina-embeddings-v3"`.
- `embedding_max_token_size`: int, default to `8192`. Maximum token size for text to be embedded.

### Profile Configuration
Check what a profile is in Memobase [here](/features/customization/profile).
- `additional_user_profiles`: list, default to `[]`. Add additional user profiles. Each profile should have a `topic` and a list of `sub_topics`.
  - For `topic`, it must have a `topic` field and optionally a `description` field:
  ```yaml
  additional_user_profiles:
    - topic: "gaming"
      # description: "User's gaming interests"
      sub_topics:
        ...
  ```
  - For each `sub_topic`, it must have a `name` field (or just be a string) and optionally a `description` field:
  ```yaml
  sub_topics:
    - "SP1"
    - name: "SP2"
      description: "Sub-Profile 2" 
  ```
- `overwrite_user_profiles`: list, default to `null`. Format is the same as `additional_user_profiles`.
  Memobase has built-in profile slots like `work_title`, `name`, etc. For full control of the slots, use this parameter.
  The final profile slots will be only those defined here.
- `profile_strict_mode`: boolean, default to `false`. Enforces strict validation of profile structure.
- `profile_validate_mode`: boolean, default to `true`. Enables validation of profile data.

### Summary Configuration
- `minimum_chats_token_size_for_event_summary`: int, default to `256`. Minimum token size required to trigger an event summary.
- `event_tags`: list, default to `[]`. Custom event tags for classification.

### Telemetry Configuration
- `telemetry_deployment_environment`: string, default to `"local"`. The deployment environment identifier for telemetry.

## Environment Variable Overrides

All configuration values can be overridden using environment variables. The naming convention is to prefix the configuration field name with `MEMOBASE_` and convert it to uppercase.

For example, to override the `llm_api_key` configuration:

```bash
export MEMOBASE_LLM_API_KEY="your-api-key-here"
```

This is particularly useful for:
- Keeping sensitive information like API keys out of configuration files
- Deploying to different environments (development, staging, production)
- Containerized deployments where environment variables are the preferred configuration method

For complex data types (lists, dictionaries, etc.), you can use JSON-formatted strings:

```bash
# Override additional_user_profiles with a JSON array
export MEMOBASE_ADDITIONAL_USER_PROFILES='[{"topic": "gaming", "sub_topics": ["RPG", "Strategy"]}]'
```

The server will automatically parse JSON-formatted environment variables when appropriate.


=== snippets/snippet-intro.mdx ===
One of the core principles of software development is DRY (Don't Repeat
Yourself). This is a principle that apply to documentation as
well. If you find yourself repeating the same content in multiple places, you
should consider creating a custom snippet to keep your content in sync.


=== templates/dify.mdx ===
---
title: Dify Plugin for Long-Term Memory
---

Enhance your Dify applications with long-term memory by integrating the Memobase plugin. This guide will walk you through setting up and using the plugin to create more intelligent, context-aware AI agents.

## Prerequisites

First, find and install the open-source [Memobase plugin](https://github.com/ACAne0320/dify-plugin-memobase) from the Dify plugin marketplace.

<Frame caption="Memobase Plugin in the Dify Marketplace">
  <img src="/images/dify_memobase_marketplace.png" />
</Frame>

Next, you'll need a Memobase instance:

-   **Memobase Cloud**: The easiest way to get started is by signing up for a managed instance on the [Memobase dashboard](https://www.memobase.io/en/dashboard).
-   **Self-Hosted**: For more control, you can deploy your own instance. See the [Memobase GitHub repository](https://github.com/memodb-io/memobase) for instructions.

## Plugin Configuration

To connect the plugin to your Memobase instance, you need to provide two credentials when adding the tool to your Dify application:

1.  **Memobase URL**: The API endpoint for your instance (e.g., `https://api.memobase.dev`).
2.  **Memobase API Key**: Your unique API key for authentication.

You can find both of these in your Memobase dashboard.

<Frame caption="API Key and URL in the Memobase Dashboard">
  <img src="/images/dify_memobase_dashboard.png" />
</Frame>

## Using the Plugin in Dify Workflows

Once configured, you can use the plugin's tools in your Dify workflows to:

-   **Store and Recall Conversations**: Persist dialogue for long-term context.
-   **Personalize Responses**: Retrieve user profiles to tailor interactions.
-   **Access Past Events**: Search and utilize historical user data.
-   **Manage Memory**: Directly manipulate data within your Memobase instance from Dify.

For detailed information on each tool, refer to the [Memobase API Reference](/api-reference/overview).

### Example Workflow

Here is a conceptual example of a Dify workflow that uses the Memobase plugin to retrieve and store memory:

<Frame caption="A minimal Dify workflow demonstrating memory retrieval and storage.">
  <img src="/images/dify_memobase_workflow.png" />
</Frame>

By integrating Memobase, you can build sophisticated AI applications that learn from and remember past interactions, leading to more engaging and personalized user experiences.

=== templates/livekit.mdx ===
---
title: Building a Voice Agent with LiveKit and Memobase
---

> [Full Code](https://github.com/memodb-io/memobase/tree/dev/assets/tutorials/livekit%2Bmemobase)

This tutorial demonstrates how to build a voice agent with long-term memory using Memobase and LiveKit. This combination is ideal for applications like AI companions, customer support bots, and more.

## Setup

1.  **Get API Keys**:
    -   **Memobase**: Sign up at [Memobase](https://www.memobase.io/en) or [run a local server](/references/local_config).
    -   **LiveKit**: Get your `LIVEKIT_URL`, `API_KEY`, and `API_SECRET` from the [LiveKit Cloud Console](https://cloud.livekit.io/).
    -   **Deepgram**: Get your `DEEPGRAM_API_KEY` from the [Deepgram Console](https://console.deepgram.com/).

2.  **Environment Variables**: Set up your environment variables.

    ```bash
    OPENAI_API_KEY="your_openai_api_key"
    DEEPGRAM_API_KEY="your_deepgram_api_key"
    LIVEKIT_URL="your_livekit_url"
    LIVEKIT_API_KEY="your_livekit_api_key"
    LIVEKIT_API_SECRET="your_livekit_api_secret"
    MEMOBASE_URL="https://api.memobase.io"
    MEMOBASE_API_KEY="your_memobase_api_key"
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Code Breakdown

The full code is available [here](https://github.com/memodb-io/memobase/tree/dev/assets/tutorials/livekit%2Bmemobase/livekit_example.py). We will be using the [LiveKit Agents SDK v1.0](https://docs.livekit.io/agents/build/).

The core of the integration involves subclassing the `livekit.agents.Agent` class and overriding the `llm_node` method to inject memory context from Memobase.

### Agent Initialization

First, we initialize the Memobase client and define our custom agent class.

```python
import os
from dotenv import load_dotenv
from livekit.agents import Agent, llm
from memobase import AsyncMemoBaseClient, ChatBlob
from memobase.utils import string_to_uuid

load_dotenv()
mb_client = AsyncMemoBaseClient(
    api_key=os.getenv("MEMOBASE_API_KEY"), project_url=os.getenv("MEMOBASE_URL")
)

class RAGEnrichedAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="You are a warm-hearted partner who remembers past interactions.",
        )
        self.user_name = os.getenv("MEMOBASE_USER_NAME", "test_user")
        self.chat_log_index = 1
```

### Injecting Memory

Next, we override the `llm_node` method. This method is called just before the chat history is sent to the LLM. Here, we will retrieve the user's memory from Memobase and add it to the system prompt.

```python
async def llm_node(
    self,
    chat_ctx: llm.ChatContext,
    # ... other params
) -> AsyncIterable[llm.ChatChunk]:
    # Ensure Memobase is reachable
    assert await mb_client.ping(), "Memobase is not reachable"
    
    # Get or create the user in Memobase
    user = await mb_client.get_or_create_user(string_to_uuid(self.user_name))

    # Insert new messages into memory
    if len(chat_ctx.items) > self.chat_log_index:
        new_messages = chat_ctx.items[self.chat_log_index : len(chat_ctx.items) - 1]
        if len(new_messages):
            blob = ChatBlob(
                messages=[
                    {"role": m.role, "content": m.content[0]}
                    for m in new_messages
                    if m.role in ["user", "assistant"]
                ]
            )
            await user.insert(blob)
            await user.flush()
            self.chat_log_index = len(chat_ctx.items) - 1

    # Retrieve memory context and add to chat history
    rag_context: str = await user.context(max_token_size=500)
    chat_ctx.add_message(content=rag_context, role="system")
    
    # Call the default LLM node
    return Agent.default.llm_node(self, chat_ctx, tools, model_settings)
```

The `rag_context` string will contain the user's [profile](/features/profile/) and recent [events](/features/event/), formatted and ready to be used by the LLM.

### Running the Agent

Finally, we set up the entry point to run the agent.

```python
async def entrypoint(ctx: JobContext):
    # ... (connect to room, set up STT, TTS, etc.)
    await session.start(
        agent=RAGEnrichedAgent(),
        # ...
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
```

To run the code, first download the necessary assets:
```bash
python livekit_example.py download-files
```

Then, start the agent:
```bash
python livekit_example.py console
```

You can now have a conversation with the voice agent. It will remember information you provide across different sessions.




=== templates/mcp.mdx ===
---
title: Memobase and the Model Context Protocol (MCP)
---

> [Full Code](https://github.com/memodb-io/memobase/tree/dev/src/mcp)

This tutorial explains how to integrate Memobase with the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) to provide your AI agents with persistent, long-term memory. By using the Memobase MCP server, your agents can store, retrieve, and search memories, making them stateful and context-aware across conversations.

## What is MCP?

The Model Context Protocol is an open standard that allows AI assistants to securely connect to external data sources and tools. This enables them to access real-time information, execute functions, and maintain a persistent state, breaking free from the limitations of their training data.

## Why Memobase + MCP?

Traditional AI conversations are stateless. The Memobase MCP server changes this by providing:

1.  **Persistent Memory**: Store conversation history and user preferences across sessions.
2.  **Semantic Search**: Find relevant context using natural language queries.
3.  **User Profiles**: Build a comprehensive understanding of users over time.
4.  **Cross-Platform Compatibility**: Works with any MCP-compatible client, such as Claude Desktop, Cursor, or Windsurf.

## Setup

### Prerequisites

-   Python 3.11+
-   A Memobase backend (either [local](/references/local_config) or [cloud](https://www.memobase.io/en))

### Installation

We recommend using `uv` for installation:

```bash
# Install uv if you don't have it
pip install uv

# Clone the repository
git clone https://github.com/memodb-io/memobase
cd memobase/src/mcp

# Install dependencies
uv pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your Memobase credentials
```

### Environment Configuration

Configure your `.env` file:

```bash
TRANSPORT=sse
HOST=0.0.0.0
PORT=8050
MEMOBASE_API_KEY="your_api_key_here"
MEMOBASE_BASE_URL="https://api.memobase.dev"
```

## Running the MCP Server

Start the server using `uv`:

```bash
uv run src/main.py
```

The server will be available at `http://localhost:8050` with an SSE endpoint at `/sse`.

## Client Integration

Configure your MCP client to connect to the Memobase server. For example, in Cursor, add this to your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "memobase": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

## Available Tools

The Memobase MCP server exposes three powerful tools to your AI agent.

### 1. `save_memory`

Stores information in long-term memory with semantic indexing.

```python
# Example usage in your AI agent
await save_memory("User prefers dark mode and uses Python for backend development.")
```

### 2. `search_memories`

Finds relevant context using natural language queries.

```python
# Search for relevant memories
context = await search_memories("What are the user's programming language preferences?")
```

### 3. `get_user_profiles`

Retrieves a comprehensive, structured user profile.

```python
# Get the full user profile
profiles = await get_user_profiles()
```

## Real-World Example

**Without Memory:**

> **User**: "I prefer Python for backend development."
> **AI**: "That's great! Python is excellent for backend work."
> 
> *Later...*
> 
> **User**: "What's the best language for my new API?"
> **AI**: "There are many options, like Python, Node.js, or Go..."

**With Memobase MCP:**

> **User**: "I prefer Python for backend development."
> **AI**: "Got it. I'll remember your preference for Python."
> *(Memory saved: "User prefers Python for backend development")*
> 
> *Later...*
> 
> **User**: "What's the best language for my new API?"
> **AI**: *(Searches memories)* "Based on your preference for Python, I'd recommend using FastAPI or Django."

## Conclusion

The Memobase MCP server transforms stateless AI interactions into intelligent, context-aware conversations. By providing persistent memory through a standardized protocol, you can build AI applications that learn, remember, and deliver truly personalized experiences.


=== templates/ollama.mdx ===
---
title: Using Memobase with Ollama
---

> [Full Code](https://github.com/memodb-io/memobase/tree/dev/assets/tutorials/ollama%2Bmemobase)

Memobase supports any OpenAI-compatible LLM provider as its backend. This tutorial demonstrates how to use [Ollama](https://ollama.com/) to run a local LLM for both the Memobase server and your chat application.

## Setup

### 1. Configure Ollama

-   [Install Ollama](https://ollama.com/download) on your local machine.
-   Verify the installation by running `ollama -v`.
-   Pull a model to use. For this example, we'll use `qwen2.5:7b`.
    ```bash
    ollama pull qwen2.5:7b
    ```

### 2. Configure Memobase

To use a local LLM provider with the Memobase server, you need to modify your `config.yaml` file.

<Tip>Learn more about [`config.yaml`](/references/cloud_config).</Tip>

Set the following fields to point to your local Ollama instance:

```yaml config.yaml
llm_api_key: ollama
llm_base_url: http://host.docker.internal:11434/v1
best_llm_model: qwen2.5:7b
```

**Note**: Since the Memobase server runs in a Docker container, we use `host.docker.internal` to allow it to access the Ollama server running on your local machine at port `11434`.

## Code Breakdown

This example uses Memobase's [OpenAI Memory Patch](/practices/openai) for a clear demonstration.

### Client Initialization

First, we set up the OpenAI client to point to our local Ollama server and then apply the Memobase memory patch.

```python
from memobase import MemoBaseClient
from openai import OpenAI
from memobase.patch.openai import openai_memory

# Point the OpenAI client to the local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

# Initialize the Memobase client
mb_client = MemoBaseClient(
    project_url="http://localhost:8019", # Assuming local Memobase server
    api_key="secret",
)

# Apply the memory patch
client = openai_memory(client, mb_client)
```

After patching, your OpenAI client is now stateful. It will automatically manage memory for each user, recalling information from past conversations.

### Chat Function

Next, we create a chat function that uses the patched client. The key is to pass a `user_id` to trigger the memory functionality.

```python
def chat(message, user_id=None, close_session=False):
    print(f"Q: {message}")
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": message}],
        model="qwen2.5:7b",
        stream=True,
        user_id=user_id, # Pass user_id to enable memory
    )
    
    # Display the response
    for chunk in response:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()

    # Flush the memory buffer at the end of a session
    if close_session and user_id:
        client.flush(user_id)
```

### Testing the Memory

Now, you can test the difference between a stateless and a stateful conversation:

```python
# --- Without Memory ---
print("-- Ollama without memory --")
chat("My name is Gus.")
chat("What is my name?") # The model won't know

# --- With Memory ---
print("\n--- Ollama with memory ---")
user = "gus_123"
chat("My name is Gus.", user_id=user, close_session=True)

# In a new conversation, the model remembers
chat("What is my name?", user_id=user)
```

For the complete code, see the [full example on GitHub](https://github.com/memodb-io/memobase/tree/dev/assets/tutorials/ollama%2Bmemobase).


=== templates/openai.mdx ===
---
title: OpenAI Client with User Memory
---

A key feature of Memobase is its ability to remember user preferences from conversation history. This tutorial demonstrates how to integrate this memory capability directly into the OpenAI client.

While Memobase offers a simple [patch](/practices/openai) for this, the following sections provide a detailed breakdown of the implementation.

## Setup

1.  **Get API Keys**: Obtain an API key from [Memobase](https://www.memobase.io/en) or run a [local server](https://github.com/memodb-io/memobase/tree/dev/src/server).
2.  **Configure Environment Variables**:
    ```bash
    OPENAI_API_KEY="your_openai_api_key"
    MEMOBASE_URL="https://api.memobase.dev"
    MEMOBASE_API_KEY="your_memobase_api_key"
    ```
3.  **Install Dependencies**:
    ```bash
    pip install openai memobase
    ```

## Code Breakdown

<Frame caption="Diagram of OpenAI API with Memory">
  <img src="/images/openai_client.png" />
</Frame>

The implementation involves three main steps:
1.  **Wrap the OpenAI client**: This allows us to intercept chat messages and inject memory context into prompts.
2.  **Integrate Memobase APIs**: Use the wrappers to store chat history and retrieve user memories.
3.  **Test**: Verify that the memory feature functions correctly.

> You can find the [full source code](https://github.com/memodb-io/memobase/blob/main/src/client/memobase/patch/openai.py) on GitHub.

### Basic Setup

First, initialize the OpenAI and Memobase clients.

```python
import os
from memobase import MemoBaseClient
from openai import OpenAI

client = OpenAI()
mb_client = MemoBaseClient(
    api_key=os.getenv("MEMOBASE_API_KEY"),
    project_url=os.getenv("MEMOBASE_URL"),
)
```

### Wrapping the OpenAI Client

We use duck typing to wrap the OpenAI client. This approach avoids altering the original client's class structure.

```python
def openai_memory(
    openai_client: OpenAI | AsyncOpenAI,
    mb_client: MemoBaseClient
) -> OpenAI | AsyncOpenAI:
    if hasattr(openai_client, "_memobase_patched"):
        return openai_client
    openai_client._memobase_patched = True
    openai_client.chat.completions.create = _sync_chat(
        openai_client, mb_client
    )
```

This simplified code does two things:
- It checks if the client has already been patched to prevent applying the wrapper multiple times.
- It replaces the standard `chat.completions.create` method with our custom `_sync_chat` function, which will contain the memory logic.

### The New `chat.completions.create` Method

Our new `chat.completions.create` method must meet several requirements:
- Accept a `user_id` to enable user-specific memory.
- Support all original arguments to ensure backward compatibility.
- Return the same data types, including support for streaming.
- Maintain performance comparable to the original method.

First, we ensure that calls without a `user_id` are passed directly to the original method.

```python
def _sync_chat(
    client: OpenAI,
    mb_client: MemoBaseClient,
):
    # Save the original create method
    _create_chat = client.chat.completions.create
    def sync_chat(*args, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
        is_streaming = kwargs.get("stream", False)
        # If no user_id, call the original method
        if "user_id" not in kwargs:
            return _create_chat(*args, **kwargs)

        # Pop user_id and convert it to UUID for Memobase
        user_id = string_to_uuid(kwargs.pop("user_id"))
        ...

    return sync_chat
```
The wrapper passes all arguments (`*args`, `**kwargs`) to the original function, preserving its behavior. Memobase uses UUIDs to identify users, so we convert the provided `user_id` (which can be any string) into a UUID.

If a `user_id` is present, the workflow is:
1.  Get or create the user in Memobase.
2.  Inject the user's memory context into the message list.
3.  Call the original `create` method with the modified messages.
4.  Save the new conversation to Memobase for future recall.

Here is the implementation logic:
```python
def _sync_chat(client: OpenAI, mb_client: MemoBaseClient):
    _create_chat = client.chat.completions.create

    def sync_chat(*args, **kwargs) -> ChatCompletion | Stream[ChatCompletionChunk]:
        # ... existing code for handling no user_id ...
        user_query = kwargs["messages"][-1]
        if user_query["role"] != "user":
            LOG.warning(f"Last message is not from the user: {user_query}")
            return _create_chat(*args, **kwargs)

        # 1. Get or create user
        u = mb_client.get_or_create_user(user_id)

        # 2. Inject user context
        kwargs["messages"] = user_context_insert(
            kwargs["messages"], u
        )

        # 3. Call original method
        response = _create_chat(*args, **kwargs)

        # 4. Save conversation (details below)
        # ... handle streaming and non-streaming cases
```

### Enhancing Messages with User Context

The `user_context_insert` function injects the user's memory into the prompt.

```python
PROMPT = '''

--# ADDITIONAL INFO #--
{user_context}
{additional_memory_prompt}
--# DONE #--'''

def user_context_insert(
    messages, u: User, additional_memory_prompt: str="", max_context_size: int = 750
):
    # Retrieve user's memory from Memobase
    context = u.context(max_token_size=max_context_size)
    if not context:
        return messages

    # Format the context into a system prompt
    sys_prompt = PROMPT.format(
        user_context=context, additional_memory_prompt=additional_memory_prompt
    )

    # Add the context to the list of messages
    if messages and messages[0]["role"] == "system":
        messages[0]["content"] += sys_prompt
    else:
        messages.insert(0, {"role": "system", "content": sys_prompt.strip()})
    return messages
```
This function retrieves the user's context from Memobase, formats it into a special system prompt, and prepends it to the message list sent to OpenAI.

### Saving Conversations

After receiving a response from OpenAI, we save the conversation to Memobase to build the user's memory. This is done asynchronously using a background thread to avoid blocking.

```python
def add_message_to_user(messages: ChatBlob, user: User):
    try:
        user.insert(messages)
        LOG.debug(f"Inserted messages for user {user.id}")
    except ServerError as e:
        LOG.error(f"Failed to insert messages: {e}")
```

#### Non-Streaming Responses

For standard responses, we extract the content and save it.

```python
# Non-streaming case
response_content = response.choices[0].message.content
messages = ChatBlob(
    messages=[
        {"role": "user", "content": user_query["content"]},
        {"role": "assistant", "content": response_content},
    ]
)
threading.Thread(target=add_message_to_user, args=(messages, u)).start()
```

#### Streaming Responses

For streaming, we yield each chunk as it arrives and accumulate the full response. Once the stream is complete, we save the entire conversation.

```python
# Streaming case
def yield_response_and_log():
    full_response = ""
    for chunk in response:
        yield chunk
        content = chunk.choices[0].delta.content
        if content:
            full_response += content

    # Save the complete conversation after streaming finishes
    messages = ChatBlob(
        messages=[
            {"role": "user", "content": user_query["content"]},
            {"role": "assistant", "content": full_response},
        ]
    )
    threading.Thread(target=add_message_to_user, args=(messages, u)).start()
```

### Utility Functions

The patch also adds several helper functions to the client for managing user memory:

```python
# Get a user's profile
def _get_profile(mb_client: MemoBaseClient):
    def get_profile(user_string: str) -> list[UserProfile]:
        uid = string_to_uuid(user_string)
        return mb_client.get_user(uid, no_get=True).profile()
    return get_profile

# Get the formatted memory prompt for a user
def _get_memory_prompt(mb_client: MemoBaseClient, ...):
    def get_memory(user_string: str) -> str:
        uid = string_to_uuid(user_string)
        u = mb_client.get_user(uid, no_get=True)
        context = u.context(...)
        return PROMPT.format(user_context=context, ...)
    return get_memory

# Clear a user's memory
def _flush(mb_client: MemoBaseClient):
    def flush(user_string: str):
        uid = string_to_uuid(user_string)
        return mb_client.get_user(uid, no_get=True).flush()
    return flush
```
These functions provide direct access to get a user's profile, retrieve the generated memory prompt, or clear a user's history in Memobase.

## Usage Example

Here’s how to use the patched OpenAI client.

```python
import os
from openai import OpenAI
from memobase import MemoBaseClient
from memobase.patch import openai_memory

# 1. Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
mb_client = MemoBaseClient(
    api_key=os.getenv("MEMOBASE_API_KEY"),
    project_url=os.getenv("MEMOBASE_URL"),
)

# 2. Patch the OpenAI client
memory_client = openai_memory(openai_client, mb_client)

# 3. Use the patched client with a user_id
# The first time, the AI won't know the user's name.
response = memory_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hi, do you know my name?"}],
    user_id="john_doe"  # Can be any string identifier
)
print(response.choices[0].message.content)
# Expected output: "I'm sorry, I don't know your name."
```

Now, let's inform the AI of the user's name and see if it remembers.

```python
# Tell the AI the user's name
memory_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "My name is John Doe."}],
    user_id="john_doe"
)

# Start a new conversation and ask again
response = memory_client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's my name?"}],
    user_id="john_doe"
)

print(response.choices[0].message.content)
# Expected output: "Your name is John Doe."
```
Because the conversation history is now stored in Memobase, the AI can recall the user's name in subsequent, separate conversations.

## Conclusion

This guide demonstrates a powerful method for adding persistent user memory to the OpenAI client. The patched client:

- **Is fully compatible**: It works identically to the original client.
- **Enables memory**: Adds memory capabilities when a `user_id` is provided.
- **Supports all modes**: Handles both streaming and non-streaming responses.
- **Is automatic**: Seamlessly saves conversations and injects context without extra code.

This approach offers a clean and non-intrusive way to build personalized, stateful AI experiences into your existing OpenAI applications.







