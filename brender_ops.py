import bpy
from .mylib import mypika

class Brender_OT_Operator(bpy.types.Operator):
    bl_idname = "brender.ot_operator"
    bl_label = "Brender"

    def execute(self, context):
        print('op')
        return {'FINISHED'}


class Brender_OT_Operator(bpy.types.Operator):
    bl_idname = "brender.pike_test_ot"
    bl_label = "Brender pike test"

    def execute(self, context):
        mypika.test_pika()
        return {'FINISHED'}


