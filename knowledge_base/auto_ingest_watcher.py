import time
import os
import sys
import logging
import hashlib

# Add current directory to path so we can import ingest_data
sys.path.append(os.path.abspath(os.curdir))

from knowledge_base.ingest_data import run_ingestion

# Setup Logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "auto_ingestion.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_dir_state(path):
    """Returns a dictionary mapping filenames to their modification times"""
    state = {}
    for filename in os.listdir(path):
        if filename.endswith((".txt", ".pdf", ".json")):
            file_path = os.path.join(path, filename)
            state[filename] = os.path.getmtime(file_path)
    return state

def start_polling_watcher():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if not os.path.exists(path):
        os.makedirs(path)
        
    logging.info(f"📡 'Noor' Knowledge Watcher (Polling Mode) started on: {path}")
    logging.info("Watching for new or modified scholarly texts...")
    
    last_state = get_dir_state(path)
    
    try:
        while True:
            time.sleep(5) # Poll every 5 seconds
            current_state = get_dir_state(path)
            
            changes = False
            for filename, mtime in current_state.items():
                if filename not in last_state or mtime > last_state[filename]:
                    logging.info(f"🔔 Change detected in: {filename}")
                    changes = True
                    break
            
            if not changes:
                # Check for deletions (though less critical for ingestion)
                for filename in last_state:
                    if filename not in current_state:
                        logging.info(f"🔔 File removed: {filename}")
                        changes = True
                        break
            
            if changes:
                logging.info("🚀 Starting auto-ingestion...")
                try:
                    run_ingestion()
                    logging.info("✅ Auto-ingestion completed successfully.")
                except Exception as e:
                    logging.error(f"❌ Auto-ingestion failed: {e}")
                
                last_state = current_state
                
    except KeyboardInterrupt:
        logging.info("🛑 Watcher stopped.")

if __name__ == "__main__":
    start_polling_watcher()
