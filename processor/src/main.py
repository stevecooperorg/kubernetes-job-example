import os
import pika
import time

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    time.sleep(2)

def main():

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

    channel.basic_consume(queue='ids',
                         auto_ack=True,
                         on_message_callback=callback)

    channel.start_consuming()

    connection.close()
    print("processed all work")

main()