import bpy
import os
import sys

def test_process_outfit():
    """
    Test processing an existing FBX file from Masterpiece with our templates
    """
    try:
        # Use an actual downloaded FBX from Masterpiece
        test_dir = os.path.join(os.getcwd(), 'temp', 'output', 'test_outfit')
        os.makedirs(test_dir, exist_ok=True)
        
        # This should be a path to an actual downloaded FBX from Masterpiece
        masterpiece_fbx = os.path.join(test_dir, 'original.fbx')
        
        if not os.path.exists(masterpiece_fbx):
            print(f"Error: No Masterpiece FBX found at {masterpiece_fbx}")
            print("Please first convert and download an FBX from Masterpiece")
            return False
            
        print(f"Processing Masterpiece FBX: {masterpiece_fbx}")
        
        # Test processing as different outfit types
        outfit_types = ['clothes', 'hats', 'shoes']
        
        for outfit_type in outfit_types:
            print(f"\nTesting {outfit_type} processing...")
            
            from convert_image import process_outfit_fbx
            processed_fbx = process_outfit_fbx(masterpiece_fbx, outfit_type)
            
            if os.path.exists(processed_fbx):
                print(f"Successfully processed as {outfit_type}: {processed_fbx}")
            else:
                print(f"Failed to process as {outfit_type}")
                
        return True
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run test with Blender Python
    test_process_outfit() 