from rembg import remove
from PIL import Image
import os

def test_background_removal():
    # Create test directories if they don't exist
    temp_dir = os.path.join(os.getcwd(), 'temp')
    uploads_dir = os.path.join(temp_dir, 'uploads')
    output_dir = os.path.join(temp_dir, 'output')
    
    for dir_path in [temp_dir, uploads_dir, output_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # Test image path - replace with your test image
    input_path = os.path.join(uploads_dir, 'test.png')  # Put a test image here
    output_path = os.path.join(output_dir, 'test_output.png')
    
    try:
        # Open the input image
        input_image = Image.open(input_path)
        
        # Remove background
        output_image = remove(input_image)
        
        # Save the result
        output_image.save(output_path)
        
        print(f"Success! Output saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_background_removal() 