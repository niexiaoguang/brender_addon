import sys, os, time
import requests
import logging

import bpy
# from . blender_bg import progress

uploadHttpUrl = 'http://118.24.60.58/api/appupload'




def start_logging():
    # logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)
    # requests_log = logging.getLogger("requests.packages.urllib3")
    # requests_log.setLevel(logging.DEBUG)
    # requests_log.propagate = True
    return 'ok'

class upload_in_chunks(object):
    def __init__(self, filename, chunksize=1 << 13, report_name='file'):
        self.filename = filename
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filename)
        self.readsofar = 0
        self.report_name = report_name

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunksize)
                if not data:
                    # sys.stderr.write("\n")
                    sys.stdout.write("brender stdout upload chunk file done\n")
                    break
                self.readsofar += len(data)
                percent = int(self.readsofar * 1e2 / self.totalsize)
                # progress('uploading %s' % self.report_name, percent)
                sys.stdout.write('brender buploading ' +  str(percent) + "%.\n" )
                yield data

    def __len__(self):
        return self.totalsize





def upload_file():

    argv = sys.argv
    argv = argv[argv.index("--") + 1:]  # get all args after "--"

    uploadFile = argv[1]

    uploadFileName = str(time.time()) + ".blend"# need set proper file name by args  TODO
    uploaded = False


    username = 'pata'
    headers = {'filename': uploadFileName,
                'username': username,
                'Content-Type':'multipart/form-data'
                }

    try:    
        upload_response = requests.post(uploadHttpUrl,headers=headers,
                                data=upload_in_chunks(uploadFile,4096),
                                stream=True, verify=False)



        if upload_response.status_code == 200:
            uploaded = True

            sys.stdout.write('brender upload bsuccessed\n') # use successed pass to thread com for finish the subprocess
        else:
            #TODO
            uploaded = False
            sys.stdout.write('brender upload bfailed : ' + str(upload_response) + '\n') # ---------

    except Exception as e:
        # sys.stderr.write('brenderfailed : %s\n',e) #-------------
        sys.stdout.write('brender bfailed : %s\n',e) #------------- 
        time.sleep(1)

    return uploaded


if __name__ == "__main__":
    upload_file()