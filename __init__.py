bl_info = {
    "name" : "Brender",
    "author" : "Pampa Nie",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "Render > Engine > Brender",
    "warning" : "",
    "category" : "Generic"
}

if "bpy" in locals():
    from importlib import reload
    brender_panel = reload(brender_panel)
    blender_bg = reload(blender_bg)
else:
    from . import brender_panel,blender_bg

import bpy
import requests
import time
import shutil
import os
import threading
import subprocess

def register():
    print ("Registering ", __name__)
    brender_panel.register_panel()
    blender_bg.register()

def unregister():
    print ("Unregistering ", __name__)
    brender_panel.unregister_panel()
    blender_bg.unregister()


if __name__ == "__main__":
    register()
