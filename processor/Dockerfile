FROM python:3.9-buster

RUN python -m pip install pika --upgrade

ENV WORK_QUEUE_HOST=work-queue
ENV WORK_QUEUE_PORT=5672

COPY ./src/main.py /app/main.py

ENTRYPOINT python /app/main.py