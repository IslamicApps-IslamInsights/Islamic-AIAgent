# 🌟 Master Application Runner - Complete Guide

## The Best Way to Run Everything

You now have **multiple ways** to run the Noor Islamic AI Agent. Here's which one to use:

---

## ⚡ EASIEST - Ultra-Simple (Recommended for most users)

```bash
./start.sh
```

**That's it!** Everything starts automatically.

- ✅ Hot reload enabled
- ✅ Both services start together
- ✅ Auto health checks
- ✅ Live status dashboard

Access at: http://localhost:3001

---

## 🎛️ FLEXIBLE - Master Runner Script

```bash
./run.sh              # Development (hot reload)
./run.sh --prod       # Production (optimized)
./run.sh --help       # Show help
./run.sh --health     # Check health only
```

**Features:**
- Single unified script
- Mode auto-detection
- Better error handling
- Comprehensive logging
- Process management

---

## 🚀 PRODUCTION - Optimized Deployment

```bash
./start-prod.sh
# or
./run.sh --prod
# or
ENVIRONMENT=production ./run.sh
```

**What happens:**
- Builds frontend for production
- Starts backend with 4 worker processes (Gunicorn)
- Auto-restarts on crash
- Optimized performance
- Production logging

---

## 📦 MAKE COMMANDS - Traditional Interface

```bash
make dev              # Development
make prod             # Production
make logs             # View logs
make stop             # Stop services
make help             # All commands
```

---

## 🐳 DOCKER - Container-Based

```bash
docker-compose up -d
```

---

## 📊 Comparison Table

| Command | Mode | Hot Reload | Performance | Best For |
|---------|------|------------|-------------|----------|
| `./start.sh` | Dev | ✅ Yes | Good | **Most users** |
| `./run.sh` | Dev | ✅ Yes | Good | Power users |
| `./run.sh --prod` | Prod | ❌ No | **Best** | Deployment |
| `./start-prod.sh` | Prod | ❌ No | **Best** | Production |
| `make dev` | Dev | ✅ Yes | Good | Developers |
| `make prod` | Prod | ❌ No | **Best** | Developers |
| `docker-compose up` | Container | ❌ No | **Best** | Cloud/K8s |

---

## 🎯 Quick Decision Guide

**"I just want to start developing"**
```bash
./start.sh
```

**"I want more control"**
```bash
./run.sh --help
./run.sh
```

**"I'm deploying to production"**
```bash
./start-prod.sh
```

**"I prefer make commands"**
```bash
make dev
```

**"I'm using Docker"**
```bash
docker-compose up -d
```

---

## 📍 What Each Script Does

### start.sh (Ultra-Simple)
- Runs `./run.sh` in development mode
- Perfect for beginners
- One-command startup

### start-prod.sh (Production)
- Runs `./run.sh --prod`
- Perfect for deployment
- Optimized configuration

### run.sh (Master Runner)
The most powerful and flexible script:

```
./run.sh              → Development mode (default)
./run.sh --prod       → Production mode
./run.sh --help       → Show help
./run.sh --health     → Health check
./run.sh --version    → Version info
```

**Development mode:**
- Flask development server
- Vite with hot reload
- Console logging
- Auto health checks
- Concurrent startup

**Production mode:**
- Gunicorn with 4 workers
- Optimized frontend build
- File logging
- Process monitoring
- Health recovery

---

## 🔄 How They Relate

```
start.sh ──→ run.sh (default/dev)
start-prod.sh ──→ run.sh --prod
make dev ──→ dev.sh
make prod ──→ prod.sh
```

---

## 📍 Service URLs

All modes start services on the same ports:

- **Frontend:** http://localhost:3001
- **Backend:** http://localhost:5010
- **Backend Health:** http://localhost:5010/api/health

---

## 📋 Logs Location

All modes save logs to `logs/` directory:

```
logs/
├── frontend.log          # Frontend server logs
├── backend.log           # Backend server logs
└── backend_access.log    # Backend HTTP access (prod only)
```

View logs:
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

Or use:
```bash
make logs
```

---

## ✋ Stopping Services

All modes listen to `Ctrl+C` for graceful shutdown:

```bash
# Press Ctrl+C in the terminal running the script
# Services will shut down gracefully
```

Or kill from another terminal:
```bash
make stop
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file:
```bash
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
FLASK_ENV=development
VITE_API_URL=http://localhost:5010
```

### Port Configuration

Edit the script to change ports:
```bash
# In run.sh, prod.sh, or dev.sh
BACKEND_PORT=5010
FRONTEND_PORT=3001
```

---

## 🐛 Troubleshooting

### "Port already in use"
```bash
make stop
./start.sh
```

### "Dependencies missing"
```bash
make install
```

### "Services not starting"
```bash
./run.sh --health
tail -f logs/backend.log
```

### "Frontend not showing"
```bash
cd frontend && npm install && cd ..
./start.sh
```

---

## 🚀 Complete Workflow

### Local Development
```bash
./start.sh          # Start with hot reload
# Make changes to code
# Changes reload automatically
# Press Ctrl+C to stop
```

### Testing Production Locally
```bash
./start-prod.sh     # Start optimized
# Test full application
# Check performance
```

### Deploying
```bash
# Via Docker
docker-compose up -d

# Or via SSH to server
./start-prod.sh
```

---

## 📚 Related Documentation

- **QUICK_START.md** - Getting started guide
- **DEPLOYMENT_METHODS.md** - Detailed comparison
- **RUNNER_IMPROVEMENTS.md** - Behind the scenes
- **Makefile** - All make commands

---

## 💡 Pro Tips

1. **Use `./start.sh` for 99% of development**
   - Simple, reliable, perfect for daily work

2. **Use `./run.sh --help` when you need options**
   - More control, better debugging

3. **Use `./start-prod.sh` before deploying**
   - Test production mode locally

4. **Use `make logs` in another terminal**
   - See logs while working

5. **Keep `.env` in .gitignore**
   - Never commit API keys

---

## ✨ Summary

You have **3 ways** to run the app:

```bash
./start.sh           # Easiest - just works!
./run.sh --prod      # Flexible - more options
docker-compose up    # Scalable - containers
```

**Pick your comfort level and go!**

---

**Status:** ✅ All systems operational  
**Ready:** Yes, start with `./start.sh`  

May Allah bless this project! 🤲
