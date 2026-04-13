import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def test_raw_sdk():
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    models_to_try = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-pro",
        "gemini-1.0-pro"
    ]
    
    for model_name in models_to_try:
        print(f"\n--- Trying {model_name} ---")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello")
            print(f"✅ Success: {response.text}")
        except Exception as e:
            print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_raw_sdk()
