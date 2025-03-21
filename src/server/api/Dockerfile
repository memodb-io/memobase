FROM python:3.11-slim-buster AS build

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python3.11 -m pip install --no-cache-dir -r requirements.txt

COPY ./memobase_server /app/memobase_server
COPY ./api.py /app
COPY ./api_docs.py /app

CMD ["python3.11", "-m", "fastapi", "run", "api.py"]