import os
from dotenv import load_dotenv
from agentscope.model import GeminiChatModel
from agentscope.formatter import GeminiChatFormatter
from agentscope.message import Msg
from agentscope.agent import ReActAgent
import asyncio

load_dotenv()

async def test_gemini():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Use regular name first
    model_name = "gemini-1.5-flash"
    print(f"Testing with {model_name}...")
    
    model = GeminiChatModel(
        model_name=model_name, 
        api_key=api_key,
        stream=False
    )
    
    formatter = GeminiChatFormatter()
    
    agent = ReActAgent(
        name="TestAgent",
        model=model,
        formatter=formatter,
        sys_prompt="You are a helpful assistant."
    )
    
    user_msg = Msg(name="user", content="Hello, who are you?", role="user")
    
    try:
        response = await agent(user_msg)
        print(f"Agent Response: {response.content}")
    except Exception as e:
        print(f"Agent Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
