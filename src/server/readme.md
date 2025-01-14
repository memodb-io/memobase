<div align="center">
    <a href="https://memobase.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://assets.memodb.io/memobase-dark.svg">
      <img alt="Shows the Memobase logo" src="https://assets.memodb.io/memobase-light.svg" width="424">
    </picture>
  </a>
  <p><strong>The server-side of Memobase</strong></p>
  <p>
    <img src="https://img.shields.io/badge/docker-blue">
    <img src="https://img.shields.io/badge/version-0.0.1.dev-green">
  </p>
</div>




## Get started
1. Make sure you have [docker-compose](https://docs.docker.com/compose/install/) installed.
2. Copy the `.env.example` file to `.env` and set the environment variables.
3. Copy the `./api/config.yaml.example` file to `./api/config.yaml` and set the configuration.
   1. You must fill the OpenAI API Key in `llm_api_key`  in `config.yaml`
   2. Or you can change `llm_base_url` to any OpenAI-SDK-Compatible service(via [vllm](https://github.com/vllm-project/vllm), [Ollama](https://github.com/ollama/ollama?tab=readme-ov-file),...)

4. Run `docker-compose build && docker-compose up` to start the services.

Check out the [docs](https://docs.memobase.io/quickstart) of how to use Memobase client or APIs.



## Use Memobase core sololy

1. If you have existing postgres and reids, you can only launch the Memobase core

2. Find and download the docker image of Memobase:

   ```bash
   docker pull ghcr.io/memodb-io/memobase:main
   ```

3. Setup your `config.yaml` and an `env.list` file, the `env.list` should look like [this](./api/.env.example):

4. Run the service:
   ```bash
   docker run --env-file env.list ./api/config.yaml:/app/config.yaml -p 8019:8000 ghcr.io/memodb-io/memobase:main
   ```

   

## SDKs

- **Python**: `pip install memobase`
- **Typescript**: coming soon

