"""
Gemini-powered Islamic AI Agent
Provides intelligent Islamic guidance using Google's Gemini AI
"""

import os
import google.generativeai as genai
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiIslamicAgent:
    """Islamic AI Agent powered by Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini Islamic AI Agent
        
        Args:
            api_key: Google API key (optional, can be set in .env file)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY in .env file or pass as parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Islamic AI system prompt
        self.system_prompt = """بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ

You are an Islamic AI Assistant named "Noor" (meaning "Light" in Arabic) from TheIslamInsights.com. You provide authentic Islamic guidance based on the Quran and Sunnah.

**Your Purpose:**
- Provide accurate Islamic knowledge and guidance
- Help Muslims with their daily religious practices
- Share authentic Hadith and Quran verses with proper citations
- Assist with prayer times, Qibla direction, and Islamic calendar
- Offer spiritual guidance based on Islamic teachings

**Your Capabilities:**
- Access to Quran verses with Arabic text and translations
- Knowledge of authentic Hadith collections from Sahih sources
- Understanding of Islamic jurisprudence (Fiqh)
- Guidance on worship, fasting, charity, pilgrimage
- Islamic calendar and Hijri date knowledge
- Duas for various occasions with Arabic text and transliterations

**Guidelines:**
1. Always provide authentic information based on Quran and Sunnah
2. Include Arabic text when sharing Quran verses or Duas
3. Cite sources for Hadith (e.g., Sahih Bukhari, Sahih Muslim)
4. Be respectful and use Islamic greetings
5. For complex religious matters, recommend consulting qualified scholars
6. Be helpful, patient, and kind in all interactions
7. Use emojis appropriately to make responses engaging

**Response Style:**
- Start responses with appropriate Islamic greetings when relevant
- Use proper Islamic phrases (InshaAllah, MashaAllah, Alhamdulillah, etc.)
- Format responses clearly with emojis and structure
- Include Arabic text with transliterations for Quran verses and Duas
- Provide practical guidance alongside spiritual advice
- End with appropriate Islamic phrases or duas

**Topics you can help with:**
- Quran verses and their meanings
- Authentic Hadith and their applications
- Five daily prayers and their procedures
- Islamic calendar and important dates
- Zakat (charity) calculations and guidance
- Hajj and Umrah procedures
- Islamic finance and halal/haram guidance
- Duas for various occasions
- Islamic history and biography of Prophet Muhammad (ﷺ)
- Fiqh (Islamic jurisprudence) questions

Remember: You are here to serve Allah by helping His servants learn and practice Islam correctly. Always maintain the highest standards of authenticity and respect for Islamic teachings."""

        print("🌟 Gemini Islamic AI Agent 'Noor' is ready!")
        print("🤖 Powered by Google Gemini AI")
        print("🤲 May Allah bless your learning journey!")
    
    def get_response(self, message: str) -> str:
        """
        Get AI response for a given message
        
        Args:
            message: User's message/question
            
        Returns:
            AI-generated Islamic guidance response
        """
        try:
            # Combine system prompt with user message
            full_prompt = f"{self.system_prompt}\n\nUser Question: {message}\n\nPlease provide authentic Islamic guidance:"
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response at this time. Please try rephrasing your question or ask about a specific Islamic topic."
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"I'm experiencing some technical difficulties. Please try again later or ask a different question. For immediate Islamic guidance, please consult your local Islamic scholar.\n\nError: {str(e)}"
    
    def get_quran_guidance(self, topic: str) -> str:
        """Get Quranic guidance on a specific topic"""
        prompt = f"What does the Quran say about {topic}? Please provide relevant verses with Arabic text, transliterations, translations, and explanations."
        return self.get_response(prompt)
    
    def get_hadith_guidance(self, topic: str) -> str:
        """Get Hadith guidance on a specific topic"""
        prompt = f"What do authentic Hadith say about {topic}? Please provide relevant Hadith with proper citations from Sahih collections."
        return self.get_response(prompt)
    
    def get_prayer_guidance(self) -> str:
        """Get guidance about Islamic prayers"""
        prompt = "Please explain the five daily prayers in Islam, their times, and how to perform them correctly."
        return self.get_response(prompt)
    
    def get_dua_for_occasion(self, occasion: str) -> str:
        """Get dua for a specific occasion"""
        prompt = f"Please provide authentic duas for {occasion} with Arabic text, transliteration, and English translation."
        return self.get_response(prompt)
    
    def get_islamic_guidance(self, question: str) -> str:
        """Get general Islamic guidance"""
        return self.get_response(question)

def test_gemini_agent():
    """Test function for the Gemini Islamic Agent"""
    try:
        # Initialize agent
        agent = GeminiIslamicAgent()
        
        # Test questions
        test_questions = [
            "What does the Quran say about patience?",
            "Tell me about the importance of prayer in Islam",
            "What are the five pillars of Islam?",
            "How do I calculate Zakat?"
        ]
        
        print("\n🧪 Testing Gemini Islamic AI Agent...")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*50}")
            print(f"Test {i}: {question}")
            print('='*50)
            
            response = agent.get_response(question)
            print(response)
            
            if i < len(test_questions):
                input("\nPress Enter to continue to next test...")
        
        print("\n✅ Gemini Islamic AI Agent testing completed!")
        
    except Exception as e:
        print(f"❌ Error testing Gemini agent: {e}")
        print("Please make sure you have set your GOOGLE_API_KEY in the .env file")

if __name__ == "__main__":
    test_gemini_agent()
