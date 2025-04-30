API_X_CODE_DOCS = {}


API_X_CODE_DOCS["GET /healthcheck"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

assert memobase.ping()
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

await client.ping();
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

ok := client.Ping()
if !ok {
    panic("Failed to connect to Memobase")
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["GET /project/billing"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

print(memobase.get_usage())
""",
            "label": "Python",
        },
    ]
}

API_X_CODE_DOCS["POST /project/profile_config"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

memobase.update_config('your_profile_config')
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

await client.updateConfig('your_profile_config');
""",
            "label": "JavaScript",
        },
    ]
}

API_X_CODE_DOCS["GET /project/profile_config"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

config = memobase.get_config()
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

const config = await client.getConfig();
""",
            "label": "JavaScript",
        },
    ]
}

API_X_CODE_DOCS["POST /users"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

uid = client.add_user({"ANY": "DATA"})
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

const userId = await client.addUser({ANY: "DATA"});
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
    "github.com/google/uuid"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Generate a UUID for the user
userID := uuid.New().String()

// Create user with some data
data := map[string]interface{}{"ANY": "DATA"}
resultID, err := client.AddUser(data, userID)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["GET /users/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

u = client.get_user(uid)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

const user = await client.getUser(userId);
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user by ID
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["PUT /users/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

client.update_user(uid, {"ANY": "NEW_DATA"})
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

await client.updateUser(userId, {ANY: "NEW_DATA"});
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Update user data
newData := map[string]interface{}{"ANY": "NEW_DATA"}
err = client.UpdateUser(userID, newData)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["DELETE /users/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

client.delete_user(uid)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

await client.deleteUser(userId);
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Delete user
err = client.DeleteUser(userID)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["GET /users/blobs/{user_id}/{blob_type}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase
from memobase.core.blob import BlobType

memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

user = memobase.get_user('user_id')
blobs = user.get_all(BlobType.CHAT)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient, BlobType } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

const user = client.getUser('user_id');
const blobs = await user.getAll(BlobType.Enum.chat);
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
    "github.com/memodb-io/memobase/src/client/memobase-go/blob"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Get all blobs
blobs, err := user.GetAll(blob.ChatType)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["POST /blobs/insert/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase
from memobase import ChatBlob

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

b = ChatBlob(messages=[
    {
        "role": "user",
        "content": "Hi, I'm here again"
    },
    {
        "role": "assistant",
        "content": "Hi, Gus! How can I help you?"
    }
])
u = client.get_user(uid)
bid = u.insert(b)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient, Blob, BlobType } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

const blobId = await user.insert(Blob.parse({
  type: BlobType.Enum.chat,
  messages: [
    {
      role: 'user',
      content: 'Hi, I\'m here again'
    },
    {
      role: 'assistant',
      content: 'Hi, Gus! How can I help you?'
    }
  ]
}));
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
    "github.com/memodb-io/memobase/src/client/memobase-go/blob"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Create chat blob
chatBlob := &blob.ChatBlob{
    BaseBlob: blob.BaseBlob{
        Type: blob.ChatType,
    },
    Messages: []blob.OpenAICompatibleMessage{
        {
            Role:    "user",
            Content: "Hi, I'm here again",
        },
        {
            Role:    "assistant",
            Content: "Hi, Gus! How can I help you?",
        },
    },
}

// Insert blob
blobID, err := user.Insert(chatBlob)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["GET /blobs/{user_id}/{blob_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

u = client.get_user(uid)
b = u.get(bid)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

const blob = await user.get(blobId);
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
    "github.com/memodb-io/memobase/src/client/memobase-go/blob"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Get blob
blob, err := user.Get(blobID)
if err != nil {
    panic(err)
}

// If it's a chat blob, you can access its messages
if chatBlob, ok := blob.(*blob.ChatBlob); ok {
    messages := chatBlob.Messages
    // Process messages
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["DELETE /blobs/{user_id}/{blob_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

u = client.get_user(uid)
u.delete(bid)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

await user.delete(blobId);
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Delete blob
err = user.Delete(blobID)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["GET /users/profile/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

u = client.get_user(uid)
p = u.profile()
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

const profiles = await user.profile();
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Get profile
profiles, err := user.Profile()
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["POST /users/buffer/{user_id}/{buffer_type}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

u.flush()
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient, BlobType } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

await user.flush(BlobType.Enum.chat);
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
    "github.com/memodb-io/memobase/src/client/memobase-go/blob"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Flush buffer
err = user.Flush(blob.ChatType)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["DELETE /users/profile/{user_id}/{profile_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

memobase = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

memobase.delete_profile('user_id', 'profile_id')
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);

await client.deleteProfile('user_id', 'profile_id');
""",
            "label": "JavaScript",
        },
        {
            "lang": "Go",
            "source": """// To use the Go SDK, install the package:
// go get github.com/memodb-io/memobase/src/client/memobase-go@latest

import (
    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

projectURL := "YOUR_PROJECT_URL"
apiKey := "YOUR_API_KEY"
client, err := core.NewMemoBaseClient(projectURL, apiKey)
if err != nil {
    panic(err)
}

// Get user
user, err := client.GetUser(userID)
if err != nil {
    panic(err)
}

// Delete profile
err = user.DeleteProfile(profileID)
if err != nil {
    panic(err)
}
""",
            "label": "Go",
        },
    ]
}

API_X_CODE_DOCS["GET /users/event/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
u = client.get_user(uid)

events = u.event(topk=10, max_token_size=1000, need_summary=True)
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

const events = await user.event();
""",
            "label": "JavaScript",
        },
    ]
}

API_X_CODE_DOCS["GET /users/context/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

context = u.context()
""",
            "label": "Python",
        },
        {
            "lang": "JavaScript",
            "source": """// To use the JavaScript SDK, install the package:
// npm install @memobase/memobase

import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

const context = await user.context();
""",
            "label": "JavaScript",
        },
    ]
}

API_X_CODE_DOCS["POST /users/profile/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

profile_id = u.add_profile("value", "topic", "sub_topic")
""",
            "label": "Python",
        },
    ]
}


API_X_CODE_DOCS["PUT /users/profile/{user_id}/{profile_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')

profile_id = u.add_profile("value", "topic", "sub_topic")
u.update_profile(profile_id, "value2", "topic2", "sub_topic2")
""",
            "label": "Python",
        },
    ]
}

API_X_CODE_DOCS["PUT /users/event/{user_id}/{event_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)
# ... insert messages to user

events = u.event(topk=5)
eid = events[0].id

u.update_event(eid, {"event_tip": "The event is about..."})
print(u.event(topk=1))
""",
            "label": "Python",
        },
    ]
}

API_X_CODE_DOCS["DELETE /users/event/{user_id}/{event_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)
# ... insert messages to user

events = u.event(topk=1)
print(events)

eid = events[0].id
u.delete_event(eid)

print(u.event(topk=1))
""",
            "label": "Python",
        },
    ]
}

API_X_CODE_DOCS["GET /users/event/search/{user_id}"] = {
    "x-code-samples": [
        {
            "lang": "Python",
            "source": """# To use the Python SDK, install the package:
# pip install memobase

from memobase import Memobase

client = Memobase(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)

b = ChatBlob(messages=[
    {
        "role": "user",
        "content": "Hi, I'm here again"
    },
    {
        "role": "assistant",
        "content": "Hi, Gus! How can I help you?"
    }
])
u.insert(b)
u.flush()

events = u.search_event('query')
print(events)
""",
            "label": "Python",
        },
    ]
}
