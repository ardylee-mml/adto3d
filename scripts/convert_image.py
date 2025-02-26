import os
import sys
import json
import time
import shutil
import requests
from mpx_genai_sdk import Masterpiecex
from dotenv import load_dotenv
from PIL import Image

def download_file(url, output_path):
    """
    Downloads a file from URL to the specified path with error handling and retries
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"Attempting to download {url} to {output_path}")  # Debug print
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Download file in chunks
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was created and has size > 0
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"Successfully downloaded {url}")  # Debug print
                return True
            else:
                raise Exception("Downloaded file is empty or missing")
            
        except requests.exceptions.RequestException as e:
            print(f"Download attempt {retry_count + 1} failed for {url}: {str(e)}", file=sys.stderr)
            retry_count += 1
            if retry_count == max_retries:
                raise Exception(f"Failed to download file after {max_retries} attempts: {str(e)}")
            time.sleep(2)  # Wait before retrying

def validate_image(image_path):
    """
    Validates image and returns detailed feedback about requirements
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            format = img.format
            file_size = os.path.getsize(image_path) / (1024 * 1024)  # Size in MB
            
            requirements_status = {
                "success": True,
                "current": {
                    "width": width,
                    "height": height,
                    "format": format,
                    "file_size_mb": round(file_size, 2)
                },
                "requirements": {
                    "min_resolution": "512x512",
                    "max_resolution": "4096x4096",
                    "formats": ["JPEG", "PNG"],
                    "max_file_size_mb": 10
                },
                "checks": {
                    "resolution": True,
                    "format": True,
                    "file_size": True
                },
                "message": "All requirements met"
            }
            
            # Check resolution
            if width < 512 or height < 512:
                requirements_status["success"] = False
                requirements_status["checks"]["resolution"] = False
                requirements_status["message"] = f"Image resolution ({width}x{height}) is too low. Minimum required: 512x512"
                return False, requirements_status
                
            elif width > 4096 or height > 4096:
                requirements_status["success"] = False
                requirements_status["checks"]["resolution"] = False
                requirements_status["message"] = f"Image resolution ({width}x{height}) is too high. Maximum allowed: 4096x4096"
                return False, requirements_status
            
            # Check format
            if format not in ['JPEG', 'PNG']:
                requirements_status["success"] = False
                requirements_status["checks"]["format"] = False
                requirements_status["message"] = f"Invalid format: {format}. Must be JPEG or PNG"
                return False, requirements_status
            
            # Check file size
            if file_size > 10:
                requirements_status["success"] = False
                requirements_status["checks"]["file_size"] = False
                requirements_status["message"] = f"File size ({round(file_size, 2)}MB) exceeds 10MB limit"
                return False, requirements_status
            
            # Print basic validation info
            print(f"Image validation:")
            print(f"Format: {format}")
            print(f"Size: {width}x{height}")
            print(f"File size: {file_size:.2f}MB")
                
            return True, requirements_status
            
    except Exception as e:
        return False, {
            "success": False,
            "message": f"Error checking image: {str(e)}",
            "error": str(e)
        }

def rename_downloaded_file(src_path, dst_path):
    try:
        if os.path.exists(src_path):
            os.rename(src_path, dst_path)
            return True
        return False
    except Exception as e:
        print(f"Error renaming file {src_path}: {str(e)}", file=sys.stderr)
        return False

def process_outfit_fbx(fbx_path, outfit_type):
    """
    Process an existing FBX file from Masterpiece to meet Roblox outfit requirements.
    """
    try:
        import bpy
        
        print(f"Processing Masterpiece FBX for Roblox {outfit_type}")
        print(f"Input FBX: {fbx_path}")
        
        # Clear existing scene
        bpy.ops.wm.read_factory_settings(use_empty=True)
        
        # Load the Masterpiece-converted FBX
        print("Loading Masterpiece FBX...")
        bpy.ops.import_scene.fbx(filepath=fbx_path)
        
        # Get all mesh objects from the scene
        mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
        if not mesh_objects:
            raise Exception("No mesh objects found in the FBX file")
            
        # Use the first mesh object
        masterpiece_mesh = mesh_objects[0]
        print(f"Using mesh: {masterpiece_mesh.name}")
        
        # Make sure the mesh is selected and active
        bpy.ops.object.select_all(action='DESELECT')
        masterpiece_mesh.select_set(True)
        bpy.context.view_layer.objects.active = masterpiece_mesh
        
        if outfit_type == 'clothes':
            # Load R15 template
            template_path = os.path.join(os.getcwd(), 'templates', 'r15_armature.fbx')
            print(f"Loading R15 template: {template_path}")
            
            # Import the armature template
            bpy.ops.import_scene.fbx(filepath=template_path)
            
            # Find the armature object
            armature = next((obj for obj in bpy.context.scene.objects if obj.type == 'ARMATURE'), None)
            if not armature:
                raise Exception("R15 armature not found in template")
                
            print(f"Found armature: {armature.name}")
            
            # Parent mesh to armature with automatic weights
            masterpiece_mesh.parent = armature
            mod = masterpiece_mesh.modifiers.new(name="Armature", type='ARMATURE')
            if mod:  # Check if modifier was created successfully
                mod.object = armature
                print("Added armature modifier")
            else:
                print("Warning: Could not create armature modifier")
            
        elif outfit_type == 'hats':
            # Add attachment point
            bpy.ops.object.empty_add(type='PLAIN_AXES')
            attachment = bpy.context.active_object
            attachment.name = "HatAttachment"
            attachment.parent = masterpiece_mesh
            print("Added hat attachment point")
            
        elif outfit_type == 'shoes':
            # Add foot attachments
            for side in ['Left', 'Right']:
                bpy.ops.object.empty_add(type='PLAIN_AXES')
                attachment = bpy.context.active_object
                attachment.name = f"{side}FootAttachment"
                attachment.parent = masterpiece_mesh
                attachment.location = (0.1 if side == 'Right' else -0.1, 0, 0)
            print("Added foot attachment points")
        
        # Export the processed version
        processed_path = fbx_path.replace('.fbx', '_processed.fbx')
        print(f"Exporting processed FBX to: {processed_path}")
        
        # Make sure the mesh is selected for export
        bpy.ops.object.select_all(action='SELECT')
        
        bpy.ops.export_scene.fbx(
            filepath=processed_path,
            use_selection=True,
            mesh_smooth_type='EDGE',
            add_leaf_bones=False,
            bake_anim=False,
            embed_textures=True,
            path_mode='ABSOLUTE',
            use_mesh_modifiers=True,
            use_triangles=True
        )
        
        print(f"Successfully exported processed FBX")
        return processed_path
        
    except Exception as e:
        print(f"Error processing outfit: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return original FBX path if processing fails
        return fbx_path

def convert_image(image_path, file_name, is_outfit='false', outfit_type=''):
    try:
        # Validate image with detailed requirements check
        is_valid, validation_result = validate_image(image_path)
        if not is_valid:
            print(json.dumps(validation_result))
            sys.exit(1)
            
        # Debug logging
        print(f"Debug: Starting conversion with image_path={image_path}, file_name={file_name}", file=sys.stderr)
        print(f"Debug: Current directory={os.getcwd()}", file=sys.stderr)
        
        # Load environment variables with absolute path
        env_path = os.path.join(os.getcwd(), '.env.local')
        print(f"Debug: Loading .env from: {env_path}", file=sys.stderr)
        load_dotenv(env_path)
        
        token = os.getenv("MPX_SDK_BEARER_TOKEN")
        if not token:
            raise Exception("MPX_SDK_BEARER_TOKEN not found in environment")
        print(f"Debug: Token available: {bool(token)}", file=sys.stderr)

        # Initialize client
        client = Masterpiecex(
            bearer_token=token
        )

        # Test connection first
        print("Testing connection...")
        connection_test = client.connection_test.retrieve()
        print("Connection test successful:", connection_test)
        
        # Create output directory
        output_dir = os.getcwd() + "/temp/output"
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nOutput directory: {output_dir}")
        
        # Create public URL using the server's IP address
        image_filename = os.path.basename(image_path)
        public_url = f"http://40.81.21.27:3000/api/files/uploads/{image_filename}"
        
        print(f"\nPublic Image URL: {public_url}")
        
        print("\nStarting 3D conversion...")
        response = client.functions.imageto3d(
            image_url=public_url,
            texture_size=2048
        )
        print(f"Conversion started! Request ID: {response.requestId}")
        
        # Monitor status with more detailed error reporting
        start_time = time.time()
        while True:
            status_response = client.status.retrieve(response.requestId)
            print(f"Status: {status_response.status}")
            print(f"Full status response: {status_response.__dict__}")
            
            # Send structured progress updates
            progress_info = {
                "type": "progress",
                "stage": status_response.status,
                "progress": getattr(status_response, 'progress', 0),
                "message": f"Converting: {getattr(status_response, 'progress', 0)}%",
                "details": getattr(status_response, 'error', None)
            }
            print(json.dumps(progress_info))
            
            if status_response.status == "failed":
                error_details = getattr(status_response, 'error', None)
                error_message = {
                    "success": False,
                    "error": "Conversion failed",
                    "details": error_details if error_details else "Unknown error",
                    "full_response": status_response.__dict__
                }
                print(json.dumps(error_message))
                sys.exit(1)

            if status_response.status == "complete":
                print("Conversion complete!")
                
                # Get output URLs from the API response
                outputs = status_response.outputs
                print(f"Debug: Output URLs received: {outputs}")  # Debug print
                
                # Create directory for downloaded files
                download_dir = os.path.join(os.getcwd(), 'temp', 'output', file_name)
                os.makedirs(download_dir, exist_ok=True)
                
                try:
                    # Define final paths
                    final_paths = {
                        'glb': os.path.join(download_dir, f"{file_name}.glb"),
                        'fbx': os.path.join(download_dir, f"{file_name}.fbx"),
                        'usdz': os.path.join(download_dir, f"{file_name}.usdz"),
                        'thumbnail': os.path.join(download_dir, f"{file_name}_preview.png")
                    }
                    
                    # Download all files from Google Cloud Storage
                    print("Downloading files from storage...")
                    
                    # Access URLs as attributes of the Outputs object
                    download_urls = {
                        'glb': getattr(outputs, 'glb'),
                        'fbx': getattr(outputs, 'fbx'),
                        'usdz': getattr(outputs, 'usdz'),
                        'thumbnail': getattr(outputs, 'thumbnail')
                    }
                    
                    # Download each file
                    for file_type, url in download_urls.items():
                        print(f"Downloading {file_type} from {url}")  # Debug print
                        if not download_file(url, final_paths[file_type]):
                            raise Exception(f"Failed to download {file_type} file")
                    
                    # Verify all files were downloaded
                    for file_type, file_path in final_paths.items():
                        if not os.path.exists(file_path):
                            raise Exception(f"Failed to download {file_type} file: {file_path}")
                        else:
                            print(f"Successfully downloaded {file_type} to {file_path}")  # Debug print
                    
                    if is_outfit == 'true' and outfit_type:
                        # Process the FBX file for the specific outfit type
                        fbx_path = os.path.join(download_dir, f"{file_name}.fbx")
                        processed_fbx_path = process_outfit_fbx(fbx_path, outfit_type)
                        
                        # Update the FBX path in the results
                        result = {
                            "success": True,
                            "outputs": {
                                "glb": f"/api/files/{file_name}/{file_name}.glb",
                                "fbx": f"/api/files/{file_name}/{file_name}_processed.fbx",
                                "usdz": f"/api/files/{file_name}/{file_name}.usdz",
                                "thumbnail": f"/api/files/{file_name}/{file_name}_preview.png"
                            },
                            "message": "Conversion completed successfully"
                        }
                        print(json.dumps(result))
                        sys.exit(0)
                    
                    # Return the local URLs for the files
                    result = {
                        "success": True,
                        "outputs": {
                            "glb": f"/api/files/{file_name}/{file_name}.glb",
                            "fbx": f"/api/files/{file_name}/{file_name}.fbx",
                            "usdz": f"/api/files/{file_name}/{file_name}.usdz",
                            "thumbnail": f"/api/files/{file_name}/{file_name}_preview.png"
                        },
                        "message": "Conversion completed successfully"
                    }
                    print(json.dumps(result))
                    sys.exit(0)
                    
                except Exception as e:
                    print(f"Debug: Download error details: {str(e)}", file=sys.stderr)  # Debug print
                    error_result = {
                        "success": False,
                        "error": "Failed to download converted files",
                        "details": str(e)
                    }
                    print(json.dumps(error_result))
                    sys.exit(1)

            # Add timeout check
            if time.time() - start_time > 300:  # 5 minutes timeout
                raise Exception("Conversion timeout")
                
            time.sleep(10)
            
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "details": getattr(e, 'details', str(e))
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "error": "Invalid arguments"
        }))
        sys.exit(1)
    
    is_outfit = sys.argv[3] if len(sys.argv) > 3 else 'false'
    outfit_type = sys.argv[4] if len(sys.argv) > 4 else ''
    
    convert_image(sys.argv[1], sys.argv[2], is_outfit, outfit_type) 