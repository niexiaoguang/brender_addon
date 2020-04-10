import requests
import json
from hashlib import md5
import os
from pathlib import Path
from pathlib import PurePath
import gzip
import time

import binascii
from hashids import Hashids

# =======================  path related ===================
# for root, dirs, files in os.walk("./data"):

#     for p in exceptDirs:
#         if Path(p) not in Path(root).parents and p != root:
#             # print(root)
#             # print(dirs)
#             for filename in files:
#                 ext = Path(filename).suffix
#                 if ext not in exceptExts:

#                     print(filename)

#  except dirs should has full path from target root dir
# return path in string --------- TODO
def get_files_list_with_except(targetdir,exceptdirs=[],exceptexts=[]):

    # much cleaner version
    # targetDir = './data'
    # exceptDirs = ['f1/f2'] # sub dictory under targetDir 
    # exceptExts = ['.jpg','.txt']

    res = []
    p = Path(targetdir)
    for i in p.glob('**/*'):
        for folder in exceptdirs:
            if p.joinpath(folder) not in i.parents and i.is_file() and i.suffix not in exceptexts:
                # print(i)
                res.append(str(i))
    return res





def download_steam(url,savepath,chunk=4096):
    if not isinstance(savepath, PurePath):
        savepath = Path(savepath)
    
    p = savepath.parent
    fn = savepath.name
    p.mkdir(parents=True, exist_ok=True) 
    filepath = p / fn

    r = requests.get(url, stream=True)
    with filepath.open("wb") as f:
        for chunk in r.iter_content(chunk_size=chunk):
            if chunk:
                f.write(chunk)
                # time.sleep(0.1) # speed limit TODO
    
 


def compress(filepath):
    p = Path(filepath)
    if not p.is_file():
        return

    # f_in = open(filepath, 'rb')
    # f_out = gzip.open(filepath + '.gz', 'wb')
    # f_out.writelines(f_in)
    # f_out.close()
    # f_in.close()
    input = open(p, 'rb')
    s = input.read()
    input.close()
    
    outputPath = Path(str(p) + '.gz')
    output = gzip.GzipFile(outputPath, 'wb')
    output.write(s)
    output.close()
    return str(outputPath)


def decompress(filepath,dest_folder,overwrite=True):
    p = Path(filepath)
    if not p.is_file() or p.suffix != '.gz':
        return

    input = gzip.GzipFile(p, 'rb')
    s = input.read()
    input.close()

    outputPath = Path(str(p)[:-3])
    if overwrite and outputPath.is_file():
        os.remove(outputPath)
    else:
        print('not overwrite')
        outputPath = Path(dest_folder).joinpath(Path(outputPath.stem + '.' + str(time.time()) + outputPath.suffix))
        print(outputPath)
    output = open(outputPath, 'wb')
    output.write(s)
    output.close()

    return str(outputPath)

PartSize = 4096 * 1024 # 4MB parts file

def split(source, dest_folder, write_size=PartSize):
    # Make a destination folder if it doesn't exist yet
    # make sure source exist
    if not Path(source).is_file():
        return

    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
    else:
        # Otherwise clean out all files in the destination folder
        for file in os.listdir(dest_folder):
            os.remove(os.path.join(dest_folder, file))
 
    partnum = 0
    source = Path(source)
    # Open the source file in binary mode
    input_file = open(source, 'rb')
 

    while True:
        # Read a portion of the input file
        chunk = input_file.read(write_size)
 
        # End the loop if we have hit EOF
        if not chunk:
            break
 
        # Increment partnum
        partnum += 1
 
        # Create a new file name
        filename = os.path.join(dest_folder, source.name + str(partnum).zfill(3))
 
        # Create a destination file
        dest_file = open(filename, 'wb')
 
        # Write to this portion of the destination file
        dest_file.write(chunk)
 
        # Explicitly close 
        dest_file.close()
     
    # Explicitly close
    input_file.close()
     
    # Return the number of files created by the split
    return partnum
 
 
def join(source_dir, dest_file, read_size=PartSize):
    # Create a new destination file
    dest_file = Path(dest_file)
    output_file = open(dest_file, 'wb')
     
    # Get a list of the file parts
    parts = os.listdir(source_dir)
     
    # Sort them by name (remember that the order num is part of the file name)
    parts.sort()
 
    # Go through each portion one by one
    for file in parts:
         
        # Assemble the full path to the file
        path = os.path.join(source_dir, file)
         
        # Open the part
        input_file = open(path, 'rb')
         
        while True:
            # Read all bytes of the part
            bytes = input_file.read(read_size)
             
            # Break out of loop if we are at end of file
            if not bytes:
                break
                 
            # Write the bytes to the output file
            output_file.write(bytes)
             
        # Close the input file
        input_file.close()
         
    # Close the output file
    output_file.close()
    return str(dest_file)



def computeMD5hash(raw):
    m = md5()
    m.update(raw.encode('utf-8'))
    return m.hexdigest()[8:-8]


def http_req_post_json(url,data):
    headers = {
        'Connection': 'close'
    }
    try:    
        response = requests.post(url,headers=headers,data=data)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            #TODO
            return None

    # better handle exception TODO
    except Exception as e:
        return e



def http_req_get_json(url):
    # add auth later TODO
    headers = {
        # 'Connection': 'close'
    }
    try:    
        response = requests.get(url,headers=headers)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            #TODO
            return None

    # better handle exception TODO
    except Exception as e:
        return e


def http_req_get_plain(url):
    try:    
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            #TODO
            return None
    # better handle exception TODO
    except Exception as e:
        return e


def hash1encode(raw):

    salt = '2aiA3B8ge9ypyuXh'
    hashids = Hashids(salt)

    hex1 = binascii.hexlify(raw.encode())
    encoded = hashids.encode_hex(hex1.decode())

    return encoded


def hash1decode(raw):
    salt = '2aiA3B8ge9ypyuXh'
    hashids = Hashids(salt)

    hex2 = hashids.decode_hex(raw)
    decoded = binascii.unhexlify(hex2)
    decoded = decoded.decode()

    return decoded