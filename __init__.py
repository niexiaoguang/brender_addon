bl_info = {
    "name": "Brender",
    "author": "Pampa Nie",
    "description": "",
    "blender": (2, 82, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic"
}

import bpy
import os
import pathlib
import sys
from . import auto_load

brender_addon_path = pathlib.Path(__file__).parent.absolute()
sep = os.path.sep
lib_path = str(brender_addon_path) + sep + 'libs/pika-1.1.0'
print(lib_path)
sys.path.append(lib_path)
lib_path = str(brender_addon_path) + sep + 'libs/avro-python3-1.9.2'
sys.path.append(lib_path)

lib_path = str(brender_addon_path) + sep + 'libs/qiniu-python-sdk-7.2.8'
sys.path.append(lib_path)

lib_path = str(brender_addon_path) + sep + 'libs/hashids-1.2.0'
sys.path.append(lib_path)


auto_load.init()



def register():
    auto_load.register()



def unregister():
    auto_load.unregister()


