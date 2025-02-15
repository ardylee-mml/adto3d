from rembg import remove
from PIL import Image
import os
import subprocess

def test_full_workflow():
    # Setup directories
    temp_dir = os.path.join(os.getcwd(), 'temp')
    uploads_dir = os.path.join(temp_dir, 'uploads')
    output_dir = os.path.join(temp_dir, 'output')
    
    for dir_path in [temp_dir, uploads_dir, output_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    # Test paths
    input_path = os.path.join(uploads_dir, 'test.png')
    bg_removed_path = os.path.join(output_dir, 'bg_removed.png')
    final_3d_path = os.path.join(output_dir, 'final.fbx')
    
    try:
        # Step 1: Remove background
        print("Step 1: Removing background...")
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(bg_removed_path)
        print("✓ Background removal successful")
        
        # Step 2: Convert to 3D
        print("\nStep 2: Converting to 3D...")
        blender_script = os.path.join('scripts', 'convert_to_3d.py')
        blender_path = os.getenv('BLENDER_PATH', '/Applications/Blender.app/Contents/MacOS/blender')
        
        process = subprocess.run([
            blender_path,
            '--background',
            '--python',
            blender_script,
            '--',
            bg_removed_path,
            final_3d_path
        ], capture_output=True, text=True)
        
        if process.returncode == 0:
            print("✓ 3D conversion successful")
            print(f"\nFinal output saved to: {final_3d_path}")
            return True
        else:
            print("✗ 3D conversion failed")
            print("Error output:", process.stderr)
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_full_workflow() 