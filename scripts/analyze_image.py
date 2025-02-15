import cv2
import numpy as np
import sys
import json
import traceback
from PIL import Image
import logging
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/mml_admin/2dto3d/logs/analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    try:
        import cv2
        import numpy
        from PIL import Image
        return True
    except ImportError as e:
        print(json.dumps({
            "error": f"Missing dependency: {str(e)}"
        }))
        return False

def analyze_image(image_path):
    try:
        logger.info(f"Starting image analysis for: {image_path}")
        
        # Verify image exists
        if not os.path.exists(image_path):
            raise Exception(f"Image file not found: {image_path}")
        
        # Load image with PIL first to verify it's valid
        logger.info("Attempting to open image with PIL")
        pil_image = Image.open(image_path)
        logger.info(f"Image size: {pil_image.size}, mode: {pil_image.mode}")
        
        # Load with OpenCV
        logger.info("Loading image with OpenCV")
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Failed to load image with OpenCV")
        
        height, width = img.shape[:2]
        logger.info(f"Image dimensions: {width}x{height}")
        
        # Color analysis
        logger.info("Performing color analysis")
        colors = cv2.mean(img)
        dominant_color = np.mean(img.reshape(-1, 3), axis=0)
        
        # Edge detection
        logger.info("Performing edge detection")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_count = cv2.countNonZero(edges)
        logger.info(f"Found {edge_count} edge pixels")
        
        # Shape analysis
        logger.info("Analyzing shape")
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        logger.info(f"Found {len(contours)} contours")
        
        analysis = {
            "image_properties": {
                "width": width,
                "height": height,
                "aspect_ratio": round(width/height, 2)
            },
            "color_analysis": {
                "average_rgb": [round(colors[2]), round(colors[1]), round(colors[0])],
                "dominant_rgb": [round(x) for x in dominant_color]
            },
            "complexity_analysis": {
                "edge_count": edge_count,
                "contour_count": len(contours)
            }
        }
        
        if contours:
            main_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            analysis["shape_analysis"] = {
                "type": "circular" if circularity > 0.8 else "rectangular" if circularity > 0.6 else "irregular",
                "circularity": round(circularity, 2),
                "area": round(area),
                "perimeter": round(perimeter)
            }
            logger.info(f"Shape analysis completed: {analysis['shape_analysis']['type']}")
        
        # Generate prompt based on analysis
        prompt = generate_prompt(analysis)
        analysis["generated_prompt"] = prompt
        
        logger.info("Analysis completed successfully")
        return json.dumps(analysis)

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc()
        })

def generate_prompt(analysis):
    """Generate a detailed prompt based on image analysis"""
    shape_type = analysis.get("shape_analysis", {}).get("type", "unknown")
    width = analysis["image_properties"]["width"]
    height = analysis["image_properties"]["height"]
    colors = analysis["color_analysis"]["dominant_rgb"]
    
    prompt = f"Create a Roblox-style 3D model with these specifications:\n"
    prompt += f"- Primary shape: {shape_type}\n"
    prompt += f"- Proportions: {width}x{height} (scaled appropriately)\n"
    prompt += f"- Main color: RGB({colors[0]}, {colors[1]}, {colors[2]})\n"
    prompt += f"- Complexity: {'high' if analysis['complexity_analysis']['edge_count'] > 1000 else 'medium' if analysis['complexity_analysis']['edge_count'] > 500 else 'low'}\n"
    
    logger.info(f"Generated prompt: {prompt}")
    return prompt

if __name__ == "__main__":
    try:
        logger.info("Starting image analysis script")
        if not check_dependencies():
            sys.exit(1)
        
        if len(sys.argv) > 1:
            result = analyze_image(sys.argv[1])
            print(result)
        else:
            logger.error("No input file provided")
            print(json.dumps({"error": "No input file provided"}))
    except Exception as e:
        logger.error(f"Script error: {str(e)}")
        logger.error(traceback.format_exc()) 