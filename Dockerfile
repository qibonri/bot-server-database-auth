FROM python:3.7

WORKDIR ./home

RUN mkdir -p ./home/db

ENV BOT_API_TOKEN='7049229917:AAHQDyXrPT1NO6QGA0gn3hjxcFA0AkABNa8'

ENV TZ=Europe/Moscow

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
COPY db/createdb.sql ./

CMD ["python", "server.py"]
