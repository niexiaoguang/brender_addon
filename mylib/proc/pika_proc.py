import sys
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


# not perfect import solution
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))

# import myqiniu
import myutils
import mypika
import myavro
import config

# def test_send(item):
#     recvQueueName = 'sender'
#     msg = {
#             myavro.SchemaNameConst.Code:myavro.Code.FileHash,
#             myavro.SchemaNameConst.Data:str(item),
#             myavro.SchemaNameConst.Sender:recvQueueName,
#             myavro.SchemaNameConst.Status:0}


#     byte_msg = myavro.encode_byte_body(msg)

#     mypika.publish_msg(_fileHandlerQueueName,byte_msg,_user,_passwd,_host,_port)

# declare a excluse auto-delete queue for recv feedback from file handler

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    ch.basic_ack(delivery_tag=method.delivery_tag)





def declare_queue(queue,callback):
    print('consumer got queue name is ' + queue)

    channel = mypika.create_channel(config.user,config.passwd,config.host,config.port)
    channel.queue_declare(queue=queue, durable=False,exclusive=True, auto_delete=True)
    # print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    channel.start_consuming()




def run():
    queue = 'uuid'
    # for item in range(5):
    #     test_send(queue,item)
        
    declare_queue(queue,callback)



if __name__ == "__main__":
    pass