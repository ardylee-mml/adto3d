import os
import sys
import json
import requests
import time
from dotenv import load_dotenv
from mpx_genai_sdk import Masterpiecex
import argparse
import logging
from PIL import Image
import trimesh
import numpy as np
import subprocess
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Debug logging for environment
logger.info("=== ENVIRONMENT VERIFICATION ===")
logger.info(f"Current working directory: {os.getcwd()}")
token = os.getenv('MPX_SDK_BEARER_TOKEN')
logger.info(f"MPX_SDK_BEARER_TOKEN exists: {bool(token)}")
logger.info(f"Env file location: {os.path.join(os.path.dirname(__file__), '..', '.env')}")
logger.info("===============================")

# Set MPX_API_KEY from bearer token for SDK compatibility
if token and 'MPX_API_KEY' not in os.environ:
    os.environ['MPX_API_KEY'] = token

ROBLOX_STYLE_CONFIG = {
    "output_format": "glb",
    "polygon_limit": 1000,
    "texture_size": 512,
    "style_preset": "low_poly",
    "shading": "toon",
    "scale_factor": 0.01  # Roblox world scale
}

# Roblox configuration for different outfit types
ROBLOX_CONFIG = {
    'clothes': {
        'max_triangles': 8000,
        'skeleton': 'R15',
        'bones': [
            'HumanoidRootNode', 'Torso', 'UpperTorso', 'LowerTorso',
            'RightArm', 'RightForearm', 'LeftArm', 'LeftForearm',
            'RightLeg', 'RightForeleg', 'LeftLeg', 'LeftForeleg'
        ],
        'uv_regions': {
            'shirt': {'top': [0, 0, 1, 0.5], 'bottom': [0, 0.5, 1, 1]},
            'pants': {'legs': [0, 0, 1, 1]}
        }
    },
    'hats': {
        'max_triangles': 2000,
        'size_limits': {'x': 500, 'y': 500, 'z': 500},
        'attachments': ['HeadAttachment'],
        'needs_rigging': False
    },
    'shoes': {
        'max_triangles': 1500,
        'size_limits': {'x': 200, 'y': 200, 'z': 200},
        'attachments': ['LeftFootAttachment', 'RightFootAttachment'],
        'needs_rigging': True,
        'bones': ['LeftFoot', 'RightFoot']
    }
}

def process_fbx_for_roblox(fbx_path, outfit_type):
    """Process FBX file according to Roblox requirements using Blender."""
    try:
        temp_dir = os.path.join(os.path.dirname(fbx_path), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        script_path = os.path.join(temp_dir, 'process.py')
        with open(script_path, 'w') as f:
            f.write(f"""
import bpy
import os
import bmesh
import math
from mathutils import Vector, Matrix

def optimize_mesh(obj, max_triangles, target_quality='high'):
    # Triangulate with specific settings
    bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new(type='TRIANGULATE', name='Triangulate')
    mod.quad_method = 'BEAUTY'
    mod.keep_custom_normals = True
    bpy.ops.object.modifier_apply(modifier='Triangulate')
    
    # Check triangle count and optimize if needed
    if len(obj.data.polygons) > max_triangles:
        # First try beauty method
        mod = obj.modifiers.new(name='Decimate', type='DECIMATE')
        mod.ratio = max_triangles / len(obj.data.polygons)
        mod.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier='Decimate')
        
        # If still too high, use more aggressive decimation
        if len(obj.data.polygons) > max_triangles:
            mod = obj.modifiers.new(name='Decimate', type='DECIMATE')
            mod.ratio = (max_triangles * 0.9) / len(obj.data.polygons)
            bpy.ops.object.modifier_apply(modifier='Decimate')

def setup_r15_armature():
    bpy.ops.object.armature_add()
    armature = bpy.context.active_object
    armature.name = 'R15_Armature'
    
    # Enhanced R15 bone structure with proper connections
    bones = {{
        'HumanoidRootNode': {{'pos': Vector((0, 0, 0)), 'parent': None}},
        'LowerTorso': {{'pos': Vector((0, 0, 1)), 'parent': 'HumanoidRootNode'}},
        'UpperTorso': {{'pos': Vector((0, 0, 2)), 'parent': 'LowerTorso'}},
        'Head': {{'pos': Vector((0, 0, 3)), 'parent': 'UpperTorso'}},
        'LeftUpperArm': {{'pos': Vector((-0.5, 0, 2.5)), 'parent': 'UpperTorso'}},
        'LeftLowerArm': {{'pos': Vector((-1, 0, 2.3)), 'parent': 'LeftUpperArm'}},
        'LeftHand': {{'pos': Vector((-1.5, 0, 2.1)), 'parent': 'LeftLowerArm'}},
        'RightUpperArm': {{'pos': Vector((0.5, 0, 2.5)), 'parent': 'UpperTorso'}},
        'RightLowerArm': {{'pos': Vector((1, 0, 2.3)), 'parent': 'RightUpperArm'}},
        'RightHand': {{'pos': Vector((1.5, 0, 2.1)), 'parent': 'RightLowerArm'}},
        'LeftUpperLeg': {{'pos': Vector((-0.2, 0, 0.8)), 'parent': 'LowerTorso'}},
        'LeftLowerLeg': {{'pos': Vector((-0.2, 0, 0.4)), 'parent': 'LeftUpperLeg'}},
        'LeftFoot': {{'pos': Vector((-0.2, 0, 0)), 'parent': 'LeftLowerLeg'}},
        'RightUpperLeg': {{'pos': Vector((0.2, 0, 0.8)), 'parent': 'LowerTorso'}},
        'RightLowerLeg': {{'pos': Vector((0.2, 0, 0.4)), 'parent': 'RightUpperLeg'}},
        'RightFoot': {{'pos': Vector((0.2, 0, 0)), 'parent': 'RightLowerLeg'}}
    }}
    
    # Create and connect bones
    bpy.ops.object.mode_set(mode='EDIT')
    created_bones = {{}}
    
    for name, data in bones.items():
        bone = armature.data.edit_bones.new(name)
        bone.head = data['pos']
        bone.tail = data['pos'] + Vector((0, 0, 0.2))
        created_bones[name] = bone
        
        if data['parent'] and data['parent'] in created_bones:
            bone.parent = created_bones[data['parent']]
            bone.use_connect = True
    
    bpy.ops.object.mode_set(mode='OBJECT')
    return armature

def verify_uv_mapping(obj, outfit_type):
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name='UVMap')
    
    # Get the active UV layer
    uv_layer = obj.data.uv_layers.active
    
    # UV validation stats
    stats = {{
        'overlapping': 0,
        'outside_bounds': 0,
        'total_uvs': len(uv_layer.data)
    }}
    
    # Check and fix UV coordinates
    for poly in obj.data.polygons:
        for loop_idx in poly.loop_indices:
            uv = uv_layer.data[loop_idx].uv
            
            # Check for overlapping UVs
            for other_poly in obj.data.polygons:
                if poly.index != other_poly.index:
                    for other_idx in other_poly.loop_indices:
                        other_uv = uv_layer.data[other_idx].uv
                        if (uv - other_uv).length < 0.001:
                            stats['overlapping'] += 1
            
            # Fix out-of-bounds UVs
            if uv.x < 0 or uv.x > 1 or uv.y < 0 or uv.y > 1:
                stats['outside_bounds'] += 1
                uv_layer.data[loop_idx].uv = Vector((
                    max(0, min(1, uv.x)),
                    max(0, min(1, uv.y))
                ))
    
    return stats

def add_collision(obj, collision_type='convex'):
    bpy.ops.object.duplicate()
    collision = bpy.context.active_object
    collision.name = f"{obj.name}_collision"
    
    if collision_type == 'convex':
        # Create convex hull for better performance
        mod = collision.modifiers.new(name='Convex Hull', type='REMESH')
        mod.mode = 'VOXEL'
        mod.octree_depth = 4
        bpy.ops.object.modifier_apply(modifier='Convex Hull')
    else:
        # Simplified mesh collision
        mod = collision.modifiers.new(name='Decimate', type='DECIMATE')
        mod.ratio = 0.3
        bpy.ops.object.modifier_apply(modifier='Decimate')
    
    # Add collision property
    collision.game.physics_type = 'STATIC'
    collision.game.use_collision_bounds = True
    collision.game.collision_bounds_type = 'CONVEX_HULL' if collision_type == 'convex' else 'TRIANGLE_MESH'
    
    collision.parent = obj
    collision.hide_viewport = True
    return collision

def verify_materials(obj):
    # Ensure PBR materials
    for mat_slot in obj.material_slots:
        if mat_slot.material:
            mat = mat_slot.material
            if not mat.use_nodes:
                mat.use_nodes = True
            
            # Set up basic PBR material
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            
            # Clear existing nodes
            nodes.clear()
            
            # Add basic PBR setup
            output = nodes.new('ShaderNodeOutputMaterial')
            principled = nodes.new('ShaderNodeBsdfPrincipled')
            links.new(principled.outputs[0], output.inputs[0])
            
            # Set default PBR values
            principled.inputs['Metallic'].default_value = 0.0
            principled.inputs['Roughness'].default_value = 0.7
            principled.inputs['Specular'].default_value = 0.5

def setup_animations(armature, outfit_type):
    if outfit_type == 'clothes':
        # Add basic pose library
        if not armature.pose_library:
            bpy.ops.pose.new_poselib()
        
        # Add default poses
        poses = {{
            'T_Pose': {{
                'LeftUpperArm': (0, 0, 90),
                'RightUpperArm': (0, 0, -90)
            }},
            'A_Pose': {{
                'LeftUpperArm': (0, 0, 45),
                'RightUpperArm': (0, 0, -45)
            }}
        }}
        
        for pose_name, bone_rotations in poses.items():
            bpy.ops.object.mode_set(mode='POSE')
            for bone_name, rotation in bone_rotations.items():
                if bone_name in armature.pose.bones:
                    bone = armature.pose.bones[bone_name]
                    bone.rotation_euler = [math.radians(r) for r in rotation]
            bpy.ops.poselib.pose_add(name=pose_name)

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import FBX
bpy.ops.import_scene.fbx(filepath='{fbx_path}')

# Get the imported objects
mesh_obj = None
armature_obj = None

# First clear any existing selection
bpy.ops.object.select_all(action='DESELECT')

# Find the mesh and armature objects
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        mesh_obj = obj
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_obj
    elif obj.type == 'ARMATURE':
        armature_obj = obj

if mesh_obj:
    # Process based on outfit type
    if '{outfit_type}' == 'clothes':
        if not armature_obj:
            armature_obj = setup_r15_armature()
        
        mesh_obj.scale = (1.0, 1.0, 1.0)
        optimize_mesh(mesh_obj, 8000, 'high')
        uv_stats = verify_uv_mapping(mesh_obj, '{outfit_type}')
        verify_materials(mesh_obj)
        
        if armature_obj:
            mod = mesh_obj.modifiers.new(type='ARMATURE', name="Armature")
            mod.object = armature_obj
            mesh_obj.parent = armature_obj
            setup_animations(armature_obj, '{outfit_type}')
            
            # Weight paint setup
            bpy.ops.paint.weight_paint_mode_toggle()
            bpy.ops.object.vertex_group_normalize_all()

    elif '{outfit_type}' == 'hats':
        max_dim = max(mesh_obj.dimensions)
        if max_dim > 5:
            scale_factor = 5 / max_dim
            mesh_obj.scale = (scale_factor, scale_factor, scale_factor)
        
        optimize_mesh(mesh_obj, 2000, 'medium')
        uv_stats = verify_uv_mapping(mesh_obj, '{outfit_type}')
        verify_materials(mesh_obj)
        
        # Add head attachment point
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        attachment = bpy.context.active_object
        attachment.name = 'HeadAttachment'
        attachment.parent = mesh_obj
        
        # Add optimized collision
        collision = add_collision(mesh_obj, 'convex')

    elif '{outfit_type}' == 'shoes':
        max_dim = max(mesh_obj.dimensions)
        if max_dim > 2:
            scale_factor = 2 / max_dim
            mesh_obj.scale = (scale_factor, scale_factor, scale_factor)
        
        optimize_mesh(mesh_obj, 1500, 'high')
        uv_stats = verify_uv_mapping(mesh_obj, '{outfit_type}')
        verify_materials(mesh_obj)
        
        for side in ['Left', 'Right']:
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            attachment = bpy.context.active_object
            attachment.name = f'{side}FootAttachment'
            attachment.parent = mesh_obj
        
        # Add detailed collision
        collision = add_collision(mesh_obj, 'mesh')

    # Common processing for all types
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.delete_loose()
    bpy.ops.mesh.dissolve_degenerate()
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Make sure the mesh object is selected for export
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    if armature_obj:
        armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # Export processed FBX
    output_path = '{fbx_path}'.replace('.fbx', '_roblox.fbx')
    bpy.ops.export_scene.fbx(
        filepath=output_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        bake_space_transform=True,
        use_mesh_modifiers=True,
        mesh_smooth_type='OFF',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_armature_deform_only=True,
        bake_anim=False
    )

    # Enhanced export statistics
    stats = {{
        'mesh': {{
            'triangles': len(mesh_obj.data.polygons),
            'vertices': len(mesh_obj.data.vertices),
            'edges': len(mesh_obj.data.edges),
            'uv_layers': len(mesh_obj.data.uv_layers),
            'vertex_groups': len(mesh_obj.vertex_groups),
            'materials': len(mesh_obj.material_slots),
            'dimensions': [mesh_obj.dimensions.x, mesh_obj.dimensions.y, mesh_obj.dimensions.z],
            'volume': mesh_obj.dimensions.x * mesh_obj.dimensions.y * mesh_obj.dimensions.z,
            'bounds_center': [mesh_obj.location.x, mesh_obj.location.y, mesh_obj.location.z]
        }},
        'uv_mapping': uv_stats,
        'armature': {{
            'exists': armature_obj is not None,
            'bones': len(armature_obj.data.bones) if armature_obj else 0,
            'has_animations': bool(armature_obj.animation_data) if armature_obj else False,
            'animation_details': {{
                'action_count': len(armature_obj.animation_data.actions) if armature_obj and armature_obj.animation_data else 0,
                'total_frames': sum(action.frame_range[1] - action.frame_range[0] for action in armature_obj.animation_data.actions) if armature_obj and armature_obj.animation_data else 0,
                'animation_types': [action.name for action in armature_obj.animation_data.actions] if armature_obj and armature_obj.animation_data else []
            }} if armature_obj and armature_obj.animation_data else None
        }} if armature_obj else None,
        'materials': [{{
            'name': mat.material.name if mat.material else 'None',
            'has_texture': bool(mat.material.use_nodes) if mat.material else False,
            'surface_properties': {{
                'type': mat.material.get('surface_type', 'Unknown') if mat.material else 'None',
                'transparency': mat.material.alpha if mat.material else 1.0,
                'reflectance': mat.material.metallic if mat.material else 0.0,
                'roughness': mat.material.roughness if mat.material else 0.5
            }} if mat.material else None
        }} for mat in mesh_obj.material_slots],
        'attachments': [child.name for child in mesh_obj.children if child.type == 'EMPTY'],
        'has_collision': any(child.name.endswith('_collision') for child in mesh_obj.children),
        'physics': {{
            'enabled': bool(mesh_obj.rigid_body or mesh_obj.soft_body),
            'type': 'rigid' if mesh_obj.rigid_body else 'soft' if mesh_obj.soft_body else 'none',
            'properties': {{
                'mass': mesh_obj.rigid_body.mass if mesh_obj.rigid_body else None,
                'friction': mesh_obj.rigid_body.friction if mesh_obj.rigid_body else None,
                'use_margin': mesh_obj.rigid_body.use_margin if mesh_obj.rigid_body else None,
                'collision_shape': mesh_obj.rigid_body.collision_shape if mesh_obj.rigid_body else None
            }} if mesh_obj.rigid_body or mesh_obj.soft_body else None
        }},
        'lod': {{
            'enabled': bool(mesh_obj.modifiers.get('LOD')),
            'levels': [{{
                'distance': mod.distance,
                'ratio': mod.ratio
            }} for mod in mesh_obj.modifiers if mod.type == 'DECIMATE' and 'LOD' in mod.name] if mesh_obj.modifiers.get('LOD') else []
        }},
        'constraints': [{{
            'type': const.type,
            'name': const.name,
            'target': const.target.name if const.target else None,
            'influence': const.influence
        }} for const in mesh_obj.constraints]
    }}
    
    with open(output_path + '_stats.json', 'w') as f:
        import json
        json.dump(stats, f, indent=2)
""")

        # Run Blender in background mode
        blender_cmd = [
            'blender',
            '--background',
            '--python', script_path
        ]
        
        result = subprocess.run(blender_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Blender processing failed: {result.stderr}")
            return None
            
        processed_path = fbx_path.replace('.fbx', '_roblox.fbx')
        stats_path = processed_path + '_stats.json'
        
        if os.path.exists(processed_path):
            # Enhanced validation
            if os.path.exists(stats_path):
                with open(stats_path, 'r') as f:
                    stats = json.load(f)
                    
                config = ROBLOX_CONFIG[outfit_type]
                validation_errors = []
                validation_warnings = []
                
                # Mesh validation
                if stats['mesh']['triangles'] > config['max_triangles']:
                    validation_errors.append(
                        f"Triangle count ({stats['mesh']['triangles']}) exceeds limit ({config['max_triangles']})"
                    )
                
                # Size validation
                if outfit_type in ['hats', 'shoes']:
                    size_limits = config['size_limits']
                    for i, dim in enumerate(['x', 'y', 'z']):
                        if stats['mesh']['dimensions'][i] > size_limits[dim]:
                            validation_errors.append(
                                f"{dim.upper()} dimension ({stats['mesh']['dimensions'][i]}) exceeds limit ({size_limits[dim]})"
                            )
                
                # UV mapping validation
                if stats['uv_mapping']['overlapping'] > 0:
                    validation_warnings.append(
                        f"Found {stats['uv_mapping']['overlapping']} overlapping UVs"
                    )
                if stats['uv_mapping']['outside_bounds'] > 0:
                    validation_warnings.append(
                        f"Found {stats['uv_mapping']['outside_bounds']} UVs outside 0-1 range (fixed)"
                    )
                
                # Armature validation for clothes
                if outfit_type == 'clothes':
                    if not stats['armature']:
                        validation_errors.append("Missing required armature for clothes")
                    elif stats['armature']['bones'] < len(config['bones']):
                        validation_errors.append(
                            f"Insufficient bones ({stats['armature']['bones']}) for R15 skeleton"
                        )
                
                # Attachment validation
                required_attachments = config.get('attachments', [])
                existing_attachments = stats['attachments']
                missing_attachments = [att for att in required_attachments if att not in existing_attachments]
                if missing_attachments:
                    validation_errors.append(f"Missing required attachments: {', '.join(missing_attachments)}")
                
                # Material validation
                if not stats['materials']:
                    validation_warnings.append("No materials found")
                else:
                    untextured_materials = [mat['name'] for mat in stats['materials'] if not mat['has_texture']]
                    if untextured_materials:
                        validation_warnings.append(f"Untextured materials found: {', '.join(untextured_materials)}")
                
                # Collision validation
                if outfit_type in ['hats', 'shoes'] and not stats['has_collision']:
                    validation_errors.append("Missing collision geometry")
                
                if validation_errors:
                    logger.error("Validation errors:")
                    for error in validation_errors:
                        logger.error(f"- {error}")
                
                if validation_warnings:
                    logger.warning("Validation warnings:")
                    for warning in validation_warnings:
                        logger.warning(f"- {warning}")
                
                logger.info("Model statistics:")
                logger.info(json.dumps(stats, indent=2))
            
            logger.info(f"FBX processing completed: {processed_path}")
            return processed_path
        else:
            logger.error("Processed FBX file not found")
            return None
        
    except Exception as e:
        logger.error(f"Error processing FBX: {str(e)}")
        return None
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def download_file(url, output_path):
    """Download a file from URL and save it to the specified path."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"File saved to: {output_path}")
            return True
        else:
            logger.error(f"Failed to download file: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return False

def verify_model_for_roblox(mesh_path, outfit_type):
    """Verify and log model statistics for Roblox requirements."""
    try:
        # Load the mesh
        mesh = trimesh.load(mesh_path)
        
        # Get basic statistics
        stats = {
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
            'bounds': mesh.bounds.tolist(),
            'volume': float(mesh.volume),
            'area': float(mesh.area),
            'performance_metrics': {
                'geometry': {
                    'vertex_density': len(mesh.vertices) / float(mesh.area) if mesh.area > 0 else 0,
                    'triangle_density': len(mesh.faces) / float(mesh.area) if mesh.area > 0 else 0,
                    'mesh_complexity': len(mesh.edges) / len(mesh.vertices),
                    'vertex_cache_ratio': len(mesh.vertices) / (len(mesh.faces) * 3),
                    'validation': []
                },
                'textures': {
                    'total_size': 0,
                    'texture_count': 0,
                    'memory_usage': 0,
                    'validation': []
                },
                'materials': {
                    'unique_materials': 0,
                    'transparent_count': 0,
                    'pbr_count': 0,
                    'validation': []
                },
                'animation': {
                    'keyframe_density': 0,
                    'bone_count': 0,
                    'animation_length': 0,
                    'validation': []
                },
                'physics': {
                    'collision_complexity': 0,
                    'joint_count': 0,
                    'constraint_count': 0,
                    'validation': []
                },
                'optimization': {
                    'uv_efficiency': 0,
                    'bone_weights_per_vertex': 0,
                    'draw_call_estimate': 0,
                    'validation': []
                }
            },
            'roblox_features': {
                'animations': {
                    'present': False,
                    'count': 0,
                    'types': [],
                    'total_frames': 0,
                    'validation': []
                },
                'physics': {
                    'present': False,
                    'properties': {},
                    'validation': []
                },
                'lod': {
                    'present': False,
                    'levels': [],
                    'validation': []
                },
                'surfaces': {
                    'present': False,
                    'properties': {},
                    'validation': []
                },
                'constraints': {
                    'present': False,
                    'types': [],
                    'validation': []
                }
            }
        }

        # Performance validation thresholds
        perf_thresholds = {
            'vertex_density': {'warning': 0.1, 'error': 0.2},
            'triangle_density': {'warning': 0.05, 'error': 0.1},
            'mesh_complexity': {'warning': 2.5, 'error': 3.0},
            'vertex_cache_ratio': {'warning': 0.8, 'error': 0.9},
            'texture_memory': {'warning': 1024 * 1024 * 10, 'error': 1024 * 1024 * 20},  # 10MB, 20MB
            'material_count': {'warning': 3, 'error': 5},
            'keyframe_density': {'warning': 2, 'error': 4},
            'bone_weights': {'warning': 4, 'error': 6}
        }

        # Geometry performance checks
        geom_metrics = stats['performance_metrics']['geometry']
        if geom_metrics['vertex_density'] > perf_thresholds['vertex_density']['error']:
            geom_metrics['validation'].append(
                f"Error: Very high vertex density ({geom_metrics['vertex_density']:.2f}). Consider reducing vertex count."
            )
        elif geom_metrics['vertex_density'] > perf_thresholds['vertex_density']['warning']:
            geom_metrics['validation'].append(
                f"Warning: High vertex density ({geom_metrics['vertex_density']:.2f}). May impact performance."
            )

        if geom_metrics['triangle_density'] > perf_thresholds['triangle_density']['error']:
            geom_metrics['validation'].append(
                f"Error: Very high triangle density ({geom_metrics['triangle_density']:.2f}). Consider mesh decimation."
            )
        elif geom_metrics['triangle_density'] > perf_thresholds['triangle_density']['warning']:
            geom_metrics['validation'].append(
                f"Warning: High triangle density ({geom_metrics['triangle_density']:.2f}). May impact performance."
            )

        # Check for non-manifold edges and vertices
        non_manifold_edges = mesh.edges_unique[mesh.edges_unique_inverse.sum(axis=1) > 2]
        if len(non_manifold_edges) > 0:
            geom_metrics['validation'].append(
                f"Error: Found {len(non_manifold_edges)} non-manifold edges. This may cause rendering issues."
            )

        # Check for degenerate triangles
        areas = mesh.area_faces
        degenerate_faces = np.sum(areas < 1e-8)
        if degenerate_faces > 0:
            geom_metrics['validation'].append(
                f"Error: Found {degenerate_faces} degenerate triangles. Clean up mesh geometry."
            )

        # Material and texture performance checks
        if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'material'):
            mat_metrics = stats['performance_metrics']['materials']
            tex_metrics = stats['performance_metrics']['textures']
            
            # Calculate texture memory usage
            if hasattr(mesh.visual.material, 'image'):
                tex_metrics['texture_count'] += 1
                tex_size = mesh.visual.material.image.size
                tex_metrics['total_size'] += tex_size[0] * tex_size[1] * 4  # RGBA
                tex_metrics['memory_usage'] = tex_metrics['total_size'] / (1024 * 1024)  # Convert to MB
                
                if tex_metrics['memory_usage'] > perf_thresholds['texture_memory']['error']:
                    tex_metrics['validation'].append(
                        f"Error: Very high texture memory usage ({tex_metrics['memory_usage']:.1f}MB). Reduce texture sizes."
                    )
                elif tex_metrics['memory_usage'] > perf_thresholds['texture_memory']['warning']:
                    tex_metrics['validation'].append(
                        f"Warning: High texture memory usage ({tex_metrics['memory_usage']:.1f}MB). Consider optimization."
                    )

        # Animation performance checks
        if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'animation'):
            anim_metrics = stats['performance_metrics']['animation']
            
            # Calculate keyframe density
            total_bones = len(getattr(mesh, 'bones', []))
            total_frames = sum(anim.frame_count for anim in mesh.visual.animation)
            anim_metrics['bone_count'] = total_bones
            anim_metrics['animation_length'] = total_frames
            
            if total_bones > 0:
                anim_metrics['keyframe_density'] = total_frames / total_bones
                
                if anim_metrics['keyframe_density'] > perf_thresholds['keyframe_density']['error']:
                    anim_metrics['validation'].append(
                        f"Error: Very high keyframe density ({anim_metrics['keyframe_density']:.1f}). Reduce animation complexity."
                    )
                elif anim_metrics['keyframe_density'] > perf_thresholds['keyframe_density']['warning']:
                    anim_metrics['validation'].append(
                        f"Warning: High keyframe density ({anim_metrics['keyframe_density']:.1f}). Consider optimization."
                    )

        # Physics performance checks
        phys_metrics = stats['performance_metrics']['physics']
        if hasattr(mesh, 'physics_properties'):
            collision_mesh = getattr(mesh, 'collision_mesh', None)
            if collision_mesh:
                phys_metrics['collision_complexity'] = len(collision_mesh.faces) / len(mesh.faces)
                
                if phys_metrics['collision_complexity'] > 0.5:
                    phys_metrics['validation'].append(
                        f"Warning: Complex collision mesh ({phys_metrics['collision_complexity']:.2f} ratio). Consider simplifying."
                    )

        # Optimization metrics
        opt_metrics = stats['performance_metrics']['optimization']
        
        # UV efficiency check
        if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'uv'):
            uv_coords = mesh.visual.uv
            uv_area = np.sum(np.abs(np.cross(uv_coords[1:] - uv_coords[0], uv_coords[2:] - uv_coords[0]))) / 2
            opt_metrics['uv_efficiency'] = uv_area / (1.0 if uv_area == 0 else uv_area)
            
            if opt_metrics['uv_efficiency'] < 0.5:
                opt_metrics['validation'].append(
                    f"Warning: Poor UV space utilization ({opt_metrics['uv_efficiency']:.2f}). Consider repacking UVs."
                )

        # Draw call estimation
        unique_materials = len(set(mesh.visual.material.name for face in mesh.faces)) if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'material') else 1
        opt_metrics['draw_call_estimate'] = unique_materials
        
        if opt_metrics['draw_call_estimate'] > perf_thresholds['material_count']['error']:
            opt_metrics['validation'].append(
                f"Error: High number of draw calls ({opt_metrics['draw_call_estimate']}). Reduce material count."
            )
        elif opt_metrics['draw_call_estimate'] > perf_thresholds['material_count']['warning']:
            opt_metrics['validation'].append(
                f"Warning: Elevated draw calls ({opt_metrics['draw_call_estimate']}). Consider combining materials."
            )

        # Log comprehensive performance validation results
        logger.info("\n=== Performance Validation Results ===")
        for category, metrics in stats['performance_metrics'].items():
            logger.info(f"\n{category.upper()} Performance:")
            for key, value in metrics.items():
                if key != 'validation':
                    logger.info(f"- {key}: {value}")
            if metrics['validation']:
                for msg in metrics['validation']:
                    if 'Error' in msg:
                        logger.error(f"  {msg}")
                    else:
                        logger.warning(f"  {msg}")

        return stats
        
    except Exception as e:
        logger.error(f"Error analyzing model: {str(e)}")
        return None

def add_roblox_animations(armature, outfit_type):
    """Add Roblox-specific animations."""
    animations = {
        'clothes': {
            'idle': {
                'frames': 30,
                'poses': {
                    'UpperTorso': [(0, 'ROT', (0, 0, 0)), (15, 'ROT', (0, 5, 0)), (30, 'ROT', (0, 0, 0))],
                    'LowerTorso': [(0, 'ROT', (0, 0, 0)), (15, 'ROT', (0, -2, 0)), (30, 'ROT', (0, 0, 0))]
                }
            },
            'walk': {
                'frames': 24,
                'poses': {
                    'LeftUpperLeg': [(0, 'ROT', (30, 0, 0)), (12, 'ROT', (-30, 0, 0)), (24, 'ROT', (30, 0, 0))],
                    'RightUpperLeg': [(0, 'ROT', (-30, 0, 0)), (12, 'ROT', (30, 0, 0)), (24, 'ROT', (-30, 0, 0))]
                }
            }
        },
        'shoes': {
            'walk': {
                'frames': 24,
                'poses': {
                    'LeftFoot': [(0, 'ROT', (15, 0, 0)), (12, 'ROT', (-15, 0, 0)), (24, 'ROT', (15, 0, 0))],
                    'RightFoot': [(0, 'ROT', (-15, 0, 0)), (12, 'ROT', (15, 0, 0)), (24, 'ROT', (-15, 0, 0))]
                }
            }
        }
    }

def add_roblox_physics(obj, outfit_type):
    """Add Roblox-specific physics properties."""
    physics_props = {
        'clothes': {
            'mass': 1.0,
            'friction': 0.3,
            'elasticity': 0.5,
            'use_cloth_physics': True,
            'cloth_stiffness': 0.8
        },
        'hats': {
            'mass': 0.5,
            'friction': 0.7,
            'elasticity': 0.2,
            'use_rigid_body': True
        },
        'shoes': {
            'mass': 0.8,
            'friction': 0.9,
            'elasticity': 0.1,
            'use_rigid_body': True
        }
    }

def add_roblox_lod(obj, outfit_type):
    """Add Level of Detail for Roblox optimization."""
    lod_levels = {
        'clothes': [
            {'distance': 0, 'triangle_percent': 1.0},
            {'distance': 10, 'triangle_percent': 0.75},
            {'distance': 20, 'triangle_percent': 0.5}
        ],
        'hats': [
            {'distance': 0, 'triangle_percent': 1.0},
            {'distance': 15, 'triangle_percent': 0.6}
        ],
        'shoes': [
            {'distance': 0, 'triangle_percent': 1.0},
            {'distance': 12, 'triangle_percent': 0.7}
        ]
    }

def add_roblox_surfaces(obj, outfit_type):
    """Add Roblox-specific surface properties."""
    surface_props = {
        'clothes': {
            'surface_type': 'SmoothNoOutlines',
            'transparency': 0,
            'reflectance': 0.1
        },
        'hats': {
            'surface_type': 'Smooth',
            'transparency': 0,
            'reflectance': 0.2,
            'cast_shadow': True
        },
        'shoes': {
            'surface_type': 'Smooth',
            'transparency': 0,
            'reflectance': 0.15,
            'cast_shadow': True
        }
    }

def add_roblox_constraints(obj, outfit_type):
    """Add Roblox-specific constraints and attachments."""
    constraints = {
        'clothes': {
            'weld_parts': True,
            'allow_rotation': False,
            'preserve_position': True
        },
        'hats': {
            'attachment_type': 'Weld',
            'allow_rotation': True,
            'max_angle': 45
        },
        'shoes': {
            'attachment_type': 'Motor6D',
            'allow_rotation': True,
            'follow_animation': True
        }
    }

def create_3d_model(params, input_path, output_path):
    try:
        # Log input information
        logger.info(f"Full input path: {input_path}")
        logger.info(f"Original filename: {os.path.basename(input_path)}")
        
        # Extract parameters
        is_outfit = params.get('isOutfit', False)
        outfit_type = params.get('outfitType', None)
        
        # Initialize the Masterpiece SDK client
        client = Masterpiecex(
            bearer_token=os.getenv("MPX_SDK_BEARER_TOKEN")
        )
        logger.info("SDK initialized successfully")

        # Construct the URL for the uploaded image
        image_url = f"http://40.81.21.27/uploads/{os.path.basename(input_path)}"
        logger.info(f"Using image URL: {image_url}")

        # Start 3D conversion with Masterpiece (matching debug.py parameters)
        logger.info("Starting Masterpiece 2D to 3D conversion...")
        response = client.functions.imageto3d(
            image_url=image_url,
            seed=1
        )
        request_id = response.requestId
        logger.info(f"Conversion started! Request ID: {request_id}")

        # Monitor conversion status
        while True:
            status_response = client.status.retrieve(request_id)
            logger.info(f"Status: {status_response.status}")
            
            if hasattr(status_response, 'progress'):
                logger.info(f"Progress: {status_response.progress}%")

            if status_response.status == "complete":
                logger.info("Masterpiece conversion complete!")
                logger.info(f"Processing time: {status_response.processing_time_s}s")
                
                if hasattr(status_response, 'outputs'):
                    outputs = status_response.outputs
                    base_name = os.path.splitext(os.path.basename(input_path))[0]
                    timestamp = time.strftime("%Y%m%d%H%M%S")
                    
                    # Define output paths for all file types
                    output_files = {
                        'glb': f"{base_name}_{timestamp}.glb",
                        'fbx': f"{base_name}_{timestamp}.fbx",
                        'usdz': f"{base_name}_{timestamp}.usdz",
                        'thumbnail': f"{base_name}_{timestamp}_thumb.png"
                    }

                    # Download all available output files
                    downloaded_files = {}
                    output_dir = os.path.dirname(output_path)
                    
                    for file_type, filename in output_files.items():
                        if hasattr(outputs, file_type) and getattr(outputs, file_type):
                            url = getattr(outputs, file_type)
                            file_path = os.path.join(output_dir, filename)
                            logger.info(f"Downloading {file_type} file from: {url}")
                            
                            if download_file(url, file_path):
                                downloaded_files[file_type] = filename
                    
                    # After downloading all files, process FBX for Roblox if needed
                    if is_outfit and outfit_type and 'fbx' in downloaded_files:
                        fbx_path = os.path.join(output_dir, downloaded_files['fbx'])
                        logger.info(f"Processing downloaded FBX for Roblox {outfit_type} requirements")
                        processed_path = process_fbx_for_roblox(fbx_path, outfit_type)
                        
                        if processed_path:
                            # Add processed file to downloads
                            roblox_filename = f"{base_name}_{timestamp}_roblox.fbx"
                            shutil.move(processed_path, os.path.join(output_dir, roblox_filename))
                            downloaded_files['fbx_roblox'] = roblox_filename
                            
                            # Verify and log Roblox-specific metrics
                            logger.info("Verifying Roblox requirements and performance metrics...")
                            roblox_stats = verify_model_for_roblox(
                                os.path.join(output_dir, roblox_filename),
                                outfit_type
                            )
                            if roblox_stats:
                                stats_filename = f"{base_name}_{timestamp}_roblox_validation.json"
                                with open(os.path.join(output_dir, stats_filename), 'w') as f:
                                    json.dump(roblox_stats, f, indent=2)
                                downloaded_files['validation_stats'] = stats_filename

                    # Return paths of all downloaded files
                    return {
                        'success': True,
                        'files': downloaded_files,
                        'requestId': request_id
                    }
                break
            elif status_response.status == "failed":
                error_msg = status_response.error if hasattr(status_response, 'error') else "Unknown error"
                raise Exception(f"Conversion failed: {error_msg}")
                
            time.sleep(10)

    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Convert 2D image to 3D model')
    parser.add_argument('-i', '--input', required=True, help='Input image path')
    parser.add_argument('-o', '--output', required=True, help='Output GLB path')
    parser.add_argument('--is-outfit', action='store_true', help='Process as Roblox outfit')
    parser.add_argument('--outfit-type', choices=['clothes', 'hats', 'shoes'], help='Type of outfit')
    args = parser.parse_args()

    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found - {os.path.abspath(args.input)}")
        sys.exit(1)

    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    # Run conversion
    params = {
        'isOutfit': args.is_outfit,
        'outfitType': args.outfit_type
    }
    result = create_3d_model(params, args.input, args.output)
    
    if result['success']:
        print("Conversion completed successfully!")
        print("Output files:")
        for file_type, filename in result['files'].items():
            print(f"{file_type}: {filename}")
    else:
        print(f"Conversion failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main() 