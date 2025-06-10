FROM python:3.11-slim-buster AS build


WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN python3.11 -m pip install -r requirements.txt --no-cache-dir

COPY ./memobase_server /app/memobase_server
COPY ./api.py /app
COPY ./api_docs.py /app
COPY ./entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
