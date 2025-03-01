import fbx
import FbxCommon


def test_fbx_sdk():
    # Initialize FBX SDK
    sdk_manager, scene = FbxCommon.InitializeSdkObjects()
    
    if sdk_manager:
        print("FBX SDK initialized successfully!")
        print("SDK Version:", sdk_manager.GetVersion())
    else:
        print("Failed to initialize FBX SDK")

    # Clean up
    sdk_manager.Destroy()

if __name__ == "__main__":
    test_fbx_sdk()

