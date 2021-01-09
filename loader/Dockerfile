FROM python:3.9-buster

RUN python -m pip install pika --upgrade

COPY ./src/main.py /app/main.py

ENTRYPOINT python /app/main.py