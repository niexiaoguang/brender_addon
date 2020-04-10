import bpy
from .mylib import mypika
from .mylib import myutils

class Brender_OT_Operator(bpy.types.Operator):
    bl_idname = "brender.ot_operator"
    bl_label = "Brender"

    def execute(self, context):
        print('op')
        return {'FINISHED'}


class Brender_OT_Operator_Test(bpy.types.Operator):
    bl_idname = "brender.test_ot"
    bl_label = "Brender pike test"

    def execute(self, context):
        # mypika.test_pika()
        myutils.test_hash()

        return {'FINISHED'}


