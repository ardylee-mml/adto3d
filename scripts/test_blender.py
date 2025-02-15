import bpy
import sys
import os

print(f"Python version: {sys.version}")
print(f"Blender version: {bpy.app.version_string}")
print(f"Python path: {sys.path}")

try:
    from rembg import remove
    print("rembg is installed")
except ImportError:
    print("rembg is not installed")

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Save the file
bpy.ops.wm.save_as_mainfile(filepath="test.blend")
