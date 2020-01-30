import bpy
import requests
import time
import shutil
import os
import threading
import subprocess




from . import blender_bg

uploadHttpUrl = 'http://118.24.60.58/api/appupload'




    


def init():
    print('init add on brender')


def stopRender():
    print('sstop render')

def animRender():
    print('anim render')

def frameRender():
    print('frame render')

def debug():
    print('debug')

    bpy.types.Scene.brenderUploadStatus = not bpy.types.Scene.brenderUploadStatus
    bpy.types.Scene.brenderRenderStatus = not bpy.types.Scene.brenderRenderStatus

    redraw_panel()

def bgupload(self,context):
    '''start upload process, by processing data'''
    print('bg upload')

    # disable upload enable stop anyway first 
    bpy.types.Scene.brenderUploadStatus = True
    redraw_panel()

     # check if missing files


    try:
        bpy.ops.file.report_missing_files()
    except RuntimeError as err:
        error_report = "\n".join(err.args)
        print("Caught error:", error_report)

        bpy.types.Scene.brenderUploadStatus = False
        redraw_panel()

        return {'CANCELLED'}


    else:
        bpy.ops.file.pack_all()
        # save current file 
        bpy.ops.wm.save_mainfile()
        # compress
        # bpy.ops.wm.save_as_mainfile(filepath=fpath, compress=True, copy=False)
        # pack all file into one blender file
        

        # save blend local first
        ts = time.time()
        originFileName = bpy.path.basename(bpy.context.blend_data.filepath)
        savedFileName = originFileName.split('.')[0] + '-' + str(ts) + '.blend'
        currentFolder = bpy.path.abspath("//")


        shutil.copyfile(currentFolder + originFileName , currentFolder + savedFileName)
        uploadFilePath = currentFolder + savedFileName
        

        print('prepared to upload : ' + uploadFilePath)

        try:
            # prepare file to upload TODO

            binary_path = bpy.app.binary_path
            script_path = os.path.dirname(os.path.realpath(__file__))

            proc = subprocess.Popen([
                binary_path,
                "--background",
                "-noaudio",
                "--python", os.path.join(script_path, "upload_bg.py"),
                "--","file",uploadFilePath
            ], bufsize=5000, stdout=subprocess.PIPE, stdin=subprocess.PIPE,universal_newlines=True)

            blender_bg.add_bg_process(process_type='UPLOAD', process=proc)

        except Exception as e:
            print(e)

            bpy.types.Scene.brenderUploadStatus = False
            redraw_panel()


            return {'CANCELLED'}


        finally: 
            #no temp file yet
            if bpy.types.Scene.brenderTempFile == '':
                bpy.types.Scene.brenderTempFile = savedFileName
            
            elif bpy.types.Scene.brenderTempFile != savedFileName:
            # remove temp file
                fileToDelete = currentFolder + str(bpy.types.Scene.brenderTempFile)

                if os.path.exists(fileToDelete):
                    os.remove(fileToDelete)
                
            # record new one
            bpy.types.Scene.brenderTempFile = savedFileName

        return {'FINISHED'}

def stopUpload(self,context):

    blender_bg.kill_bg_process()
    
    bpy.types.Scene.brenderUploadStatus = False
    redraw_panel()


    return {'FINISHED'}



class debugOperator(bpy.types.Operator):
    bl_idname = 'object.brender_debug'
    bl_label = 'Debug for Brender'

    def execute(self,context):
        debug()
        return {'FINISHED'}

class BgUploadOperator(bpy.types.Operator):
    bl_idname = 'object.brender_bg_upload'
    bl_label = 'bg upload project file'

    def execute(self,context):
        res = bgupload(self,context)
        return res


class FrameRenderOperator(bpy.types.Operator):
    bl_idname = 'object.brender_frame_render'
    bl_label = 'Render Frame'

    def execute(self,context):
        frameRender()
        return {'FINISHED'}


class AnimRenderOperator(bpy.types.Operator):
    bl_idname = 'object.brender_anim_render'
    bl_label = 'Render Animation'

    def execute(self,context):
        animRender()
        return {'FINISHED'}

class StopRenderOperator(bpy.types.Operator):
    bl_idname = 'object.brender_stop_render'
    bl_label = 'Stop Render'

    def execute(self,context):
        stopRender()
        return {'FINISHED'}

class StopUploadOperator(bpy.types.Operator):
    bl_idname = 'object.brender_stop_upload'
    bl_label = 'Stop upload'

    def execute(self,context):
        res = stopUpload(self,context)
        return res



class OBJECT_PT_Brender_panel(bpy.types.Panel):

    bl_label = 'Brender'
    bl_idname = 'OBJECT_PT_SCENE_BRENDER_layout'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'


    def draw(self,context):
        # buttons 
        layout = self.layout

        rowInfo = layout.column(align=True)
        rowInfo.label(text="INFO : " + str(bpy.types.Scene.brenderInfo), icon='WORLD_DATA')
        # if not bpy.types.Scene.brenderUploadStatus:

        rowUpload = layout.column(align=True)
        rowUpload.operator("object.brender_bg_upload",text="Upload BG",icon="CAMERA_DATA")


        rowStopUpload = layout.column(align=True)
        rowStopUpload.operator("object.brender_stop_upload",text="Stop Upload",icon="MESH_PLANE")


        rowFrameRender = layout.column(align=True)
        rowFrameRender.operator("object.brender_frame_render",text="Render Frame",icon="CAMERA_DATA")


        rowAnimRender = layout.column(align=True)
        rowAnimRender.operator("object.brender_anim_render",text="Render Animation",icon="EMPTY_DATA")


        rowStopRender = layout.column(align=True)
        rowStopRender.operator("object.brender_stop_render",text="Stop Render",icon="MESH_PLANE")


        rowDebug = layout.column(align=True)
        rowDebug.operator("object.brender_debug",text="Debug",icon="MESH_PLANE")

        if bpy.types.Scene.brenderUploadStatus:
            rowUpload.enabled = False
            rowStopUpload.enabled = True
        else:
            rowUpload.enabled = True
            rowStopUpload.enabled = False           

        if bpy.types.Scene.brenderRenderStatus:
            rowAnimRender.enabled = False
            rowFrameRender.enabled = False
            rowStopRender.enabled = True
        else:
            rowAnimRender.enabled = True
            rowFrameRender.enabled = True
            rowStopRender.enabled = False           




# hack to update panel in a dirty way =+++----------------  FIXME inn future 
def redraw_panel():
	try:
		bpy.utils.unregister_class(OBJECT_PT_Brender_panel)
	except:
		pass
	bpy.utils.register_class(OBJECT_PT_Brender_panel)



def register_panel():

    bpy.types.Scene.brenderInfo = bpy.props.StringProperty(name='brender info',default='')
    bpy.types.Scene.brenderUploadStatus = bpy.props.BoolProperty(name='if uploading',default=False)
    bpy.types.Scene.brenderRenderStatus = bpy.props.BoolProperty(name='if rendering remote',default=False)

    bpy.types.Scene.brenderTempFile = bpy.props.StringProperty(name='temp file for uploading',default='')

    bpy.utils.register_class(BgUploadOperator)
    bpy.utils.register_class(FrameRenderOperator)
    bpy.utils.register_class(AnimRenderOperator)
    bpy.utils.register_class(StopRenderOperator)
    bpy.utils.register_class(StopUploadOperator)
    bpy.utils.register_class(debugOperator)
    bpy.utils.register_class(OBJECT_PT_Brender_panel)


def unregister_panel():
    bpy.utils.unregister_class(BgUploadOperator)
    bpy.utils.unregister_class(FrameRenderOperator)
    bpy.utils.unregister_class(AnimRenderOperator)
    bpy.utils.unregister_class(StopRenderOperator)
    bpy.utils.unregister_class(StopUploadOperator)
    bpy.utils.unregister_class(debugOperator)
    
    bpy.utils.unregister_class(OBJECT_PT_Brender_panel)

    if bpy.types.Scene.brenderInfo:
        del bpy.types.Scene.brenderInfo

    if bpy.types.Scene.brenderUploadStatus:
        del bpy.types.Scene.brenderUploadStatus

    if bpy.types.Scene.brenderRenderStatus:
        del bpy.types.Scene.brenderRenderStatus


if __name__ == "__main__":
    init()
