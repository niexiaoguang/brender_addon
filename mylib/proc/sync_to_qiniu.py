import sys
import json
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

def pre_upload(uuid,fuid,abspath,filehash,filekey):
    url = 'https://brender.cn/api/pre_upload?uuid=' + uuid + '&hash=' + filehash
    resp = myutils.http_req_get_json(url)
    respHash = resp[config.httpRespAttrHash]
    if filehash != respHash:
        return None  # TODO
    
    token = resp[config.httpRespAttrToken]

    return token
    

def post_file_metadata(datadict):
    url = 'https://brender.cn/api/file_metadata'
    jsonStr = json.dumps(datadict)
    ret = myutils.http_req_post_json(url,jsonStr)
    return ret


def run(uuid,fuid,abspath,relpath,filehash,filekey):
    # check if file existed on cloud ,if not get upload token 
    token = pre_upload(abspath,filehash,filekey)
    if(!token):
        return config.ErrorCodeHashNotMatch
    
    if(token == config.httpRespOk):
        return token

    # upload to qiniu
    ret,info = myqiniu.upload(filekey,abspath)
    respHash = ret[config.httpRespAttrHash]

    # compare to local double check
    if(filehash != respHash):
        return config.ErrorCodeHashNotMatch
    
    #after success upload post json data about file
    dataDict = {}
    dataDict[config.httpReqAttrHash] = filehash
    dataDict[config.httpReqAttrUuid] = uuid
    dataDict[config.httpReqAttrFuid] = fuid
    dataDict[config.httpReqAttrAbspath] = abspath
    dataDict[config.httpReqAttrFilekey] = filekey
    dataDict[config.httpReqAttrRelpath] = relpath

    resp = post_file_metadata(dataDict)
    respHash = resp[config.httpRespAttrHash]

    if(filehash != respHash):
        return config.ErrorCodeHashNotMatch
    
    return config.httpRespOk

if __name__ == "__main__":
    pass