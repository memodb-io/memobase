FROM python:3.11.10


WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN python3.11 -m pip install -r requirements.txt --no-cache-dir

COPY ./memobase_server /app/memobase_server
COPY ./api.py /app


CMD ["python3.11", "-m", "fastapi", "run", "api.py"]