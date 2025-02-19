import os
import sys
import json
import time
import shutil
import requests
from mpx_genai_sdk import Masterpiecex
from dotenv import load_dotenv

def download_file(url, output_path):
    response = requests.get(url, stream=True)
    if response.ok:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True
    return False

def convert_image(image_path, file_name):
    try:
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
        
        # Construct URL
        image_url = f"http://40.81.21.27:3001/api/files/{os.path.basename(image_path)}"
        print(f"\nImage URL: {image_url}")
        
        print("\nStarting 3D conversion...")
        response = client.functions.imageto3d(
            image_url=image_url,
            texture_size=1024,
            seed=1
        )
        print(f"Conversion started! Request ID: {response.requestId}")
        
        # Monitor status
        while True:
            status_response = client.status.retrieve(response.requestId)
            print(f"Status: {status_response.status}")
            
            # Send structured progress updates
            progress_info = {
                "type": "progress",
                "stage": status_response.status,
                "progress": getattr(status_response, 'progress', 0),
                "message": f"Converting: {getattr(status_response, 'progress', 0)}%"
            }
            print(json.dumps(progress_info))
            
            if status_response.status == "complete":
                print("Conversion complete!")
                
                # Get output URLs
                outputs = status_response.outputs
                
                # Create directory for downloaded files
                download_dir = os.path.join(os.getcwd(), 'temp', 'output', file_name)
                os.makedirs(download_dir, exist_ok=True)
                
                # Download and save files with custom names
                downloaded_files = {
                    "success": True,
                    "outputs": {
                        "glb": f"/api/files/{file_name}/{file_name}.glb",
                        "fbx": f"/api/files/{file_name}/{file_name}.fbx",
                        "usdz": f"/api/files/{file_name}/{file_name}.usdz",
                        "thumbnail": f"/api/files/{file_name}/{file_name}_preview.png"
                    }
                }
                
                # Download each file
                try:
                    download_file(outputs.glb, os.path.join(download_dir, f"{file_name}.glb"))
                    download_file(outputs.fbx, os.path.join(download_dir, f"{file_name}.fbx"))
                    download_file(outputs.usdz, os.path.join(download_dir, f"{file_name}.usdz"))
                    download_file(outputs.thumbnail, os.path.join(download_dir, f"{file_name}_preview.png"))
                    
                    print(json.dumps(downloaded_files))
                    sys.exit(0)
                except Exception as e:
                    raise Exception(f"Failed to download files: {str(e)}")

            elif status_response.status == "failed":
                raise Exception("Conversion failed")
                
            time.sleep(10)
            
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(f"Debug: Error occurred: {str(e)}", file=sys.stderr)
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({
            "success": False,
            "error": "Invalid arguments"
        }))
        sys.exit(1)
    
    print(f"Debug: Script started with args: {sys.argv}", file=sys.stderr)
    convert_image(sys.argv[1], sys.argv[2]) 