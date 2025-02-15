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

print(f"Loading image from: {input_path}")

try:
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Create a plane
    bpy.ops.mesh.primitive_plane_add(size=2)
    plane = bpy.context.active_object

    # Create new material
    mat = bpy.data.materials.new(name="Image_Mat")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes

    # Clear default nodes
    nodes.clear()

    # Create nodes
    principled_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    material_output = nodes.new('ShaderNodeOutputMaterial')
    texture_image = nodes.new('ShaderNodeTexImage')

    # Load image
    texture_image.image = bpy.data.images.load(input_path)

    # Link nodes
    links = mat.node_tree.links
    links.new(texture_image.outputs[0], principled_bsdf.inputs[0])
    links.new(principled_bsdf.outputs[0], material_output.inputs[0])

    # Assign material to plane
    plane.data.materials.append(mat)

    # Export as glb
    output_path = output_path.replace('.gltf', '.glb')
    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLB',
        use_selection=False
    )
    
    print(f"Successfully exported to: {output_path}")

except Exception as e:
    print(f"Error during conversion: {str(e)}")
    sys.exit(1) 