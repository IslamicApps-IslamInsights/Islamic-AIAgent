# 🌟 Three Ways to Run Noor Islamic AI Agent

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│                 🚀 CHOOSE YOUR DEPLOYMENT METHOD 🚀                      │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ ⚡ DEVELOPMENT                                                            │
│ ─────────────────────────────────────────────────────────────────────── │
│                                                                            │
│  Command:  make dev  (or: ./dev.sh)                                       │
│                                                                            │
│  ✓ Hot reload - changes update instantly                                 │
│  ✓ Concurrent start - both services at once                              │
│  ✓ Auto health checks - ready when initialized                           │
│  ✓ Beautiful dashboard - clear status display                            │
│  ✓ Live logs - see what's happening                                      │
│  ✓ Easy shutdown - Ctrl+C stops gracefully                               │
│                                                                            │
│  Best for: Local development, debugging, rapid iteration                 │
│  Startup:  ~5-8 seconds                                                   │
│  Access:   http://localhost:3001 (Frontend)                              │
│            http://localhost:5010 (Backend)                               │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ 🚀 PRODUCTION                                                             │
│ ─────────────────────────────────────────────────────────────────────── │
│                                                                            │
│  Command:  make prod  (or: ./prod.sh)                                     │
│                                                                            │
│  ✓ Multi-worker processes - 4 worker threads                             │
│  ✓ Auto-restart - crashed services restart automatically                 │
│  ✓ Health monitoring - continuous service checks                         │
│  ✓ Graceful shutdown - SIGTERM handling                                  │
│  ✓ Optimized builds - frontend pre-built                                 │
│  ✓ Production logging - file-based logs                                  │
│                                                                            │
│  Best for: Deployment servers, CI/CD pipelines, staging                  │
│  Startup:  ~8-12 seconds                                                  │
│  Access:   http://localhost:3001 (Frontend)                              │
│            http://localhost:5010 (Backend)                               │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│ 🐳 DOCKER                                                                 │
│ ─────────────────────────────────────────────────────────────────────── │
│                                                                            │
│  Command:  docker-compose up -d                                           │
│                                                                            │
│  ✓ Containerized - isolated environments                                 │
│  ✓ Reproducible - same everywhere                                        │
│  ✓ Scalable - easy to add more services                                  │
│  ✓ Health checks - built-in container health                            │
│  ✓ Nginx proxy - reverse proxy included                                  │
│  ✓ Cloud-ready - deploy to any cloud platform                           │
│                                                                            │
│  Best for: Cloud deployment, Kubernetes, microservices                   │
│  Startup:  ~15-20 seconds (image build first time)                       │
│  Access:   http://localhost (via Nginx)                                  │
│            http://localhost:3001 (Direct Frontend)                       │
│            http://localhost:5010 (Direct Backend)                        │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                         📊 COMPARISON TABLE                              │
│                                                                            │
│  Feature              │  Development  │  Production  │  Docker          │
│  ─────────────────────┼───────────────┼──────────────┼──────────────    │
│  Setup Time           │  Instant      │  2 seconds   │  First: 20s      │
│  Hot Reload           │  Yes ✓        │  No          │  No              │
│  Worker Processes     │  1            │  4           │  4               │
│  Health Checks        │  Yes ✓        │  Yes ✓       │  Yes ✓           │
│  Auto Restart         │  No           │  Yes ✓       │  Yes ✓           │
│  Container Support    │  No           │  No          │  Yes ✓           │
│  Production Ready     │  No           │  Yes ✓       │  Yes ✓           │
│  Memory Usage         │  ~500MB       │  ~600MB      │  ~800MB          │
│  CPU Usage            │  Low          │  Medium      │  Medium          │
│  Logs Location        │  Console+file │  File only   │  Docker logs     │
│  Deployment           │  Local only   │  Local/VPS   │  Cloud/K8s       │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                         🛠️ COMMON COMMANDS                               │
│                                                                            │
│  make dev                - Start development server                      │
│  make prod               - Start production server                       │
│  make dev-backend        - Backend development only                      │
│  make dev-frontend       - Frontend development only                     │
│  make install            - Install dependencies                          │
│  make logs               - View real-time logs                           │
│  make stop               - Stop all services                             │
│  make clean              - Clean artifacts                               │
│  make health-check       - Check service health                          │
│  make monitor            - Monitor processes                             │
│  make help               - Show all commands                             │
│                                                                            │
│  docker-compose up -d    - Start Docker stack                            │
│  docker-compose down     - Stop Docker stack                             │
│  docker-compose logs -f  - Stream Docker logs                            │
│  docker-compose ps       - Show container status                         │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│                    🎯 CHOOSE BASED ON USE CASE                           │
│                                                                            │
│  I want to...              │  Use this method                             │
│  ───────────────────────────┼──────────────────────────────────────────  │
│  Develop locally            │  make dev                                   │
│  Debug issues               │  make dev-backend / make dev-frontend       │
│  Deploy on server           │  make prod                                  │
│  Deploy to cloud            │  docker-compose up -d                       │
│  Deploy to Kubernetes       │  docker-compose (then kubectl apply)        │
│  Setup CI/CD pipeline       │  docker-compose / prod.sh                   │
│  Test production config     │  make prod                                  │
│  Check service health       │  make health-check                          │
│  Monitor running services   │  make monitor                               │
│  See logs in real-time      │  make logs                                  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started (Pick One)

### Option 1: Development (Recommended for local work)
```bash
make dev
# That's it! Your app is running with hot reload
```

### Option 2: Production (For deployment)
```bash
make prod
# Multi-worker, auto-restart, monitoring enabled
```

### Option 3: Docker (For cloud)
```bash
docker-compose up -d
# Full containerized stack ready for cloud
```

---

## 📚 Need Help?

```bash
make help                    # Show all commands
cat QUICK_START.md          # Full getting started guide
cat RUNNER_IMPROVEMENTS.md  # Detailed improvements
python scripts/show_runner_summary.py  # Show this summary
```

---

**Status:** ✅ All runners tested and operational
**Ready to use:** Yes, start with `make dev`
