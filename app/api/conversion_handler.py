import os
from masterpiecex import Masterpiecex

def handle_conversion(image_path):
    try:
        if not os.path.exists(image_path):
            return {"error": "Image file not found"}, 404
            
        client = Masterpiecex(bearer_token=os.getenv("MPX_SDK_BEARER_TOKEN"))
        
        with open(image_path, "rb") as image_file:
            conversion_job = client.functions.imageto3d(
                image=image_file,
                output_format="glb",  # or "obj" for different formats
                quality="high",
                texture_resolution=2048
            )
            
        return {
            "job_id": conversion_job.id,
            "status": conversion_job.status,
            "estimated_completion": conversion_job.eta
        }
        
    except Exception as e:
        return {"error": f"Conversion failed: {str(e)}"}, 500 