
import bpy
import sys, threading, os
import re
import time

bg_processes = []

from . import brender_panel

class threadCom:  # object passed to threads to read background process stdout info
    ''' Object to pass data between thread and '''

    def __init__(self, process_type, proc, location=None, name=''):
        # self.obname=ob.name
        self.name = name
        self.process_type = process_type
        self.outtext = ''
        self.proc = proc
        self.lasttext = ''
        self.message = ''  # the message to be sent.
        self.progress = 0.0
        self.location = location
        self.error = False
        self.log = ''


def threadread(tcom):
    '''reads stdout of background process, done this way to have it non-blocking. this threads basically waits for a stdout line to come in, fills the data, dies.'''
    found = False
    while not found:
        inline = tcom.proc.stdout.readline()
        # print('readthread', time.time())
        inline = str(inline)
        tcom.outtext = inline
        if 'buploading' in tcom.outtext:
            tcom.progress = inline

        if 'bsuccessed' in tcom.outtext or 'bfailed' in tcom.outtext:
            tcom.lasttext = tcom.outtext
            found = True




def updateInfo(info):
    # try to update ts in panel



    bpy.types.Scene.brenderInfo = info
    brender_panel.redraw_panel()


@bpy.app.handlers.persistent
def bg_update():
    '''monitoring of background process'''
    # print('bg_updating ' + str(time.time()))

    global bg_processes
    if len(bg_processes) == 0:
        return 2 # timer interval to blender api

    for p in bg_processes:
        # proc=p[1].proc
        readthread = p[0]
        tcom = p[1]

        updateInfo(tcom.progress)
        
        if not readthread.is_alive():
            readthread.join() # finish a thread ??? TODO
            # stop a subprocess anyway?  TODO
            if 'bsuccessed' in tcom.lasttext or 'bfailed' in tcom.lasttext: 
                print('remove a process')

                bg_processes.remove(p)

                bpy.types.Scene.brenderUploadStatus = False
                brender_panel.redraw_panel()

        else:
            if 'brender' in tcom.outtext:# set a string as filter
                print('thread info outtext: ' + tcom.outtext)
                print('thread info lasttext: ' + tcom.lasttext)

            bpy.types.Scene.brenderUploadStatus = True
            brender_panel.redraw_panel()

        
        updateInfo(tcom.lasttext)

    
    # if len(bg_processes) == 0:
    #     bpy.app.timers.unregister(bg_update)
    if len(bg_processes) > 0:
        return .3
    return 1.


process_types = (
    ('UPLOAD', 'Upload', ''),
    ('DOWNLOAD', 'Download', ''),
)

def kill_bg_process():
    # handle excpetion TODO
    global bg_processes

    print('before kill procs number : ' + str(len(bg_processes)))
    if len(bg_processes) > 0:
        for p in bg_processes:
            print('remove p : ' + str(p))
            readthread = p[0]
            readthread.join()
            tcom = p[1]
            tcom.proc.kill()
            bg_processes.remove(p)

    
    print('after kill procs number : ' + str(len(bg_processes)))



def add_bg_process(location=None, name=None, process_type='',
                   process=None):
    '''adds process for monitoring'''
    global bg_processes
    tcom = threadCom(process_type, process, location, name)
    readthread = threading.Thread(target=threadread, args=([tcom]), daemon=True)
    readthread.start()

    bg_processes.append([readthread, tcom])
    # if not bpy.app.timers.is_registered(bg_update):
    #     bpy.app.timers.register(bg_update, persistent=True)


def register():

    bpy.app.timers.register(bg_update, persistent=True)


def unregister():

    if bpy.app.timers.is_registered(bg_update):
        bpy.app.timers.unregister(bg_update)

