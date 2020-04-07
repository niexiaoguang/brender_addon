import bpy
from pathlib import Path
import time
import json
print('brender output ******** : blender in background with local_prepare.py script')

# use custom fuction to purge
def purge_orphans():
    bpc = bpy.types.bpy_prop_collection

    for data in [eval("bpy.data.%s" % i) for i in dir(bpy.data)]:
        if type(data) is bpc and hasattr(data, 'remove'):
            remove = data.remove
            for obj in data:
                if not obj.users:
                    remove(obj)

# purge orphan data and save
purge_orphans()
bpy.ops.wm.save_mainfile()



imageFilesDict = {}

for i in bpy.data.images:
    # except render result image 
    # and etc. TODO
    if(i.filepath and i.name != 'Render Result'):
        print(i.name)
        i.pack()
        # time.sleep(0.5)
        i.unpack()
        relpath = bpy.path.relpath(i.filepath)
        abspath =  bpy.path.abspath(i.filepath)
        # avoid recount images use many times
        imageFilesDict[relpath] = abspath

print(imageFilesDict)

currentProjPath = bpy.path.abspath('//')
saveProjName = "backup.blend"
saveProjPath = currentProjPath + saveProjName
print(saveProjPath)
saveProjPath = bpy.path.native_pathsep(saveProjPath)
bpy.ops.wm.save_as_mainfile(filepath = saveProjPath,compress=True)


# gererate file tree summary json and dump to disk 
jsonStr = json.dumps(imageFilesDict)
jsonFileName = 'backup.json' # TODO
# use pathlib to handle path
currentProjPath = Path(bpy.path.abspath('//'))
jsonFilePath = currentProjPath / jsonFileName
with jsonFilePath.open('w') as f:
    f.write(jsonStr)
