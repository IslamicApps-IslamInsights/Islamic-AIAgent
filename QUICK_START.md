# 🌟 Running Noor Islamic AI Agent - Quick Start Guide

## Overview

The application can be run in multiple ways depending on your needs:

- **Development**: Fast reload, detailed logging
- **Production**: Optimized performance, graceful shutdown
- **Docker**: Containerized deployment

---

## 🚀 Quick Start (Development)

### Option 1: Single Command (Recommended)

```bash
make dev
```

Or manually:

```bash
./dev.sh
```

**What this does:**
- Starts backend on `http://localhost:5010`
- Starts frontend on `http://localhost:3001`
- Watches for file changes (hot reload)
- Shows real-time logs

### Option 2: Separate Terminal Tabs

Terminal 1 (Backend):
```bash
make dev-backend
```

Terminal 2 (Frontend):
```bash
make dev-frontend
```

---

## 📦 Production Deployment

```bash
make prod
```

Or manually:

```bash
./prod.sh
```

**What this does:**
- Builds optimized frontend assets
- Starts backend with 4 worker processes
- Enables process monitoring and auto-restart
- Logs to `logs/app.log`

---

## 🐳 Docker Deployment

### Build & Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop Services

```bash
docker-compose down
```

---

## 🛠️ Useful Commands

### Check Application Health

```bash
# Backend health
curl http://localhost:5010/api/health

# Frontend status
curl http://localhost:3001
```

### View Logs

```bash
# All logs (tail -f auto-updates)
make logs

# Or specific files
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Stop Services

```bash
make stop
```

### Monitor Processes

```bash
make monitor
```

### Install Dependencies

```bash
make install
```

### Clean Up

```bash
make clean
```

---

## 📋 Environment Variables

Create or update `.env` file:

```env
# Backend
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
FLASK_ENV=development

# Frontend
VITE_API_URL=http://localhost:5010

# Deployment
BACKEND_PORT=5010
FRONTEND_PORT=3001
WORKERS=4
```

---

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :5010
lsof -i :3001

# Kill process
kill -9 <PID>
```

### Dependencies Missing

```bash
make install
```

### Backend Not Starting

```bash
# Check Python environment
which python3

# Check dependencies
python3 -m pip list | grep -E "flask|google|chromadb"

# Run backend directly to see errors
make dev-backend
```

### Frontend Not Building

```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 📚 Additional Resources

- **Development Guide**: Read `docs/DEVELOPMENT_GUIDE.md`
- **Architecture**: Read `docs/ARCHITECTURE_OVERVIEW.md`
- **API Reference**: Read `docs/API_REFERENCE.md`

---

## 💡 Tips

1. **Development**: Use `make dev` - it provides hot reload and better debugging
2. **Production**: Use `make prod` or Docker for better stability
3. **Logs**: Always check `logs/` folder when troubleshooting
4. **Health**: Use `make health-check` to verify all services

---

## 🌍 Deployment on Vercel/Netlify

The app is configured for Vercel/Netlify deployment:

- Backend: `api/index.py` serves as Vercel serverless function
- Frontend: Deploys to Netlify automatically

For details, see `vercel.json` and `netlify.toml`.

---

**May Allah bless this project and make it beneficial! 🤲**
