import bpy
import sys
import json

# Usage: blender --background --python extract_blend_info.py -- <blendfile>
if '--' not in sys.argv:
    print(json.dumps({"error": "No blend file specified"}))
    sys.exit(1)

blendfile = sys.argv[sys.argv.index('--') + 1]

try:
    bpy.ops.wm.open_mainfile(filepath=blendfile)
    version = bpy.app.version_string
    scenes = [scene.name for scene in bpy.data.scenes]
    info = {
        "version": version,
        "scenes": scenes
    }
    print(json.dumps(info))
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
