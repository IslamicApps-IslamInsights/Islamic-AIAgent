import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def list_models_verbose():
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
    
    print("📋 Listing ALL models available to this API KEY:")
    try:
        for m in genai.list_models():
            print(f" - {m.name} (Supported: {m.supported_generation_methods})")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")

if __name__ == "__main__":
    list_models_verbose()
