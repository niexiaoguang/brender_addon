import multiprocessing
# import proc.sync_proc
# import proc.pika_proc
import logging
import time

from pathlib import Path


def wait_sync():
      # googd way to debugging multiprocessing 
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.DEBUG)

    p = multiprocessing.Process(name='pika',target=proc.pika_proc.run,args=())

    p.start()
  

def req_sync():
    # googd way to debugging multiprocessing 
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.DEBUG)

    q_remote_sync_from_qiniu = multiprocessing.Queue()
    q_sync_to_qiniu = multiprocessing.Queue()

    targetDir = './data'
    exceptExts = ['.zip']
    exceptDirs = ['f1']
    FilesToSyncList = myutils.get_files_list_with_except(targetDir,exceptDirs,exceptExts)
    FilesToSyncDict = {}
    for file in FilesToSyncList:
        logging.info(file)
        # fileHash = myqiniu.etag(file)
        q_sync_to_qiniu.put(file)
        FilesToSyncDict[file] = None

    q_remote_sync_from_qiniu.put(FilesToSyncDict)

    p = multiprocessing.Process(name='sync_to_qiniu',target=proc.sync_proc.run,args=(q_sync_to_qiniu,q_remote_sync_from_qiniu,))

    # p2 = multiprocessing.Process(name='mp2',target=mp_worker1.worker,args=(queue2,))
    # p.daemon = True
    p.start()
    # p2.start()
    # p.terminate()
    # use this after terminate is needed TODO
    # p.join()


    # tk = 0
    # while p1.is_alive():
    #     print('p1 running')
    #     time.sleep(1)
    #     tk += 1
    #     if(tk > 5):
    #         p1.terminate()
    #         p2.terminate()
    # print('after kill process')

    # # after processing exited, back queue to main
    # # time.sleep(5)
    # print('main got queue1 size' + str(queue1.qsize()))
    # print('main got queue2 size' + str(queue2.qsize()))
if __name__ == '__main__':
    req_sync()
    wait_sync()