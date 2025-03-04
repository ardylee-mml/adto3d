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
    """Process downloaded FBX file according to Roblox requirements using Blender."""
    try:
        logger.info(f"Starting Roblox FBX processing for {outfit_type}")
        logger.info(f"Source FBX: {fbx_path}")
        
        # Prepare output path in the same directory
        output_dir = os.path.dirname(fbx_path)
        processed_path = os.path.join(output_dir, os.path.basename(fbx_path).replace('.fbx', '_roblox.fbx'))
        logger.info(f"Target FBX: {processed_path}")
        
        # Call Blender in headless mode to process the FBX
        logger.info("Launching Blender for FBX processing")
        blender_script = os.path.join(os.path.dirname(__file__), 'process_fbx.py')
        cmd = [
            'blender',
            '--background',  # Run in headless mode
            '--python', blender_script,
            '--',  # Arguments after this are passed to the script
            fbx_path,
            processed_path,
            outfit_type
        ]
        
        # Run Blender process
        logger.info("Executing Blender process")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse the JSON output from the script
        try:
            # Get the last non-empty line containing JSON output
            output_lines = [line for line in result.stdout.split('\n') if line.strip()]
            if not output_lines:
                raise ValueError("No output from Blender process")
            
            output = json.loads(output_lines[-1])
            if not output['success']:
                raise RuntimeError(output.get('error', 'Unknown error in FBX processing'))
            
            # Process and save comprehensive stats
            if 'stats' in output:
                stats = output['stats']
                
                # Save detailed stats
                stats_path = processed_path.replace('.fbx', '_stats.json')
                with open(stats_path, 'w') as f:
                    json.dump(stats, f, indent=2)
                logger.info(f"Saved comprehensive validation stats to {stats_path}")
                
                # Log important metrics
                logger.info("=== Processing Summary ===")
                logger.info(f"Validation Status: {stats['processing_summary']['validation_status']}")
                logger.info(f"Geometry Changes:")
                logger.info(f"  - Vertices: {stats['processing_summary']['geometry_change']['vertices_delta']:+d}")
                logger.info(f"  - Triangles: {stats['processing_summary']['geometry_change']['triangles_delta']:+d}")
                logger.info(f"Applied Modifications: {', '.join(stats['processing_summary']['modifications_applied'])}")
                
                # Log any warnings or errors
                if stats['roblox_validation']['warnings']:
                    logger.warning("Validation Warnings:")
                    for warning in stats['roblox_validation']['warnings']:
                        logger.warning(f"  - {warning}")
                
                if stats['roblox_validation']['errors']:
                    logger.error("Validation Errors:")
                    for error in stats['roblox_validation']['errors']:
                        logger.error(f"  - {error}")
            
            logger.info("FBX processing completed successfully")
            return processed_path
            
        except json.JSONDecodeError:
            logger.error("Failed to parse Blender output")
            logger.error(f"Raw output: {result.stdout}")
            return fbx_path
            
    except subprocess.CalledProcessError as e:
        logger.error("Blender process failed")
        logger.error(f"Exit code: {e.returncode}")
        logger.error(f"Error output: {e.stderr}")
        return fbx_path
    except Exception as e:
        logger.error(f"Unexpected error in FBX processing: {str(e)}")
        return fbx_path

def verify_model_for_roblox(mesh_path, outfit_type):
    """Verify and log model statistics for Roblox requirements using Blender."""
    try:
        logger.info("Analyzing FBX file using Blender...")
        
        # Construct command to run Blender in headless mode
        cmd = [
            'blender',
            '--background',
            '--python-expr',
            '''
import bpy
import json

def get_mesh_stats():
    stats = {
        'vertices': 0,
        'faces': 0,
        'edges': 0,
        'materials': 0,
        'uvs': 0,
        'vertex_groups': 0,
        'armature': None
    }
    
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            mesh = obj.data
            stats['vertices'] += len(mesh.vertices)
            stats['faces'] += len(mesh.polygons)
            stats['edges'] += len(mesh.edges)
            stats['materials'] += len(obj.material_slots)
            stats['uvs'] += len(mesh.uv_layers)
            stats['vertex_groups'] += len(obj.vertex_groups)
        elif obj.type == 'ARMATURE':
            stats['armature'] = {
                'bones': len(obj.data.bones),
                'bone_names': [bone.name for bone in obj.data.bones]
            }
    
    return stats

def get_dimensions():
    dims = {'x': 0, 'y': 0, 'z': 0}
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            dims['x'] = max(dims['x'], abs(obj.dimensions.x))
            dims['y'] = max(dims['y'], abs(obj.dimensions.y))
            dims['z'] = max(dims['z'], abs(obj.dimensions.z))
    return dims

# Clear existing scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# Import FBX
bpy.ops.import_scene.fbx(filepath="%s")

# Get statistics
stats = get_mesh_stats()
dims = get_dimensions()

# Calculate additional metrics
total_area = sum(p.area for obj in bpy.data.objects 
                if obj.type == 'MESH' 
                for p in obj.data.polygons)

result = {
    'geometry': {
        'vertices': stats['vertices'],
        'triangles': stats['faces'],
        'edges': stats['edges']
    },
    'materials': {
        'count': stats['materials'],
        'uv_layers': stats['uvs']
    },
    'rigging': {
        'vertex_groups': stats['vertex_groups'],
        'armature': stats['armature']
    },
    'dimensions': dims,
    'metrics': {
        'vertex_density': stats['vertices'] / total_area if total_area > 0 else 0,
        'triangle_density': stats['faces'] / total_area if total_area > 0 else 0,
        'edge_vertex_ratio': stats['edges'] / stats['vertices'] if stats['vertices'] > 0 else 0
    }
}

print("STATS_START")
print(json.dumps(result))
print("STATS_END")
''' % mesh_path
        ]
        
        # Run Blender process
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the output to get the statistics
        output = result.stdout
        start_idx = output.find("STATS_START") + len("STATS_START")
        end_idx = output.find("STATS_END")
        
        if start_idx == -1 or end_idx == -1:
            raise ValueError("Could not find statistics in Blender output")
            
        stats_json = output[start_idx:end_idx].strip()
        stats = json.loads(stats_json)
        
        # Add validation results
        config = ROBLOX_CONFIG.get(outfit_type, {})
        validation = {
            'warnings': [],
            'errors': []
        }
        
        # Check triangle count
        max_triangles = config.get('max_triangles', 8000)
        if stats['geometry']['triangles'] > max_triangles:
            validation['errors'].append(
                f"Triangle count ({stats['geometry']['triangles']}) exceeds limit ({max_triangles})"
            )
            
        # Check dimensions
        if 'size_limits' in config:
            for axis, limit in config['size_limits'].items():
                if stats['dimensions'][axis] > limit:
                    validation['warnings'].append(
                        f"{axis.upper()} dimension ({stats['dimensions'][axis]:.2f}) exceeds recommended limit ({limit})"
                    )
                    
        # Check rigging requirements
        if config.get('needs_rigging', False):
            if not stats['rigging']['armature']:
                validation['errors'].append("Missing required armature")
            else:
                required_bones = config.get('bones', [])
                missing_bones = [bone for bone in required_bones 
                               if bone not in stats['rigging']['armature']['bone_names']]
                if missing_bones:
                    validation['errors'].append(f"Missing required bones: {', '.join(missing_bones)}")
                    
        # Check UV maps
        if stats['materials']['uv_layers'] == 0:
            validation['errors'].append("No UV maps found")
            
        stats['validation'] = validation
        return stats
                
    except Exception as e:
        logger.error(f"Error analyzing model: {str(e)}")
        return None

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

def create_3d_model(params, input_path, output_path):
    try:
        # Log input information
        logger.info("=== Starting 3D Model Creation ===")
        logger.info(f"Input parameters: {json.dumps(params, indent=2)}")
        logger.info(f"Full input path: {input_path}")
        logger.info(f"Output path: {output_path}")
        
        # Extract parameters
        is_outfit = params.get('isOutfit', False)
        outfit_type = params.get('outfitType', None)
        
        logger.info(f"Is outfit: {is_outfit}")
        logger.info(f"Outfit type: {outfit_type}")
        
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
                        logger.info("=== Starting Roblox FBX Processing ===")
                        fbx_path = os.path.join(output_dir, downloaded_files['fbx'])
                        logger.info(f"Original FBX path: {fbx_path}")
                        logger.info(f"Processing for outfit type: {outfit_type}")
                        
                        if not os.path.exists(fbx_path):
                            logger.error(f"Original FBX file not found at: {fbx_path}")
                            raise FileNotFoundError(f"FBX file not found: {fbx_path}")
                        
                        processed_path = process_fbx_for_roblox(fbx_path, outfit_type)
                        logger.info(f"Processed FBX path: {processed_path}")
                        
                        if processed_path and os.path.exists(processed_path):
                            # Add processed file to downloads
                            roblox_filename = f"{base_name}_{timestamp}_roblox.fbx"
                            target_path = os.path.join(output_dir, roblox_filename)
                            logger.info(f"Moving processed file to: {target_path}")
                            shutil.move(processed_path, target_path)
                            downloaded_files['fbx_roblox'] = roblox_filename
                            logger.info(f"Successfully added Roblox FBX: {roblox_filename}")
                            
                            # Verify and log Roblox-specific metrics
                            logger.info("=== Starting Roblox Validation ===")
                            roblox_stats = verify_model_for_roblox(target_path, outfit_type)
                            if roblox_stats:
                                stats_filename = f"{base_name}_{timestamp}_roblox_validation.json"
                                stats_path = os.path.join(output_dir, stats_filename)
                                logger.info(f"Writing validation stats to: {stats_path}")
                                with open(stats_path, 'w') as f:
                                    json.dump(roblox_stats, f, indent=2)
                                downloaded_files['validation_stats'] = stats_filename
                                logger.info("Validation stats saved successfully")
                        else:
                            logger.error("FBX processing failed - no processed file generated")
                    else:
                        logger.info("Skipping Roblox FBX processing - not an outfit or no FBX file available")
                        if not is_outfit:
                            logger.info("Reason: Not an outfit")
                        elif not outfit_type:
                            logger.info("Reason: No outfit type specified")
                        elif 'fbx' not in downloaded_files:
                            logger.info("Reason: No FBX file in downloaded files")

                    logger.info("=== Conversion Summary ===")
                    logger.info(f"Downloaded files: {json.dumps(downloaded_files, indent=2)}")
                    
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
        logger.error("Stack trace:", exc_info=True)
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