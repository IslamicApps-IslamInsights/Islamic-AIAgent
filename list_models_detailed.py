import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
    client = genai.Client(api_key=api_key)
    
    print("Listing models...")
    for model in client.models.list():
        actions = model.supported_actions or []
        if 'generateContent' in actions:
            print(f"- {model.name} (Supported)")
        else:
            print(f"- {model.name} (NOT supported for generation: {actions})")

if __name__ == "__main__":
    list_models()
