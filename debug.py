# Create debug.py
import os
import shutil
import requests  # Add back for testing URL
from mpx_genai_sdk import Masterpiecex
from dotenv import load_dotenv
import time

load_dotenv('.env.local')

# Initialize with API key
client = Masterpiecex(
    bearer_token=os.getenv("MPX_SDK_BEARER_TOKEN")
)

# Print SDK configuration
print("SDK Version:", client.__version__ if hasattr(client, '__version__') else "Unknown")
print("API Base URL:", client.base_url if hasattr(client, 'base_url') else "Unknown")
print("Available Functions:", dir(client.functions))

try:
    print("Testing connection...")
    connection_test = client.connection_test.retrieve()
    print("Connection test successful:", connection_test)
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "temp", "output")
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")
    
    print("\nStarting 3D conversion...")
    response = client.functions.imageto3d(
        image_url=test_url,
        texture_size=1024,
        seed=1
    )
    print(f"Conversion started! Request ID: {response.requestId}")
    
    # Monitor status with more detailed error reporting
    while True:
        status_response = client.status.retrieve(response.requestId)
        print(f"\nStatus: {status_response.status}")
        
        if hasattr(status_response, 'progress'):
            print(f"Progress: {status_response.progress}%")
            
        try:
            raw_data = status_response.model_dump()
            print("Raw status data:", raw_data)
        except:
            pass
        
        if status_response.status == "complete":
            print("Conversion complete!")
            print(f"Processing time: {status_response.processing_time_s}s")
            
            if hasattr(status_response, 'outputs'):
                outputs = status_response.outputs
                print("\nOutput Files:")
                print(f"GLB: {outputs.glb}")
                print(f"FBX: {outputs.fbx}")
                print(f"USDZ: {outputs.usdz}")
                print(f"Thumbnail: {outputs.thumbnail}")
                
                # Download all output files
                output_files = {
                    'glb': outputs.glb,
                    'fbx': outputs.fbx,
                    'usdz': outputs.usdz,
                    'thumbnail': outputs.thumbnail
                }
                
                for file_type, url in output_files.items():
                    if url:
                        output_path = os.path.join(output_dir, f"output.{file_type}")
                        print(f"\nDownloading {file_type.upper()} file...")
                        try:
                            response = requests.get(url)
                            if response.status_code == 200:
                                with open(output_path, 'wb') as f:
                                    f.write(response.content)
                                print(f"{file_type.upper()} file saved as: {output_path}")
                            else:
                                print(f"Failed to download {file_type.upper()} file: {response.status_code}")
                        except Exception as download_error:
                            print(f"Error downloading {file_type.upper()} file: {str(download_error)}")
                
                # List files in output directory
                print("\nFiles in output directory:")
                for file in os.listdir(output_dir):
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path)
                    print(f"- {file} ({file_size} bytes)")
            break
        elif status_response.status == "failed":
            print("Conversion failed!")
            if hasattr(status_response, 'error'):
                print(f"Error: {status_response.error}")
            break
            
        time.sleep(10)
        
except Exception as e:
    print("Error:", str(e))
    if hasattr(e, 'response'):
        print("Response:", e.response.text if hasattr(e.response, 'text') else e.response)