import os
import pika

# https://www.rabbitmq.com/tutorials/tutorial-one-python.html

def get_work_queue_channel(queue_name):
    work_queue_host = os.environ['WORK_QUEUE_HOST']
    work_queue_port = int(os.environ.get('WORK_QUEUE_PORT', "5672"))
    print("connecting to work queue ", work_queue_host, str(work_queue_port))
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(work_queue_host, work_queue_port, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    print("connected to work queue")
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel


def main():
    channel = get_work_queue_channel("ids")
    for x in range(100):
        print("loading data:", str(x))
        channel.basic_publish(exchange='',routing_key='ids',body=str(x))
    print("loaded data")


main()
