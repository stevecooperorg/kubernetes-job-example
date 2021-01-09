import os
import pika

user = os.environ['JOB_USER']
pwd = os.environ['JOB_PASS']

# did the credentials come through?
print("credentials:", user, pwd)

# https://www.rabbitmq.com/tutorials/tutorial-one-python.html

print("connecting to work queue")
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters('work-queue', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
print("connected to work queue")
channel = connection.channel()
channel.queue_declare(queue='ids')
connection.close()
print("connected to work queue")
