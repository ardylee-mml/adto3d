import subprocess
import sys
import os

def verify_blender():
    try:
        # Check Blender version
        result = subprocess.run(['blender', '--version'], 
                              capture_output=True, 
                              text=True)
        print("Blender version:", result.stdout)

        # Check if Blender can run in background mode
        test_cmd = ['blender', '--background', '--python-expr', 'import bpy; print("Blender Python works")']
        result = subprocess.run(test_cmd, 
                              capture_output=True, 
                              text=True)
        print("\nBlender Python test:", result.stdout)

        # Check if FBX export is available
        test_script = '''
import bpy
print("FBX addon status:", hasattr(bpy.ops, 'export_scene.fbx'))
'''
        result = subprocess.run(['blender', '--background', '--python-expr', test_script],
                              capture_output=True,
                              text=True)
        print("\nFBX addon test:", result.stdout)

        return True

    except Exception as e:
        print(f"Error verifying Blender: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    verify_blender() 