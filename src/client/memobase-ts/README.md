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
    console.log(ping)

    const config = await client.getConfig()
    console.log(config)

    const updateConfig = await client.updateConfig('a: 1')
    console.log(updateConfig)

    let userId = await client.addUser()
    console.log(userId)

    userId = await client.updateUser(userId, { name: 'John Doe' })
    console.log('Updated user id: ', userId)

    let user = await client.getUser(userId)
    console.log(user)

    const blobId = await user.insert(Blob.parse({
        type: BlobType.Enum.chat,
        messages: [{
            role: 'user',
            content: 'Hello, how are you? my name is John Doe'
        }]
    }))
    console.log(blobId)

    const blob = await user.get(blobId)
    console.log(blob)

    const flushSuc = await user.flush(BlobType.Enum.chat)
    console.log('Flush success: ', flushSuc)
    
    const blobs = await user.getAll(BlobType.Enum.chat)
    console.log(blobs)

    user = await client.getOrCreateUser(userId)
    console.log(user)

    const profiles = await user.profile()
    console.log(profiles)

    const event = await user.event(10, 1000)
    console.log(event)

    const context = await user.context(2000, 1000)
    console.log(context)

    profiles.map((profile) => {
        user.deleteProfile(profile.id).then((isDel) => {
            console.log('Delete profile success: ', isDel)
        })
    })

    const isDel = await client.deleteUser(userId)
    console.log(isDel)
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