import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv()

async def test_sdk():
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
    client = genai.Client(api_key=api_key)
    
    model_name = "models/gemini-flash-latest"
    prompt = "Hello, respond with a short greeting."
    
    print(f"Testing model with config: {model_name}")
    try:
        response = await client.aio.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "temperature": 0.0,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with config: {e}")
        
    model_name_prefixed = "models/gemini-1.5-flash"
    print(f"\nTesting model: {model_name_prefixed}")
    try:
        response = await client.aio.models.generate_content(
            model=model_name_prefixed,
            contents=prompt
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error with {model_name_prefixed}: {e}")

if __name__ == "__main__":
    asyncio.run(test_sdk())
