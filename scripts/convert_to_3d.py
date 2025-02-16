import bpy
import json
import sys
import os
import math

# Set color management
scene = bpy.context.scene
scene.view_settings.view_transform = 'Standard'
scene.display_settings.display_device = 'sRGB'

def load_analysis(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_3d_model(analysis, image_path, output_path):
    print(f"Creating 3D model with analysis: {analysis}")
    print(f"Using image: {image_path}")
    print(f"Output path: {output_path}")

    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a cylinder for the can/box
    if analysis['shape']['type'] == 'cylindrical':
        print("Creating cylindrical object...")
        # Create cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.0,
            depth=2.0,
            segments=32
        )
    else:
        print("Creating box object...")
        # Create a box for non-cylindrical objects
        bpy.ops.mesh.primitive_cube_add(size=1.0)

    obj = bpy.context.active_object
    
    # Set dimensions based on analysis
    width = analysis['dimensions']['width'] / 100
    height = analysis['dimensions']['height'] / 100
    obj.scale = (width, width, height)

    print(f"Applied dimensions: width={width}, height={height}")

    # Add material and texture
    try:
        mat = bpy.data.materials.new(name="ObjectMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        
        # Add image texture
        tex_image = nodes.new('ShaderNodeTexImage')
        tex_image.image = bpy.data.images.load(image_path)
        
        # Link texture to material
        principled = nodes.get('Principled BSDF')
        mat.node_tree.links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
        
        # Assign material to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
            
        print("Successfully applied material and texture")
    except Exception as e:
        print(f"Error applying material: {str(e)}")

    # Export as GLB
    try:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=False
        )
        print(f"Successfully exported model to: {output_path}")
    except Exception as e:
        print(f"Export error: {str(e)}")

def main():
    # Get command line arguments
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) < 2:
        print("Error: Missing required arguments")
        sys.exit(1)

    analysis_path = args[0]
    output_path = args[1]

    # Check if analysis file exists
    if not os.path.exists(analysis_path):
        print(f"Error: Analysis file not found at {analysis_path}")
        sys.exit(1)

    try:
        with open(analysis_path, 'r') as f:
            analysis = json.load(f)
    except Exception as e:
        print(f"Error reading analysis file: {e}")
        sys.exit(1)

    # Your 3D generation logic here
    # ...

    try:
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 