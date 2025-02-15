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
    """Analyze image using OpenCV to determine object characteristics"""
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise Exception("Could not read image")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Get contours
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        raise Exception("No contours found in image")
    
    # Get the largest contour
    main_contour = max(contours, key=cv2.contourArea)
    
    # Calculate basic properties
    area = cv2.contourArea(main_contour)
    perimeter = cv2.arcLength(main_contour, True)
    x, y, w, h = cv2.boundingRect(main_contour)
    
    # Calculate circularity
    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
    
    # Determine shape type
    shape_type = "cylindrical" if 0.6 < h/w < 1.8 and circularity > 0.6 else "irregular"
    
    # Calculate average color
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [main_contour], -1, (255), -1)
    average_color = cv2.mean(img, mask=mask)[:3]
    
    # Analyze symmetry
    symmetry = "symmetric" if analyze_symmetry(gray, main_contour) else "asymmetric"
    
    analysis = {
        "dimensions": {
            "width": w,
            "height": h,
            "aspect_ratio": h/w
        },
        "complexity": {
            "edge_count": len(main_contour),
            "contour_count": len(contours)
        },
        "color": {
            "average_rgb": [int(c) for c in average_color]
        },
        "shape": {
            "type": shape_type,
            "circularity": circularity,
            "symmetry": symmetry
        }
    }
    
    # Generate prompt based on analysis
    prompt = generate_3d_prompt(analysis)
    analysis["generated_prompt"] = prompt
    
    return analysis

def analyze_symmetry(gray_img, contour):
    """Analyze if the shape is roughly symmetrical"""
    x, y, w, h = cv2.boundingRect(contour)
    roi = gray_img[y:y+h, x:x+w]
    
    # Compare left and right halves
    mid = w//2
    left = roi[:, :mid]
    right = cv2.flip(roi[:, -mid:], 1)
    
    if left.shape == right.shape:
        diff = cv2.absdiff(left, right)
        symmetry_score = 1 - (np.sum(diff) / (255 * diff.size))
        return symmetry_score > 0.8
    return False

def generate_3d_prompt(analysis):
    """Generate a prompt for 3D model creation based on analysis"""
    shape_type = analysis["shape"]["type"]
    height = analysis["dimensions"]["height"]
    width = analysis["dimensions"]["width"]
    symmetry = analysis["shape"]["symmetry"]
    
    base_prompt = f"Create a {shape_type} 3D model with "
    
    if shape_type == "cylindrical":
        prompt = f"{base_prompt}height {height} units and diameter {width} units. "
    else:
        prompt = f"{base_prompt}height {height} units and width {width} units. "
    
    prompt += f"The object is {symmetry}. "
    
    if analysis["shape"]["circularity"] > 0.8:
        prompt += "The cross-section should be circular. "
    
    return prompt.strip()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_image.py <image_path>")
        sys.exit(1)
        
    try:
        analysis = analyze_image(sys.argv[1])
        print(json.dumps(analysis))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1) 