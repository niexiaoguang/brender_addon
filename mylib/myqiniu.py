import requests

from qiniu import etag
from qiniu import put_file

from pathlib import Path
from pathlib import PurePath
from pathlib import PureWindowsPath
from pathlib import PurePosixPath
from . import myutils


def get_file_hash(filepath):
    if Path(filepath).is_file():
        return etag(filepath)
    else:
        return 'None'


def generate_file_key(uuid,fuid,filepath):
    path = PurePath(filepath)
    if isinstance(path, PureWindowsPath):
        path = path.as_posix()
    key = uuid + '-' + fuid + '-' + myutils.computeMD5hash(str(path))
    return key


KFileHashReqUrlRoot = 'https://brender.cn/api/file_hash?bucket=brender-pub&key='
def get_remote_file_hash(filekey):
    url = KFileHashReqUrlRoot + filekey
    response = myutils.http_req_get_json(url)
    return response

KUploadTokenReqUrl = 'https://www.brender.cn/api/upload_token_pub'
def get_upload_token():
    url = KUploadTokenReqUrl
    response = myutils.http_req_get_plain(url)
    return response

def upload(filekey,filepath):
    token = get_upload_token()
    if not token:
        # logging.error('token req failed : ' + token)
        # return
        # handle error TODO
        pass
    
    ret,info = put_file(token, filekey, filepath)
    return ret,info

KDownloadUrlRoot = 'http://data.brender.cn/'
def download(filekey,filepath):
    url = KDownloadUrlRoot + filekey
    # result handle TODO
    myutils.download_steam(url,filepath)
    filehash = get_file_hash(filepath)
    return {'hash':filehash,'key':filekey,'path':filepath}