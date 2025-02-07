<div align="center">
    <a href="https://memobase.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://assets.memodb.io/memobase-dark.svg">
      <img alt="Shows the Memobase logo" src="https://assets.memodb.io/memobase-light.svg" width="424">
    </picture>
  </a>
  <p><strong>The server-side of Memobase</strong></p>
  <p>
    <img src="https://img.shields.io/badge/docker-0.0.5-blue">
  </p>
</div>




## Get started

> [!NOTE]
>
> You must fill the OpenAI API Key in `llm_api_key` of `config.yaml`
>
> Or you can change `llm_base_url` to any OpenAI-SDK-Compatible service(via [vllm](https://github.com/vllm-project/vllm), [Ollama](https://github.com/ollama/ollama?tab=readme-ov-file),...)



1. Make sure you have [docker-compose](https://docs.docker.com/compose/install/) installed.

2. Prepare the configs:

   ```bash
   cd src/server
   cp .env.example .env
   cp ./api/config.yaml.example ./api/config.yaml
   ```

   1. `.env` contains the service configs, like running port, secret token...
   2. `config.yaml` contains the Memobase configs, like LLM model, profile slots. [docs](https://docs.memobase.io/features/customization/full)

3. Run `docker-compose build && docker-compose up` to start the services.

Check out the [docs](https://docs.memobase.io/quickstart) of how to use Memobase client or APIs.



## Use Memobase core sololy

1. If you have existing postgres and reids, you can only launch the Memobase core

2. Find and download the docker image of Memobase:

   ```bash
   docker pull ghcr.io/memodb-io/memobase:latest
   ```

3. Setup your `config.yaml` and an `env.list` file, the `env.list` should look like [this](./api/.env.example):

4. Run the service:
   ```bash
   docker run --env-file env.list ./api/config.yaml:/app/config.yaml -p 8019:8000 ghcr.io/memodb-io/memobase:main
   ```


## SDKs

- **Python**: `pip install memobase`. 
- **Typescript**: `npm install @memobase/memobase`. More installations on [here](../client/memobase-ts/readme.md)



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
