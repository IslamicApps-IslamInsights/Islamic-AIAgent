import sys
import os
import time

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.utils.llm_provider import gemini_retry

# Mocking a function that fails with 429
attempt_count = 0

@gemini_retry
def mock_failing_call():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        print(f"--- Simulating 429 error (Attempt {attempt_count}) ---")
        raise Exception("429 RESOURCE_EXHAUSTED: Quota exceeded")
    print("--- Success on Attempt 3! ---")
    return "Result"

if __name__ == "__main__":
    print("🚀 Starting Resilience Test...")
    try:
        result = mock_failing_call()
        print(f"✅ Final Result: {result}")
    except Exception as e:
        print(f"❌ Final Error: {e}")
