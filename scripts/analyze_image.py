import cv2
import numpy as np
import sys
import json
import traceback
from PIL import Image

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
        # Verify image exists and is readable
        if not Image.open(image_path):
            raise Exception("Cannot open image file")

        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise Exception("Failed to load image with OpenCV")

        # Basic image properties
        height, width = img.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Color analysis
        colors = cv2.mean(img)
        
        # Detailed analysis
        analysis = {
            "dimensions": {
                "width": width,
                "height": height,
                "aspect_ratio": round(width/height, 2)
            },
            "complexity": {
                "edge_count": len(cv2.findNonZero(edges)),
                "contour_count": len(contours)
            },
            "color": {
                "average_rgb": [round(colors[2]), round(colors[1]), round(colors[0])]
            }
        }
        
        # Shape analysis
        if contours:
            main_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(main_contour)
            
            # Calculate shape properties
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            analysis["shape"] = {
                "type": "circular" if circularity > 0.8 else "rectangular" if circularity > 0.6 else "irregular",
                "circularity": round(circularity, 2),
                "symmetry": "symmetric" if abs(w/h - 1) < 0.2 else "asymmetric"
            }
        
        return json.dumps(analysis)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "traceback": traceback.format_exc()
        })

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    if len(sys.argv) > 1:
        result = analyze_image(sys.argv[1])
        print(result)
    else:
        print(json.dumps({"error": "No input file provided"})) 