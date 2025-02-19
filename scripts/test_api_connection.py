import os
from mpx_genai_sdk import Masterpiecex
from dotenv import load_dotenv

load_dotenv(dotenv_path='/home/mml_admin/2dto3d/.env.local')

def test_connection():
    try:
        print("Current environment variables:", dict(os.environ))
        client = Masterpiecex(bearer_token=os.getenv("MPX_SDK_BEARER_TOKEN"))
        print("SDK initialized successfully")
        
        # Test connection using official method
        connection_test = client.connection_test.retrieve()
        print("Connection test result:", connection_test)
        return True
        
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 