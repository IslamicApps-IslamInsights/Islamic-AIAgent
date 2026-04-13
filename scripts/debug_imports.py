import sys
import time

def debug_import(module_name):
    print(f"Importing {module_name}...")
    start = time.time()
    try:
        __import__(module_name)
        print(f"Successfully imported {module_name} in {time.time() - start:.2f}s")
    except Exception as e:
        print(f"Failed to import {module_name}: {e}")

debug_import("os")
debug_import("sys")
debug_import("time")
debug_import("json")
debug_import("flask")
debug_import("flask_cors")
debug_import("asyncio")
debug_import("threading")
debug_import("queue")
debug_import("dotenv")
debug_import("islamic_ai_agent")
debug_import("multi_agent_islamic_system")
print("All debug imports done")
