import os
import pika

# https://www.rabbitmq.com/tutorials/tutorial-one-python.html

work_queue_host = os.environ['WORK_QUEUE_HOST']
work_queue_port = int(os.environ.get('WORK_QUEUE_PORT', "5672"))
print("connecting to work queue ", work_queue_host, str(work_queue_port))
credentials = pika.PlainCredentials('guest', 'guest')
parameters = pika.ConnectionParameters(work_queue_host, work_queue_port, '/', credentials)
connection = pika.BlockingConnection(parameters)

print("connected to work queue")
channel = connection.channel()
channel.queue_declare(queue='ids')

for x in range(100):
    print("loading data:", str(x))
    channel.basic_publish(exchange='',routing_key='ids',body=str(x))

connection.close()
print("loaded data")
