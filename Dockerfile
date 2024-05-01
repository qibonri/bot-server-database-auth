FROM python:3.7

WORKDIR ./home

RUN mkdir -p ./home/db

ENV BOT_API_TOKEN=""
ENV MY_TELEGRAM_ID=""

ENV TZ=Europe/Moscow

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY createdb.sql ./

CMD ["python", "server.py"]