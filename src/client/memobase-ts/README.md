<div align="center">
    <a href="https://memobase.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://assets.memodb.io/memobase-dark.svg">
      <img alt="Shows the Memobase logo" src="https://assets.memodb.io/memobase-light.svg" width="424">
    </picture>
  </a>
  <p><strong>User Profile-Based Memory for GenAI Apps</strong></p>
  <p>
    <a href="https://www.npmjs.com/package/@memobase/memobase">
      <img src="https://img.shields.io/npm/v/@memobase/memobase.svg?logo=npm&&logoColor=fff&style=flat&colorA=2C2C2C&colorB=28CF8D">
    </a>
    <a href="https://jsr.io/@memobase/memobase">
      <img src="https://img.shields.io/jsr/v/@memobase/memobase.svg?logo=jsr&&logoColor=fff&style=flat&colorA=2C2C2C&colorB=28CF8D" />
    </a>
    <a href="https://npmcharts.com/compare/@memobase/memobase?minimal=true">
      <img src="https://img.shields.io/npm/dm/@memobase/memobase.svg?logo=typescript&&logoColor=fff&style=flat&colorA=2C2C2C&colorB=28CF8D" />
    </a>
    <a href="https://github.com/memodb-io/memobase/actions/workflows/publish.yaml">
      <img src="https://github.com/memodb-io/memobase/actions/workflows/publish.yaml/badge.svg">
    </a>
  </p>
</div>

# Memobase TypeScript and JavaScript API Library
This library provides convenient access to the Memobase REST API from TypeScript or JavaScript.


## Installation

```sh
npm install @memobase/memobase
```

### Installation from JSR

```sh
deno add jsr:@memobase/memobase
npx jsr add @memobase/memobase
```


## Usage

The code below shows how to get started using the completions API.

<!-- prettier-ignore -->
```js
import { MemoBaseClient, Blob, BlobType } from '@memobase/memobase';

const client = new MemoBaseClient(process.env['MEMOBASE_PROJECT_URL'], process.env['MEMOBASE_API_KEY'])

const main = async () => {
    const ping = await client.ping()
    console.log('Ping: ', ping)

    const config = await client.getConfig()
    console.log('Config: ', config)

    const updateConfig = await client.updateConfig('a: 1')
    console.log('Update config: ', updateConfig)

    let userId = await client.addUser()
    console.log('Add user: ', userId)

    userId = await client.updateUser(userId, { name: 'John Doe' })
    console.log('Updated user id: ', userId)

    let user = await client.getUser(userId)
    console.log('User: ', user)

    const blobId = await user.insert(Blob.parse({
        type: BlobType.Enum.chat,
        messages: [{
            role: 'user',
            content: 'Hello, how are you? my name is John Doe'
        }]
    }))
    console.log('Insert blob: ', blobId)

    const blob = await user.get(blobId)
    console.log('Blob: ', blob)

    const flushSuc = await user.flush(BlobType.Enum.chat)
    console.log('Flush success: ', flushSuc)

    const blobs = await user.getAll(BlobType.Enum.chat)
    console.log('Blobs: ', blobs)

    user = await client.getOrCreateUser(userId)
    console.log('Get or create user: ', user)

    const addProfileSuc = await user.addProfile("Content", "Topic1", "SubTopic1")
    console.log('Add profile success: ', addProfileSuc)

    const profiles = await user.profile(2000)
    console.log('Profiles: ', profiles)

    const updateProfileSuc = await user.updateProfile(profiles[0].id, "New Content", "New Topic", "New SubTopic")
    console.log('Update profile success: ', updateProfileSuc)

    const deleteProfileSuc = await user.deleteProfile(profiles[0].id)
    console.log('Delete profile success: ', deleteProfileSuc)

    const event = await user.event(10, 1000)
    console.log('Event: ', event)

    const updateEventSuc = await user.updateEvent(event[0].id, {
        "id": event[0].id,
        "event_data": {
            "profile_delta": [
                {
                    "content": "New Event Content",
                    "attributes": {
                        "topic": "interest",
                        "sub_topic": "foods"
                    }
                }
            ]
        },
        created_at: new Date(),
        updated_at: new Date()
    })
    console.log('Update event success: ', updateEventSuc)

    const deleteEventSuc = await user.deleteEvent(event[0].id)
    console.log('Delete event success: ', deleteEventSuc)

    const context = await user.context(2000, 1000)
    console.log('Context: ', context)

    const isDel = await client.deleteUser(userId)
    console.log('Delete user success: ', isDel)
}

main()
```

## Support

Join the community for support and discussions:

-  [Join our Discord](https://discord.gg/YdgwU4d9NB) 👻 

-  [Follow us on Twitter](https://x.com/memobase_io) 𝕏 

Or Just [email us](mailto:contact@memobase.io) ❤️


## Contributors

This project exists thanks to all the people who contribute.

And thank you to all our backers! 🙏

<a href="https://github.com/memodb-io/memobase/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=memodb-io/memobase" />
</a>


## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/memodb-io/memobase/blob/main/LICENSE) file for details.