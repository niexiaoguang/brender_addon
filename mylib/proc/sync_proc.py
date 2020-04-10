import sys
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


# not perfect import solution
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent))

import myqiniu
import myutils
import mypika
import myavro
import config

# for test dev only TODO
uuid = 'uuid'
fuid = 'fuid'

# update for new TODO
def sync_to_qiniu(filepath):
    p = Path(filepath)
    if not p.is_file():
        logging.info('error not a file : ' + filepath)
        return filepath,'error'

    logging.info('sync file : ' + str(filepath))
    localHash = myqiniu.get_file_hash(filepath)
    logging.info('local hash : ' + localHash)
    fileKey = myqiniu.generate_file_key(uuid,fuid,filepath)
    logging.info('file key : ' + fileKey)

    response = myqiniu.get_remote_file_hash(fileKey)
    if not response:
        printr('error : cant get remote file hash : ' + response)
        return filepath,'error'
    
    logging.info('get response ' + str(response))

    if localHash == response['hash']:
        logging.info('finished : file already sync')
        return filepath,{'hash':localHash} # according to qiniu return format TODO
    
    # upload file to qiniu

    # test dev only TODO

    ret,info = myqiniu.upload(fileKey,filepath)

    logging.info('upload file to qiniu info : ' + str(info))
    logging.info('upload file to qiniu return : ' + str(ret))
    
    return filepath,ret

def run(q_sync_to_qiniu,q_remote_sync_from_qiniu):
    while q_sync_to_qiniu.qsize() > 0:

        filePath = q_sync_to_qiniu.get()
        retFilePath,ret = sync_to_qiniu(filePath)

        if(ret != 'error'):
            fileHash = ret['hash']
            #get and read dict from queue
            record = q_remote_sync_from_qiniu.get()
            record[filePath] = fileHash
            q_remote_sync_from_qiniu.put(record)
            msg = filePath

            msg = {
                myavro.SchemaNameConst.Code:myavro.Code.FileSync,
                myavro.SchemaNameConst.Uuid:uuid,
                myavro.SchemaNameConst.Fuid:fuid,
                myavro.SchemaNameConst.FilePath:filePath,
                myavro.SchemaNameConst.FileHash:fileHash,
                # use uuid for sender dev only TODO
                myavro.SchemaNameConst.Sender:uuid,
                myavro.SchemaNameConst.Status:0}


            byte_msg = myavro.encode_byte_body(msg)

            mypika.publish_msg(config.FilesHandleQueue,byte_msg,config.user,config.passwd,config.host,config.port)

    logging.info('after sync q size ' + str(q_sync_to_qiniu.qsize()))
    logging.info('sync dict ' + str(q_remote_sync_from_qiniu.get()))


if __name__ == "__main__":
    pass