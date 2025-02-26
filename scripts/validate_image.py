import os
import sys
import json
from PIL import Image

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
                "message": "Image meets all requirements"
            }
            
            # Check resolution
            if width < 512 or height < 512:
                requirements_status["success"] = False
                requirements_status["checks"]["resolution"] = False
                requirements_status["message"] = f"Image resolution ({width}x{height}) is too low. Minimum required: 512x512"
                return requirements_status
                
            if width > 4096 or height > 4096:
                requirements_status["success"] = False
                requirements_status["checks"]["resolution"] = False
                requirements_status["message"] = f"Image resolution ({width}x{height}) is too high. Maximum allowed: 4096x4096"
                return requirements_status
            
            # Check format
            if format not in ['JPEG', 'PNG']:
                requirements_status["success"] = False
                requirements_status["checks"]["format"] = False
                requirements_status["message"] = f"Invalid format: {format}. Must be JPEG or PNG"
                return requirements_status
            
            # Check file size
            if file_size > 10:
                requirements_status["success"] = False
                requirements_status["checks"]["file_size"] = False
                requirements_status["message"] = f"File size ({round(file_size, 2)}MB) exceeds 10MB limit"
                return requirements_status
                
            return requirements_status
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Error checking image: {str(e)}",
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({
            "success": False,
            "error": "Invalid arguments"
        }))
        sys.exit(1)
    
    result = validate_image(sys.argv[1])
    print(json.dumps(result))
    sys.exit(0 if result["success"] else 1) 