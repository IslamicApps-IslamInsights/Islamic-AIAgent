
import os
import time
from dotenv import load_dotenv

load_dotenv()

print("1. Starting test_agentscope_v2.py")
start_time = time.time()

try:
    import agentscope
    from agentscope.model import OpenAIChatModel
    from agentscope.formatter import OpenAIChatFormatter
    from agentscope.agent import ReActAgent
    
    print(f"2. Imports done in {time.time() - start_time:.2f}s")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found")
        exit(1)
        
    print("3. Initializing agentscope...")
    agentscope.init()
    print(f"4. agentscope.init() done at {time.time() - start_time:.2f}s")
    
    print("5. Creating Model and Formatter...")
    model = OpenAIChatModel(
        model_name="gpt-4o-mini",
        api_key=api_key
    )
    formatter = OpenAIChatFormatter()
    print(f"6. Model and Formatter created at {time.time() - start_time:.2f}s")
    
    print("7. Creating ReActAgent...")
    agent = ReActAgent(
        name="TestAgent",
        model=model,
        formatter=formatter,
        sys_prompt="You are a test agent."
    )
    print(f"8. agent created at {time.time() - start_time:.2f}s")
    
    print("SUCCESS: agentscope initialized and agent created with new API")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
