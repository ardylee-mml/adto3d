import bpy
import sys
import os

def test_blender_setup():
    try:
        # Clear existing objects
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Print environment info
        print(f"Python version: {sys.version}")
        print(f"Blender version: {bpy.app.version_string}")
        print(f"Working directory: {os.getcwd()}")

        # Create test directory with absolute path
        test_dir = os.path.abspath(os.path.join(os.getcwd(), 'test'))
        os.makedirs(test_dir, exist_ok=True)
        print(f"Test directory: {test_dir}")

        # Create a simple cube
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        print(f"Created cube: {cube.name}")

        # Set up the scene
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.render.film_transparent = True

        # Export as FBX with absolute path
        test_file = os.path.join(test_dir, 'test.fbx')
        print(f"Exporting to: {test_file}")
        
        bpy.ops.export_scene.fbx(
            filepath=test_file,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            bake_space_transform=False,
            object_types={'MESH'},
            use_mesh_modifiers=True,
            mesh_smooth_type='OFF',
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=False,
            bake_anim=False,
            path_mode='ABSOLUTE'
        )

        print("Test successful!")
        print(f"Test file created at: {test_file}")
        
        # Save blend file with absolute path
        blend_file = os.path.join(test_dir, 'test.blend')
        bpy.ops.wm.save_as_mainfile(filepath=blend_file)
        print(f"Blend file saved at: {blend_file}")
        
        return True

    except Exception as e:
        print(f"Error during test: {str(e)}", file=sys.stderr)
        return False

if __name__ == "__main__":
    test_blender_setup()
