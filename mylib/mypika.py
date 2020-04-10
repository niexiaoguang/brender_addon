import pathlib
import os
import time
import pika
import ssl
from pika.credentials import ExternalCredentials



def make_conn_params(user,passwd,host,port):

    context = ssl.create_default_context(cafile="./ssl/cacert.pem")
    context.set_ciphers('ALL:@SECLEVEL=0') # 

    context.load_cert_chain(certfile="./ssl/brender-client.cert.pem",
                            keyfile="./ssl/brender-client.key.pem",
                            password="dMokP0brnSeGsphGCfsH41Yr2cwDLauB")


    credentials = pika.PlainCredentials(user, passwd)
    ssl_options = pika.SSLOptions(context, host)
    conn_params = pika.ConnectionParameters(
                                            host=host,
                                            port=port,
                                            ssl_options=ssl_options,
                                            credentials=credentials,
                                            heartbeat=30)
    return conn_params



#same user pass for test dev only TODO 
def publish_msg(queue,msg,user,passwd,host,port):
    conn_params = make_conn_params(user,passwd,host,port)
    with pika.BlockingConnection(conn_params) as conn:
        ch = conn.channel()
        # ch.queue_declare("task_queue")
        ch.queue_declare(queue=queue, durable=True)

        ch.basic_publish("", queue,msg)
        conn.close()

def publish_msg_no_care(queue,msg,user,passwd,host,port):
    conn_params = make_conn_params(user,passwd,host,port)
    with pika.BlockingConnection(conn_params) as conn:
        ch = conn.channel()
        # ch.queue_declare("task_queue")
        ch.basic_publish("", queue,msg)
        conn.close()


def init():
    pass

def create_channel(user,passwd,host,port):
    conn_params = make_conn_params(user,passwd,host,port)
    # add try except TODO
    connection = pika.BlockingConnection(conn_params)
    channel = connection.channel()
    return channel


def test_pika():
    print('test pika ssl')

    # connection = pika.BlockingConnection(
    #     pika.ConnectionParameters(host='amqp.brender.cn'))
    # channel = connection.channel()

    # channel.queue_declare(queue='hello')

    # channel.basic_publish(exchange='', routing_key='hello', body='Hello World from python!')
    # print(" [x] Sent 'Hello World!' from py")
    # connection.close()

    brender_addon_path = pathlib.Path(__file__).parent.absolute()
    sep = os.path.sep
    sslPath = str(brender_addon_path) + sep + 'ssl' + sep
    context = ssl.create_default_context(cafile= sslPath + "cacert.pem")
    context.set_ciphers('ALL:@SECLEVEL=0')

    context.load_cert_chain(certfile=sslPath + "brender-client.cert.pem",
                            keyfile=sslPath + "brender-client.key.pem",
                            password="dMokP0brnSeGsphGCfsH41Yr2cwDLauB")

    credentials = pika.PlainCredentials('guest', 'guest')
    ssl_options = pika.SSLOptions(context, 'amqps.brender.cn')
    conn_params = pika.ConnectionParameters(
        host='amqps.brender.cn',
        port=5671,
        ssl_options=ssl_options,
        credentials=credentials,
        heartbeat=30)

    with pika.BlockingConnection(conn_params) as conn:
        ts = time.time()
        ch = conn.channel()
        ch.queue_declare("foobar")
        ch.basic_publish(
            "", "foobar", "Hello, world! with ssl from blender by pika " + str(ts))
        print('test pika with ts ' + str(ts))
        # print(ch.basic_get("foobar"))
