# 🔴 Frontend Connection Errors - Complete Troubleshooting Guide

## Error Summary

You're seeing these errors because the **backend server is NOT running**:

```
❌ Failed to load resource: net::ERR_CONNECTION_REFUSED
❌ Failed to fetch Islamic data TypeError: Failed to fetch
❌ Chat error: TypeError: Failed to fetch
```

---

## Root Cause Analysis

| Error | Cause | Solution |
|-------|-------|----------|
| `ERR_CONNECTION_REFUSED` on `:5010/api/prayer-times` | Backend not listening on port 5010 | Start backend server |
| `ERR_CONNECTION_REFUSED` on `:5010/api/chat` | Backend process not running | Start backend server |
| `Failed to fetch Islamic data` | Network request to backend failed | Start backend server |
| `Chat error: Failed to fetch` | POST request to backend rejected | Start backend server |
| `runtime.lastError: Could not establish connection` | Browser extension trying to reach non-existent receiver | Safe to ignore |

---

## 🚀 Quick Fix (5 Minutes)

### **1. Kill Any Stuck Processes**

```bash
# Force kill all Python backend processes
pkill -9 -f "python.*web_api|python.*backend"

# Verify they're gone
ps aux | grep -i python | grep -i backend
# Should show no results
```

### **2. Start Backend Server**

```bash
cd "/Users/fahadiqbal/Downloads/Latest Projects/Islamic-AIAgent"

# Start backend (runs in background)
python3 backend/api/web_api.py > logs/backend.log 2>&1 &

# Wait for startup
sleep 5

# Verify it's running
curl http://localhost:5010/api/health | python3 -m json.tool
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "Islamic AI Agent Backend",
  "rag_ready": true,
  "components": {...}
}
```

### **3. Refresh Frontend in Browser**

- **Mac**: Cmd+Shift+R (hard refresh)
- **Windows/Linux**: Ctrl+Shift+R

**Result**: All errors should disappear! ✅

---

## 📋 Complete Backend Startup Script

Create this file as `start_backend.sh`:

```bash
#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/fahadiqbal/Downloads/Latest Projects/Islamic-AIAgent"

echo -e "${YELLOW}🔧 Starting Islamic AI Agent Backend${NC}"

# Step 1: Kill existing processes
echo -e "${YELLOW}1️⃣  Killing existing processes...${NC}"
pkill -9 -f "python.*web_api|python.*backend" 2>/dev/null
sleep 2

# Step 2: Verify venv
echo -e "${YELLOW}2️⃣  Checking Python environment...${NC}"
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Run: cd '$PROJECT_DIR' && python3 -m venv .venv"
    exit 1
fi

# Step 3: Start backend
cd "$PROJECT_DIR"
echo -e "${YELLOW}3️⃣  Starting backend on http://localhost:5010${NC}"
python3 backend/api/web_api.py > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Step 4: Wait for startup
echo -e "${YELLOW}4️⃣  Waiting for backend to initialize (up to 10 seconds)...${NC}"
for i in {1..20}; do
    if curl -s http://localhost:5010/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 0.5
done

# Step 5: Verify
echo ""
echo -e "${YELLOW}5️⃣  Verifying backend health...${NC}"
HEALTH=$(curl -s http://localhost:5010/api/health)
if echo "$HEALTH" | grep -q '"status"'; then
    echo -e "${GREEN}✅ Backend is running and responsive!${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo -e "${RED}❌ Backend did not respond properly${NC}"
    echo "Check logs: tail -50 logs/backend.log"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Backend started successfully!${NC}"
echo -e "${YELLOW}📱 Frontend should connect automatically${NC}"
echo -e "${YELLOW}📜 Backend logs: tail -f logs/backend.log${NC}"
```

**Run it:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

---

## 🔍 Detailed Troubleshooting

### **Scenario 1: Backend Won't Start**

**Symptoms**: `python3 backend/api/web_api.py` exits immediately

**Debug steps:**
```bash
# 1. Check Python version
python3 --version  # Should be 3.8+

# 2. Check dependencies
pip list | grep -i flask
pip list | grep -i langchain

# 3. Run with error output
python3 backend/api/web_api.py  # Don't redirect stderr

# 4. Check logs
tail -100 logs/backend.log

# 5. Reinstall dependencies
pip install -r requirements.txt
```

---

### **Scenario 2: Backend Starts but Connection Refused**

**Symptoms**: Backend runs but frontend can't connect

**Debug steps:**
```bash
# 1. Check if backend is listening on port 5010
lsof -i :5010
# Should show: python3 ... LISTEN

# 2. Test locally
curl -s http://localhost:5010/api/health | python3 -m json.tool

# 3. Check if port is occupied by something else
sudo lsof -i :5010  # Show all processes on port 5010

# 4. Try different port
# Edit backend to use port 5011 instead and retry
```

---

### **Scenario 3: Backend Responds But Frontend Still Fails**

**Symptoms**: Backend healthy but frontend gets `Failed to fetch`

**Debug steps:**
```bash
# 1. Check CORS headers
curl -i -X OPTIONS http://localhost:5010/api/chat

# 2. Test API endpoint directly
curl -X POST http://localhost:5010/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Test query","use_synthesis":true}'

# 3. Check if response is valid JSON
# Check browser Network tab (F12 → Network)

# 4. Verify frontend is using correct API URL
# Check browser console: window.location.origin
```

---

## 🎯 Error Messages - What They Mean

### **ERR_CONNECTION_REFUSED**
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
```
- **Meaning**: Connection actively refused - backend not listening
- **Fix**: Start backend with `python3 backend/api/web_api.py`

### **TypeError: Failed to fetch**
```
TypeError: Failed to fetch
    at fetchIslamicData (IslamicAIAgent.tsx:694)
```
- **Meaning**: Network request failed (backend unreachable)
- **Fix**: Verify backend is running with `curl http://localhost:5010/api/health`

### **runtime.lastError**
```
Unchecked runtime.lastError: Could not establish connection. 
Receiving end does not exist.
```
- **Meaning**: Chrome extension trying to reach something that isn't there
- **Fix**: Harmless - can ignore or disable extensions

---

## ✅ Verification Checklist

- [ ] Backend process is running: `ps aux | grep web_api`
- [ ] Port 5010 is listening: `lsof -i :5010`
- [ ] Health check passes: `curl http://localhost:5010/api/health`
- [ ] Response is valid JSON: Check with `jq`
- [ ] Frontend can reach backend: Check browser Network tab
- [ ] No CORS errors: Check browser console
- [ ] Frontend shows no connection errors: Check F12 console

---

## 🛠️ Production Deployment

For always-on backend:

### **Option 1: systemd Service (Linux/Mac)**

Create `/etc/systemd/system/noor-backend.service`:
```ini
[Unit]
Description=Noor Islamic AI Agent Backend
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/Islamic-AIAgent
ExecStart=/usr/bin/python3 backend/api/web_api.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable noor-backend
sudo systemctl start noor-backend
sudo systemctl status noor-backend
```

### **Option 2: PM2 (Node.js process manager)**

```bash
npm install -g pm2

# Start backend with PM2
pm2 start "python3 backend/api/web_api.py" --name "noor-backend"

# Auto-restart on reboot
pm2 startup
pm2 save

# Monitor
pm2 logs noor-backend
pm2 status
```

### **Option 3: Docker**

```bash
# Build
docker build -f Dockerfile.backend -t noor-backend .

# Run
docker run -p 5010:5010 \
  -v $(pwd)/backend:/app/backend \
  -v $(pwd)/logs:/app/logs \
  noor-backend
```

---

## 📊 Monitoring

### **Watch Logs in Real-Time**
```bash
tail -f logs/backend.log | grep -E "ERROR|WARNING|INFO"
```

### **Monitor Performance**
```bash
# CPU & Memory
watch -n 1 "ps aux | grep web_api"

# Port activity
watch -n 1 "lsof -i :5010"
```

### **Health Check Loop**
```bash
while true; do
    STATUS=$(curl -s http://localhost:5010/api/health | jq '.status' 2>/dev/null)
    TIME=$(date '+%H:%M:%S')
    echo "[$TIME] Backend status: $STATUS"
    sleep 5
done
```

---

## 🆘 Emergency Recovery

If everything is stuck:

```bash
# 1. Kill everything
pkill -9 -f "python.*web_api|python.*backend"
pkill -9 -f "node.*frontend"
pkill -9 -f "npm.*dev"

# 2. Clear cache/temp
rm -rf /tmp/noor-*
rm -rf frontend/node_modules/.vite

# 3. Restart fresh
cd "/Users/fahadiqbal/Downloads/Latest Projects/Islamic-AIAgent"
python3 backend/api/web_api.py

# 4. In another terminal
cd frontend
npm run dev

# 5. Check both are running
curl http://localhost:5010/api/health  # Backend
curl http://localhost:3001            # Frontend
```

---

## 📱 Frontend Error Handling Improvements

The frontend now provides better error messages:

### **Old vs New Error Messages**

| Scenario | Old Error | New Error |
|----------|-----------|-----------|
| Backend not running | "Connection issue - Attempting to restore" | "🔌 Backend not running at http://localhost:5010\n💻 Start: python3 backend/api/web_api.py" |
| Network timeout | "Failed to fetch" | "⏱️ Request timeout - Backend may be processing" |
| Prayer times API fails | "Failed to fetch Islamic data" | "⏠️ Cannot connect to backend at http://localhost:5010" |
| Chat API fails | "Chat error" | "❌ Backend error: [specific error message]" |

---

## 🎯 Summary

| Step | Command | Expected Result |
|------|---------|-----------------|
| **1. Kill processes** | `pkill -9 -f "python.*backend"` | No output |
| **2. Start backend** | `python3 backend/api/web_api.py` | `Running on http://0.0.0.0:5010` |
| **3. Verify health** | `curl http://localhost:5010/api/health` | JSON with `"status": "healthy"` |
| **4. Refresh frontend** | Cmd+Shift+R | No connection errors in console |
| **5. Test chat** | Send message in UI | ✅ Response received |

---

**Last Updated**: May 2, 2026
**Version**: 2.0 - Enhanced Error Handling
