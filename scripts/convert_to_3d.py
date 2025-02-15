try:
    import bpy
    import sys
    import os
    import math
    import bmesh
except ImportError:
    pass  # Running outside of Blender

# Get command line arguments after '--'
argv = sys.argv
argv = argv[argv.index("--") + 1:]

input_path = argv[0]
output_path = argv[1]

def create_cylinder_model():
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Create a cylinder
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=64,
        radius=1.0,
        depth=2.0,
        enter_editmode=False,
        align='WORLD'
    )
    cylinder = bpy.context.active_object
    
    # Create material
    mat = bpy.data.materials.new(name="CanMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Create nodes
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    tex_image = nodes.new('ShaderNodeTexImage')
    tex_coord = nodes.new('ShaderNodeTexCoord')
    mapping = nodes.new('ShaderNodeMapping')
    output = nodes.new('ShaderNodeOutputMaterial')
    
    # Position nodes
    output.location = (300, 0)
    principled.location = (0, 0)
    tex_image.location = (-300, 0)
    tex_coord.location = (-900, 0)
    mapping.location = (-600, 0)
    
    # Load image
    print(f"Loading image from: {input_path}")
    image = bpy.data.images.load(input_path)
    tex_image.image = image
    
    # Setup mapping
    mapping.inputs['Rotation'].default_value = (0, 0, math.pi/2)
    mapping.inputs['Scale'].default_value = (1.0, 2.0, 1.0)  # Adjusted scale
    
    # Connect nodes
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
    links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    # Material settings
    principled.inputs['Metallic'].default_value = 0.8
    principled.inputs['Roughness'].default_value = 0.2
    principled.inputs['Specular IOR Level'].default_value = 0.5
    
    # Assign material
    cylinder.data.materials.append(mat)
    
    # UV Unwrap
    bpy.context.view_layer.objects.active = cylinder
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Get the BMesh
    bm = bmesh.from_edit_mesh(cylinder.data)
    
    # Mark seams
    for edge in bm.edges:
        if abs(edge.verts[0].co.x - edge.verts[1].co.x) < 0.0001 and edge.verts[0].co.y > 0:
            edge.seam = True
    
    # Update the mesh
    bmesh.update_edit_mesh(cylinder.data)
    
    # Select all and unwrap
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    
    # Project from view
    bpy.ops.uv.cylinder_project(
        direction='VIEW_ON_EQUATOR',
        align='POLAR_ZX',
        scale_to_bounds=True
    )
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Add smooth shading
    bpy.ops.object.shade_smooth()
    
    # Export GLB
    print(f"Exporting to: {output_path}")
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=True,
        export_apply=True,
        export_texture_dir="",
        will_save_settings=True
    )
    
    print(f"Export completed")

if __name__ == "__main__":
    try:
        create_cylinder_model()
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        sys.exit(1) 