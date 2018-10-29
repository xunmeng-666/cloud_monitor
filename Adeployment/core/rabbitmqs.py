# -*- coding:utf-8-*-

import time
import pika
from Adeployment.core.model_func import get_db
from Adeployment.core.environments import get_rabbitmq


_rabbit = get_rabbitmq()
host = _rabbit['host']
port = _rabbit['port']
username = None
password = None

def rabbit_producer(info):
    '''RabbitMQ生产者'''
    if _rabbit['username'] and _rabbit['password']:
        username = _rabbit['username']
        password = _rabbit['password']
    auth = pika.PlainCredentials(username=username,password=password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port,credentials=auth))
    channel = connection.channel()
    channel.queue_declare(queue='adadmin')
    channel.basic_publish(exchange='',routing_key='adadmin',body=info,
                          )

class Rabbit_Consumer(object):
    ''' RabbitMQ消费者 '''
    def __init__(self):
        if _rabbit['username'] and _rabbit['password']:
            username = _rabbit['username']
            password = _rabbit['password']
        auth = pika.PlainCredentials(username=username, password=password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,port=self.port,credentials=auth,
                                                                       socket_timeout=10,blocked_connection_timeout=1000))
        self.channel = connection.channel()
    def rabbit_consumer(self,request):

        self.request = request
        self.channel.queue_declare(queue='adadmin')
        self.channel.basic_consume(self.callback, queue='adadmin',no_ack=False)

        self.channel.start_consuming()
    def callback(self,ch, method, properties, body):
        if body == 'quit':
            self.request.websocket.send(body)
            time.sleep(5)
            self.request.websocket.close()
            self.rabbit_close()
        else:
            self.request.websocket.send(body)
    def rabbit_close(self):
        self.channel.queue_delete(queue='adadmin')
        self.channel.close()

