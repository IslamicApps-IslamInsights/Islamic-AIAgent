
import os
import agentscope
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OpenAIChatFormatter
from agentscope.agent import ReActAgent
from dotenv import load_dotenv

load_dotenv()

def test_init():
    print("Initializing AgentScope...")
    agentscope.init()
    
    # Load model configuration manually for testing if needed
    # or rely on direct model creation as shown below.
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found")
        return

    print("Creating Model...")
    model = OpenAIChatModel(
        model_name="gpt-4o-mini",
        api_key=api_key
    )
    
    print("Creating Formatter...")
    formatter = OpenAIChatFormatter()
    
    print("Creating Agent...")
    agent = ReActAgent(
        name="Noor",
        model=model,
        formatter=formatter,
        sys_prompt="You are a helpful assistant."
    )
    
    print("Agent created successfully!")
    print(f"Agent name: {agent.name}")

if __name__ == "__main__":
    test_init()
