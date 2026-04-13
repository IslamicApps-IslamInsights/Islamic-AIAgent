
import os
import sys
from dotenv import load_dotenv

# Ensure the project root is in the search path for modularized imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from backend.utils.llm_provider import get_gemini_client, GEMINI_MODEL, GEMINI_PRO_MODEL

def test_model(model_name):
    print(f"\n--- Testing model: {model_name} ---")
    try:
        client = get_gemini_client()
        response = client.models.generate_content(
            model=model_name,
            contents="Assalamu Alaikum. Please provide a short greeting as a scholarly AI named Noor."
        )
        if response and response.text:
            print(f"Success! Response: {response.text[:100]}...")
            return True
        else:
            print("Failed: No text in response.")
            return False
    except Exception as e:
        print(f"Failed with error: {e}")
        return False

if __name__ == "__main__":
    flash_ok = test_model(GEMINI_MODEL)
    pro_ok = test_model(GEMINI_PRO_MODEL)
    
    if flash_ok and pro_ok:
        print("\n✅ Both models are working correctly.")
    else:
        print("\n❌ One or more models failed. We might need to revert or fix names.")
