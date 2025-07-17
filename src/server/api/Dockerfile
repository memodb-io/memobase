FROM python:3.11-slim-buster AS build


WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN python3.11 -m pip install -r requirements.txt --no-cache-dir

COPY ./memobase_server /app/memobase_server
COPY ./api.py /app


CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]