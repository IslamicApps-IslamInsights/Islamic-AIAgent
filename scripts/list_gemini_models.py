import os
from dotenv import load_dotenv
from google import genai
import asyncio

load_dotenv()

async def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("Listing available models...")
    try:
        # List models
        models = client.models.list()
        for m in models:
            print(m)
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
