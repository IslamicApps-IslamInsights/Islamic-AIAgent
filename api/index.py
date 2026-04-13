import os
import sys

# Ensure the project root is in the search path for modularized imports
# This allows 'import backend' to work from the 'api/' directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Correctly point to the flask app instance in web_api
from backend.api.web_api import app, initialize_agents

# Trigger initialization once at startup if needed
# Note: In Serverless, this runs once per cold start
if not os.environ.get("VERCEL"):
    # Local dev handled by simple_api.py or others
    pass
else:
    # Initialize for Cloud
    # We might want to do this lazily or in the background if it's too slow
    # but for now we'll attempt it
    try:
        initialize_agents()
    except Exception as e:
        print(f"Cloud Init Error: {e}")

# Vercel looks for 'app'
app = app
