import bpy
import json
import sys
import os
import math

def load_analysis(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def create_3d_model(analysis, image_path, output_path):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a cylinder for the can
    if analysis['shape']['type'] == 'cylindrical':
        # Create cylinder
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.0,
            depth=2.0,
            segments=32
        )
        can = bpy.context.active_object

        # Scale the cylinder based on image dimensions
        height = analysis['dimensions']['height'] / 100
        diameter = analysis['dimensions']['width'] / (100 * math.pi)  # Adjust for circumference
        can.scale = (diameter, diameter, height)

        # Smooth the cylinder
        bpy.ops.object.shade_smooth()
        
        # Add edge split modifier for sharp edges
        edge_split = can.modifiers.new(name="Edge Split", type='EDGE_SPLIT')
        edge_split.split_angle = math.radians(30)
    else:
        # Fallback to plane for non-cylindrical objects
        bpy.ops.mesh.primitive_plane_add(size=1)
        can = bpy.context.active_object
        can.scale.x = analysis['dimensions']['width'] / 100
        can.scale.y = analysis['dimensions']['height'] / 100

    # Add material
    mat = bpy.data.materials.new(name="CanMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    nodes.clear()
    
    # Create nodes
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    
    # Add image texture
    try:
        if os.path.exists(image_path):
            print(f"Loading image from: {image_path}")
            tex_image = nodes.new('ShaderNodeTexImage')
            tex_image.image = bpy.data.images.load(image_path)
            
            # Add mapping nodes for proper cylinder unwrap
            mapping = nodes.new('ShaderNodeMapping')
            tex_coord = nodes.new('ShaderNodeTexCoord')
            
            # Link nodes
            links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
            links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
            links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
            
            # Adjust mapping for cylinder
            if analysis['shape']['type'] == 'cylindrical':
                mapping.inputs['Scale'].default_value[0] = 1.0
                mapping.inputs['Scale'].default_value[1] = 2.0
        else:
            print(f"Image not found at: {image_path}, using fallback color")
            rgb = analysis['color']['average_rgb']
            principled.inputs['Base Color'].default_value = (rgb[0]/255, rgb[1]/255, rgb[2]/255, 1)
    except Exception as e:
        print(f"Error loading texture: {e}")
        rgb = analysis['color']['average_rgb']
        principled.inputs['Base Color'].default_value = (rgb[0]/255, rgb[1]/255, rgb[2]/255, 1)

    # Link output
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign material
    if can.data.materials:
        can.data.materials[0] = mat
    else:
        can.data.materials.append(mat)

    # Set up UV mapping
    bpy.context.view_layer.objects.active = can
    bpy.ops.object.mode_set(mode='EDIT')
    if analysis['shape']['type'] == 'cylindrical':
        bpy.ops.uv.cylinder_project(scale_to_bounds=True)
    else:
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Export as GLB
    try:
        bpy.ops.export_scene.gltf(
            filepath=output_path,
            export_format='GLB',
            use_selection=False,
            export_materials=True,
            export_colors=True,
            export_image_format='AUTO'
        )
        print(f"Successfully exported to: {output_path}")
    except Exception as e:
        print(f"Export error: {str(e)}")
        try:
            bpy.ops.export_scene.gltf(
                filepath=output_path,
                export_format='GLB'
            )
            print(f"Successfully exported with basic settings to: {output_path}")
        except Exception as e2:
            print(f"Alternative export also failed: {str(e2)}")
            raise

def main():
    if len(sys.argv) < 5:
        print("Usage: blender --background --python script.py -- <json_path> <output_path>")
        sys.exit(1)

    json_path = sys.argv[-2]
    output_path = sys.argv[-1]
    image_path = json_path.replace('.json', '').replace('/output/', '/uploads/')
    
    print(f"Using image path: {image_path}")
    
    try:
        analysis = load_analysis(json_path)
        create_3d_model(analysis, image_path, output_path)
    except Exception as e:
        print(f"Error during model creation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 