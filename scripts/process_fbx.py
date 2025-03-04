#!/usr/bin/env python3
import bpy
import json
import sys
import os
import math
import bmesh
from mathutils import Vector

def setup_scene():
    """Clear existing scene and set up for FBX processing."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for collection in bpy.data.collections:
        bpy.context.scene.collection.children.unlink(collection)
    for obj in bpy.data.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

def import_fbx(fbx_path):
    """Import FBX file and return success status."""
    try:
        bpy.ops.import_scene.fbx(filepath=fbx_path)
        return len(bpy.context.selected_objects) > 0
    except Exception as e:
        print(f"Error importing FBX: {str(e)}")
        return False

def optimize_mesh(obj, max_triangles):
    """Optimize mesh to meet triangle count requirements."""
    if obj.type != 'MESH':
        return
        
    mesh = obj.data
    initial_tris = len(mesh.polygons)
    
    if initial_tris <= max_triangles:
        return
    
    # Calculate ratio for decimation
    ratio = max_triangles / initial_tris
    
    # Add decimate modifier
    decimate = obj.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.ratio = ratio
    decimate.use_collapse_triangulate = True
    
    # Apply modifier
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=decimate.name)

def setup_materials(obj):
    """Set up proper materials for Roblox compatibility."""
    if obj.type != 'MESH':
        return
        
    # Ensure object has at least one material
    if len(obj.material_slots) == 0:
        mat = bpy.data.materials.new(name=f"{obj.name}_material")
        mat.use_nodes = True
        obj.data.materials.append(mat)
    
    # Set up basic PBR materials
    for slot in obj.material_slots:
        if slot.material:
            mat = slot.material
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            
            # Clear existing nodes
            nodes.clear()
            
            # Add basic PBR setup
            principled = nodes.new('ShaderNodeBsdfPrincipled')
            output = nodes.new('ShaderNodeOutputMaterial')
            
            # Link nodes
            mat.node_tree.links.new(principled.outputs[0], output.inputs[0])
            
            # Set default values for Roblox
            principled.inputs['Metallic'].default_value = 0.0
            principled.inputs['Roughness'].default_value = 0.5
            principled.inputs['Specular'].default_value = 0.5

def verify_uv_maps(obj):
    """Ensure proper UV mapping."""
    if obj.type != 'MESH' and len(obj.data.uv_layers) == 0:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.mesh.uv_texture_add()

def process_armature(obj, outfit_type):
    """Process armature for Roblox compatibility."""
    if obj.type != 'ARMATURE':
        return
        
    # Rename bones to match Roblox convention if needed
    bone_mapping = {
        'Hips': 'HumanoidRootPart',
        'Spine': 'UpperTorso',
        'Spine1': 'LowerTorso',
        'LeftUpLeg': 'LeftUpperLeg',
        'RightUpLeg': 'RightUpperLeg',
        'LeftLeg': 'LeftLowerLeg',
        'RightLeg': 'RightLowerLeg',
        'LeftFoot': 'LeftFoot',
        'RightFoot': 'RightFoot',
        'LeftArm': 'LeftUpperArm',
        'RightArm': 'RightUpperArm',
        'LeftForeArm': 'LeftLowerArm',
        'RightForeArm': 'RightLowerArm',
        'LeftHand': 'LeftHand',
        'RightHand': 'RightHand'
    }
    
    for bone in obj.data.bones:
        if bone.name in bone_mapping:
            bone.name = bone_mapping[bone.name]

def get_mesh_stats():
    """Get statistics about the current meshes."""
    stats = {
        'initial': {
            'vertices': 0,
            'triangles': 0,
            'materials': 0,
            'uv_layers': 0
        },
        'final': {
            'vertices': 0,
            'triangles': 0,
            'materials': 0,
            'uv_layers': 0
        }
    }
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            stats['final']['vertices'] += len(mesh.vertices)
            stats['final']['triangles'] += len(mesh.polygons)
            stats['final']['materials'] += len(obj.material_slots)
            stats['final']['uv_layers'] += len(mesh.uv_layers)
    
    return stats

def main():
    # Get command line arguments
    if len(sys.argv) < 6:
        print(json.dumps({
            'success': False,
            'error': 'Missing required arguments: input_path output_path outfit_type'
        }))
        sys.exit(1)
        
    input_path = sys.argv[-3]
    output_path = sys.argv[-2]
    outfit_type = sys.argv[-1]
    
    try:
        # Clear scene and import FBX
        setup_scene()
        if not import_fbx(input_path):
            raise Exception("Failed to import FBX file")
            
        # Get initial stats
        initial_stats = get_mesh_stats()
        
        # Process each object
        modifications = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                # Optimize mesh
                optimize_mesh(obj, 8000)  # Default triangle limit
                modifications.append('mesh_optimization')
                
                # Setup materials
                setup_materials(obj)
                modifications.append('material_setup')
                
                # Verify UV maps
                verify_uv_maps(obj)
                modifications.append('uv_verification')
                
            elif obj.type == 'ARMATURE':
                # Process armature
                process_armature(obj, outfit_type)
                modifications.append('armature_processing')
        
        # Get final stats
        final_stats = get_mesh_stats()
        
        # Export processed FBX
        bpy.ops.export_scene.fbx(
            filepath=output_path,
            use_selection=False,
            global_scale=1.0,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_NONE',
            bake_space_transform=False,
            object_types={'ARMATURE', 'MESH'},
            use_mesh_modifiers=True,
            mesh_smooth_type='OFF',
            use_subsurf=False,
            use_mesh_edges=False,
            use_tspace=False,
            use_custom_props=False,
            add_leaf_bones=False,
            primary_bone_axis='Y',
            secondary_bone_axis='X',
            use_armature_deform_only=True,
            armature_nodetype='NULL',
            path_mode='COPY'
        )
        
        # Prepare and return processing summary
        result = {
            'success': True,
            'stats': {
                'initial_state': initial_stats,
                'final_state': final_stats,
                'processing_summary': {
                    'validation_status': 'success',
                    'geometry_change': {
                        'vertices_delta': final_stats['final']['vertices'] - initial_stats['initial']['vertices'],
                        'triangles_delta': final_stats['final']['triangles'] - initial_stats['initial']['triangles']
                    },
                    'modifications_applied': list(set(modifications))
                }
            }
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }))
        sys.exit(1)

if __name__ == "__main__":
    main() 