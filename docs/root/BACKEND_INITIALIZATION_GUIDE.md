# Backend Initialization Guide

## ⚠️ Current Issues

### 1. **API Key Compromised** (403 PERMISSION_DENIED)
The current Google Gemini API key has been reported as leaked and is rejected by Google's servers.

**Solution:**
1. Get a new API key from [Google AI Studio](https://aistudio.google.com)
2. Update your `.env` file:
   ```
   GOOGLE_API_KEY=your_new_api_key_here
   ```
3. Restart the backend

### 2. **Low Disk Space** (Only 1.1GB free)
The BGE Reranker model (2.2GB) cannot be downloaded with only 1.1GB free space.

**Solutions:**
- **Option A:** Free up disk space (need at least 2GB)
- **Option B:** Backend now uses automatic fallback to Lite KB mode
  - Skips the reranker model
  - Disables advanced re-ranking
  - Uses cached embeddings if available
  - AI responses still work, just without RAG optimization

## ✅ Improved Initialization Strategy

The updated `backend/api/web_api.py` now:

1. **Gracefully initializes agents in stages**
   - LLM Provider setup (can fail, continues)
   - Single Agent (CRITICAL - must succeed)
   - Multi-Agent System (preferred but optional)
   - Knowledge Base (optional - doesn't block)

2. **Fallback modes:**
   - If Multi-Agent fails → falls back to Single Agent
   - If Full KB fails → tries Lite KB
   - If KB fails → AI responses work without RAG

3. **Better error reporting:**
   - Each stage logs errors separately
   - Health endpoint shows detailed status
   - No silent failures

## 🚀 Running the Backend

### Standard Mode:
```bash
cd /Users/fahadiqbal/Downloads/Latest\ Projects/Islamic-AIAgent
source ~/.islamic_ai_venv/bin/activate
python backend/api/web_api.py
```

### With Diagnostics:
```bash
python scripts/diagnose_and_fix.py
```

### Lightweight Mode (Recommended for Low Disk Space):
```bash
python backend/api/server_lite.py  # If available
# Or use the standard mode - it auto-selects Lite KB
```

## 📊 Health Check

Monitor initialization with:
```bash
curl http://localhost:5010/api/health
```

Response example:
```json
{
  "status": "success",
  "agent_initialized": true,
  "single_agent_ready": true,
  "multi_agent_ready": true,
  "kb_status": "lite_mode",
  "mode": "Multi-Agent",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🔧 Debugging

### Check Logs:
```bash
tail -f logs/backend.log
```

### Look for patterns:
- `✅` = Success
- `⚠️` = Warning (continue anyway)
- `❌` = Error (may block feature)

### Common Issues:

| Issue | Solution |
|-------|----------|
| API key 403 error | Get new key from [AI Studio](https://aistudio.google.com) |
| "No space left on device" | Free up 2GB or use Lite KB mode |
| "Agents may not be fully ready" | They initialize in background, wait 30-60s |
| Module not found errors | Run `pip install -r requirements.txt` |
| Knowledge base slow | Normal on first search, uses Lite KB if available |

## 📋 Checklist Before Running

- [ ] `.env` file exists with valid `GOOGLE_API_KEY`
- [ ] At least 1GB free disk space (2GB recommended)
- [ ] Python 3.9+ with venv activated
- [ ] `backend/data/` directory exists
- [ ] `logs/` directory exists
- [ ] All Python packages installed (`pip install -r requirements.txt`)

## 🎯 Next Steps

1. **Update API Key** (if using Gemini features)
   - Visit https://aistudio.google.com
   - Generate new key
   - Update .env

2. **Free Disk Space** (optional but improves performance)
   - Clear cache: `rm -rf ~/.cache/huggingface/`
   - Or: Delete unused files/projects

3. **Restart Backend:**
   ```bash
   ./run_app.sh
   ```

4. **Verify:**
   ```bash
   curl http://localhost:5010/api/health
   ```

## ℹ️ Architecture

```
Backend Initialization Flow:
  1. Set environment variables
  2. Initialize Flask app
  3. Start LLM provider
  4. Initialize agents (main thread)
  5. Prime knowledge base (optional)
  6. Register API routes
  7. Start listening on port 5010

Agent Initialization:
  Single Agent → Multi-Agent System
  (If multi fails, single continues)
  
Knowledge Base Initialization:
  Full KB (with reranker) → Lite KB (cached only)
  (If full fails, lite is tried)
```

## 📝 Configuration

Key settings in `.env`:
```
GOOGLE_API_KEY=your_key          # Required for Gemini features
FLASK_ENV=development            # development or production
DEBUG_MODE=false                  # Enable detailed logging
```

Settings in `islamic_config.json`:
```json
{
  "enable_kb": true,              # Enable knowledge base
  "enable_rag": true,             # Enable RAG features
  "kb_lite_mode": false,          # Force lite KB (overridden if low disk)
  "agent_timeout": 30,            # Seconds to wait for agent init
  "max_retries": 3                # Retry count for API calls
}
```

---

**Last Updated:** May 2026
**Status:** Agents initialize with graceful fallbacks
**Next Milestone:** Full system functionality testing
