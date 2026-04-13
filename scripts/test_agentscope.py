
import os
import time
from dotenv import load_dotenv

load_dotenv()

print("1. Starting test_agentscope.py")
start_time = time.time()

try:
    from agentscope.model.model import load_model_configs
    import agentscope
    from agentscope.agent import ReActAgent
    
    print(f"2. Imports done in {time.time() - start_time:.2f}s")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found")
        exit(1)
        
    print("3. Loading model configs...")
    load_model_configs([{
        "config_name": "openai_cfg",
        "model_type": "openai_chat",
        "model_name": "gpt-4o-mini",
        "api_key": api_key
    }])
    
    print("4. Initializing agentscope...")
    agentscope.init()
    print(f"5. agentscope.init() done at {time.time() - start_time:.2f}s")
    
    print("6. Creating ReActAgent...")
    agent = ReActAgent(
        name="TestAgent",
        model_config_name="openai_cfg",
        sys_prompt="You are a test agent."
    )
    print(f"7. agent created at {time.time() - start_time:.2f}s")
    
    print("SUCCESS: agentscope initialized and agent created")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
