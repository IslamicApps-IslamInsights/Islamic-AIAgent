"""
API Key Validator and Fallback Strategies
"""

import os
from dotenv import load_dotenv

load_dotenv()


def validate_google_api_key():
    """Validate and warn about Google API key issues"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("⚠️  No GOOGLE_API_KEY in .env file!")
        print("   Features requiring Gemini API will be unavailable")
        return False
    
    # Check for common issues
    if api_key.startswith("sk-") or "LEAKED" in api_key.upper():
        print("❌ WARNING: API key appears to be compromised or invalid!")
        print("   Please obtain a new API key from Google AI Studio")
        print("   Update your .env file with: GOOGLE_API_KEY=your_new_key")
        return False
    
    if len(api_key) < 20:
        print("⚠️  API key seems too short - may be invalid")
        return False
    
    print(f"✅ API key found (key starts with: {api_key[:10]}...)")
    return True


def get_fallback_response(context: str) -> str:
    """Generate fallback response when API is unavailable"""
    fallback_responses = {
        "hadith_search": "I can provide general Islamic knowledge, but detailed Hadith search requires the Gemini API to be configured.",
        "quran_analysis": "I can discuss Quranic concepts generally, but detailed analysis requires API access.",
        "general": "My full capabilities are limited without API access. I can still provide general Islamic guidance."
    }
    return fallback_responses.get(context, fallback_responses["general"])


if __name__ == "__main__":
    validate_google_api_key()
