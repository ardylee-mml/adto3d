import os
from dotenv import load_dotenv
from mpx_genai_sdk import Masterpiecex

# Load environment from specific path
load_dotenv('/home/mml_admin/2dto3d/.env.local')

# Initialize client
client = Masterpiecex(bearer_token=os.getenv("MPX_SDK_BEARER_TOKEN"))

# Create minimal test image
with open("test_image.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc``````\x00\x00\x00\x04\x00\x01\xa3\n\x15\x00\x00\x00\x00IEND\xaeB`\x82")

# Run conversion
with open("test_image.png", "rb") as f:
    job = client.functions.imageto3d(
        files={"image": f},
        parameters={
            "output_format": "glb",
            "quality": "high",
            "texture_resolution": 2048
        }
    )
    print(f"Success! Job ID: {job.id}")