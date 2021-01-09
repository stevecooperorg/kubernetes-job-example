import os
import pika

# https://www.rabbitmq.com/tutorials/tutorial-one-python.html

print("connecting to work queue")
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters('work-queue', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
print("connected to work queue")
channel = connection.channel()
channel.queue_declare(queue='ids')

for x in range(100):
    print("loading data:", str(x))
    channel.basic_publish(exchange='',routing_key='ids',body=str(x))

connection.close()
print("loaded data")
