<div align="center">
    <a href="https://memobase.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://assets.memodb.io/memobase-dark.svg">
      <img alt="Shows the Memobase logo" src="https://assets.memodb.io/memobase-light.svg" width="424">
    </picture>
  </a>
  <p><strong>The server-side of Memobase</strong></p>
  <p>
    <img src="https://img.shields.io/github/v/tag/memodb-io/memobase">
  </p>
</div>




## Get started

### Setup

[**config.yaml**](https://docs.memobase.io/references/full)

Memobase uses a single  `config.yaml` to initialize the server. It contains the configs of:

- LLM: `llm_base_url`, `llm_api_key`, `best_llm_model`,...
- Embedding: `enable_event_embedding`, `embedding_api_key`...
- Memory: `max_pre_profile_token_size`, `max_profile_subtopics`, `additional_user_profiles`...

By default, Memobase enables user profile and event memory with filter ability. That means running a Memobase server requires you to have below things:

- **LLM API**: You must fill the OpenAI API Key in `llm_api_key` of `config.yaml`.Or you can change `llm_base_url` to any OpenAI-SDK-Compatible service(via [vllm](https://github.com/vllm-project/vllm), [Ollama](../../assets/tutorials/ollama+memobase/readme.md),...). Alternatively, you can set `llm_api_key` and `llm_base_url` using environment variables `MEMOBASE_LLM_API_KEY` and `MEMOBASE_LLM_BASE_URL`
- **Embedding API**: Memobase supports OpenAI-Compatible SDK, [Jina Embedding](https://jina.ai/models/jina-embeddings-v3/) and [Ollama Embedding](https://docs.ollama.com/api#generate-embeddings). Memobase uses embedding API to retrieve related user events. If you don't have a embedding API, you can set `enable_event_embedding: false` in `config.yaml`

We have some example `config.yaml` in `examplel_config`:

- [`profile_for_assistant`](./api/example_config/profile_for_education),  [`profile_for_education`](./api/example_config/profile_for_education),  [`profile_for_companion`](./api/example_config/profile_for_companion)  are three similar configs in term of structure, but for different user cases.
- [`event_tag`](./api/example_config/event_tag) is a feature to tracking temporal attributes of users. [doc](https://docs.memobase.io/features/event/event_tag)
- [`only_strict_profile`](./api/example_config/only_strict_profile): disable all other features, only collect the profiles you design.
- [`jina_embedding`](./api/example_config/jina_embedding) uses Jina exmbedding for event search.
- [`ollama_embedding`](./api/example_config/ollama_embedding) uses Ollama exmbedding for event search.



**environment variables**

Check `./.env.example` for necessary vars. You can configure the running port and access token in here.  Also, anything in `config.yaml` can be override in env([doc](https://docs.memobase.io/references/full#environment-variable-overrides)), just starts with `MEMOBASE_`

### Launch

1. Make sure you have [docker-compose](https://docs.docker.com/compose/install/) installed.

2. Prepare the configs:

   ```bash
   cd src/server
   cp .env.example .env
   cp ./api/config.yaml.example ./api/config.yaml
   ```

   1. `.env` contains the service configs, like running port, secret token...
   2. `config.yaml` contains the Memobase configs, like LLM model, profile slots. [docs](https://docs.memobase.io/references/full)

3. Run `docker-compose build && docker-compose up` to start the services.

Check out the [docs](https://docs.memobase.io/quickstart) of how to use Memobase client or APIs.



## Use Memobase core only

1. If you have existing postgres and reids, you can only launch the Memobase core

2. Find and download the docker image of Memobase:

   ```bash
   docker pull ghcr.io/memodb-io/memobase:latest
   ```

3. Setup your `config.yaml` and an `env.list` file, the `env.list` should look like [this](./api/.env.example):

4. Run the service:
   ```bash
   docker run --env-file env.list -v ./api/config.yaml:/app/config.yaml -p 8019:8000 ghcr.io/memodb-io/memobase:main
   ```



## Development

1. Start a local DB first by `sh script/up-dev.sh`
2. Open a new terminal window and `cd ./api`
3. Install python deps: `uv sync`
4. To test if you got everything right, run `uv run pytest` to see if all the tests are passed.
5. Launch Memobase Server in dev mode: `uv run -m fastapi dev --port 8019`

> `fastapi dev` has hot-reload, so you can just modify the code and test it without relaunch the service.



## Migrations

Memobase may introduce breaking changes in DB schema, here is a guideline of how to migrate your data to latest Memobase:

1. Install `alembic`: `pip install alembic`

2. Modify `./api/alembic.ini`. Find the field called `sqlalchemy.url` in `alembbic.ini`, change it to your Postgres DB of Memobase

3. Run below commands to prepare the migration plan:

   ```bash
   cd api
   mkdir migrations/versions
   alembic upgrade head
   alembic revision --autogenerate -m "memobase changes"
   ```

4. ⚠️ Run the command `alembic upgrade head` again to migrate your current Memobase DB to the latest one.
