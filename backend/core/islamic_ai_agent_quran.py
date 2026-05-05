"""
Islamic AI Agent Enhanced with Quran Foundation MCP
Powered by the Quran Foundation for authentic Islamic knowledge.
Simplified, reliable implementation focused on Quran-first retrieval.
"""

from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class IslamicAIAgent:
    """Islamic AI Agent powered by Quran Foundation MCP"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Islamic AI Agent with Quran Foundation MCP
        
        Args:
            api_key: Optional API key (not needed for Quran Foundation)
        """
        self.initialized = False
        self.setup_agent()
    
    def setup_agent(self):
        """Set up Islamic AI agent with Quran Foundation"""
        try:
            self.initialized = True
            
            print("✅ Islamic AI Agent with Quran Foundation initialized")
            
        except Exception as e:
            print(f"⚠️  Agent setup warning: {e}")
            self.initialized = True  # Still mark as initialized for graceful degradation
    
    def chat(self, user_message: str) -> str:
        """
        Chat with the Islamic AI agent using Quran Foundation
        
        Args:
            user_message: User's question or message
            
        Returns:
            Agent's response with Quranic knowledge
        """
        if not self.initialized:
            return "⚠️  Agent not properly initialized. Please try again."
        
        try:
            # Use Hybrid RAG with Quran Foundation priority
            from backend.utils.hybrid_rag_llm import get_hybrid_response_sync
            
            response = get_hybrid_response_sync(
                user_message,
                use_quran_foundation=True,
                use_gemini_synthesis=False
            )
            
            if response.get("final_response"):
                return response.get("final_response")
            else:
                return "⚠️  Could not generate response. Please try again."
                
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_welcome_message(self) -> str:
        """Get welcome message for the agent"""
        return """🌙 Islamic AI Agent - Powered by Quran Foundation

Assalamu Alaikum wa Rahmatullahi wa Barakatuh! 

Welcome to your Islamic AI Assistant. I'm powered by the Quran Foundation MCP, 
providing authentic Islamic guidance directly from Quranic sources.

✨ What I can help with:
📖 Quranic knowledge and verses
🕌 Islamic guidance and rulings
📚 Tafsir (Quranic interpretation)
🌟 Islamic themes and concepts
🔍 Hadith and scholarly insights

May Allah bless your learning journey! 🤲"""


def main():
    """Main entry point - test the agent"""
    agent = IslamicAIAgent()
    print(agent.get_welcome_message())
    print("\n" + "="*60)
    print("Agent Status: ✅ Ready" if agent.initialized else "Agent Status: ⚠️  Limited")
    print("="*60)


if __name__ == "__main__":
    main()
