import sys
import os
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')



from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))

# import myqiniu
import myutils
import mypika
import myavro
import config
import myqiniu

def sync_file_from_qiniu(uuid,fuid,filepath,filehash):

        datarootpath = Path(config.ServerDataRootPath)
        mayLocalFilePath = datarootpath.joinpath(uuid,fuid,filepath)

        if(mayLocalFilePath.is_file()):
            mayLocalHash = myqiniu.get_file_hash(mayLocalFilePath)

            if(mayLocalHash == filehash):
                logging.info('local file synced , done')
                return  {'hash':filehash,'key':None,'path':filepath}
            else:
                # has local file but out dated
                logging.info('local file outdated ,remvoe')
                os.remove(mayLocalFilePath)
                return {'hash':filehash,'key':None,'path':filepath}
        else:
            # download from qiniu and save
            logging.info('no local file ,download from qiniu')
            fileKey = myqiniu.generate_file_key(uuid,fuid,filepath)
            raw_ret = myqiniu.download(fileKey,mayLocalFilePath)
            return raw_ret


def callback(ch, method, properties, body):
    logging.info(" [x] Received byte : %r" % body)
    msg = myavro.decode_byte_body(body)
    logging.info(" [x] Received msg : %r" % msg)

    code = msg[myavro.SchemaNameConst.Code]
    if code == myavro.Code.FileSync:
        uuid = msg[myavro.SchemaNameConst.Uuid]
        fuid = msg[myavro.SchemaNameConst.Fuid]
        filePath = msg[myavro.SchemaNameConst.FilePath]
        fileHash = msg[myavro.SchemaNameConst.FileHash]
        sender = msg[myavro.SchemaNameConst.Sender]
    
        # compare local files hash 
        # return {'hash':filehash,'key':None,'path':filepath}
        ret = sync_file_from_qiniu(uuid,fuid,filePath,fileHash)

        resp_msg = msg
        if(fileHash == ret['hash']):
            resp_msg[myavro.SchemaNameConst.Status] = myavro.Status.Success
        else:
            resp_msg[myavro.SchemaNameConst.Status] = myavro.Status.ErrRemoteFileSyncFromQiniuHashNotMatchToOriginal
    # finally after finish all work to ack a msg
    ch.basic_ack(delivery_tag=method.delivery_tag)

    byte_resp_msg = myavro.encode_byte_body(resp_msg)
    mypika.publish_msg_no_care(sender,byte_resp_msg,config.user,config.passwd,config.host,config.port)



def declare_queue(queue,callback):
    print('consumer got queue name is ' + queue)

    channel = mypika.create_channel(config.user,config.passwd,config.host,config.port)
    channel.queue_declare(queue=queue, durable=True)
    # print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    channel.start_consuming()




def run():
    queue = config.FilesHandleQueue
    # for item in range(5):
    #     test_send(queue,item)
        
    declare_queue(queue,callback)

if __name__ == '__main__':
    run()