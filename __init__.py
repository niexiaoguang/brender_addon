import os
import pathlib
import sys
import time
from . import auto_load

brender_addon_path = pathlib.Path(__file__).parent.absolute()
sep = os.path.sep
lib_path = str(brender_addon_path) + sep + 'pika-1.1.0'
print(lib_path)
sys.path.append(lib_path)
lib_path = str(brender_addon_path) + sep + 'avro-python3-1.9.2'
sys.path.append(lib_path)

lib_path = str(brender_addon_path) + sep + 'qiniu-python-sdk-7.2.8'
sys.path.append(lib_path)

lib_path = str(brender_addon_path) + sep + 'hashids-1.2.0'
sys.path.append(lib_path)

import pika
import avro
import ssl
import qiniu
import avro.schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter

bl_info = {
    "name": "brender_test",
    "author": "Pampa Nie",
    "description": "",
    "blender": (2, 82, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}


auto_load.init()

print('hello')

import binascii
from hashids import Hashids
hashids = Hashids()

hex1 = binascii.hexlify('FmER_mJpSutxsBTMnFacisNjy_Ib'.encode())
print(hex1)
hash1 = hashids.encode_hex(hex1.decode())
print(hash1)

hex2 = hashids.decode_hex(hash1)
print(hex2)
s = binascii.unhexlify(hex2)
print(s.decode())



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
        ch = conn.channel()
        ch.queue_declare("foobar")
        ch.basic_publish(
            "", "foobar", "Hello, world! with ssl from blender by pika " + str(time.time()))
        # print(ch.basic_get("foobar"))


test_pika()


def register():
    auto_load.register()



def unregister():
    auto_load.unregister()


