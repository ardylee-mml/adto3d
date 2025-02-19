import os
import sys
import json
import requests
import time
from dotenv import load_dotenv
from mpx_genai_sdk import Masterpiecex
import argparse

# Load environment variables from specific path
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
load_dotenv(dotenv_path=env_path)

# Verification test (temporary)
print("\n=== ENVIRONMENT VERIFICATION ===")
print("MPX_SDK_BEARER_TOKEN exists:", bool(os.getenv("MPX_SDK_BEARER_TOKEN")))
print("===============================\n")

MPX_SDK_BEARER_TOKEN = os.getenv("MPX_SDK_BEARER_TOKEN")
if not MPX_SDK_BEARER_TOKEN:
    raise ValueError("MPX_SDK_BEARER_TOKEN environment variable not set")

ROBLOX_STYLE_CONFIG = {
    "output_format": "glb",
    "polygon_limit": 1000,
    "texture_size": 512,
    "style_preset": "low_poly",
    "shading": "toon",
    "scale_factor": 0.01  # Roblox world scale
}

def load_analysis(json_path):
    with open(json_path, 'r') as f:
        return json.load(f)

def convert_to_roblox_3d(image_path, output_path):
    print(f"Starting conversion for: {image_path}")
    
    try:
        # Correct initialization for 0.8.1
        client = Masterpiecex(bearer_token=os.getenv("MPX_SDK_BEARER_TOKEN"))
        
        # Modern SDK call
        with open(image_path, "rb") as image_file:
            conversion_job = client.functions.image_to_3d(
                files={"image": image_file},
                parameters={
                    "output_format": "glb",
                    "quality": "high",
                    "texture_resolution": 2048
                }
            )
        
        print(f"Job ID: {conversion_job.id}")
        
        # Modern status polling
        while True:
            status = client.query_job_status(conversion_job.id)
            print(f"Status: {status.state} - Progress: {status.progress}%")
            if status.complete:
                break
            if status.failed:
                raise Exception(f"Job failed: {status.error_message}")
            time.sleep(10)
            
        # Modern download method
        output_file = client.download_job_result(
            job_id=conversion_job.id,
            output_dir=os.path.dirname(output_path),
            filename=os.path.basename(output_path)
        )
        print(f"Model saved to: {output_file}")
        return True
        
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        raise e

def create_3d_model(analysis, image_path, output_path):
    return convert_to_roblox_3d(image_path, output_path)

def main():
    parser = argparse.ArgumentParser(description='Convert 2D image to 3D model')
    parser.add_argument('-i', '--input', required=True, help='Input image path')
    parser.add_argument('-o', '--output', required=True, help='Output GLB path')
    args = parser.parse_args()

    # Verify input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found - {os.path.abspath(args.input)}")
        sys.exit(1)

    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)

    # Run conversion (analysis parameter removed if unused)
    create_3d_model(None, args.input, args.output)

if __name__ == "__main__":
    main() 