import cv2
import numpy as np
import os

print("OpenCV version:", cv2.__version__)
print("Working directory:", os.getcwd())

# Create a simple test image
img = np.zeros((100, 100, 3), dtype=np.uint8)
cv2.circle(img, (50, 50), 30, (0, 255, 0), -1)

# Try to save it
test_output = '/home/mml_admin/2dto3d/logs/test_opencv.png'
try:
    cv2.imwrite(test_output, img)
    print(f"Successfully wrote test image to {test_output}")
except Exception as e:
    print(f"Error writing test image: {e}") 