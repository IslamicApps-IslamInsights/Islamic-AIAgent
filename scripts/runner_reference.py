#!/usr/bin/env python3
"""
Noor Islamic AI Agent - Application Runner Reference
Visual guide to all ways to run the application
"""

def print_banner():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           🌟 NOOR ISLAMIC AI AGENT - RUNNER REFERENCE GUIDE 🌟            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

def main():
    print_banner()
    
    print("""
📋 FIVE WAYS TO RUN YOUR APPLICATION
─────────────────────────────────────────────────────────────────────────────

┌──────────────────────────────────────────────────────────────────────────┐
│ #1 🎯 EASIEST - Ultra-Simple (👈 RECOMMENDED FOR MOST USERS)            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Command:  ./start.sh                                                   │
│                                                                          │
│  What it does:                                                          │
│  ✓ Starts backend AND frontend together                                 │
│  ✓ Enables hot reload                                                   │
│  ✓ Shows status dashboard                                               │
│  ✓ Auto health checks                                                   │
│  ✓ Graceful shutdown on Ctrl+C                                          │
│                                                                          │
│  Best for:  Anyone who just wants it to work                           │
│  Startup:   ~5-8 seconds                                                │
│  Access:    http://localhost:3001                                       │
│                                                                          │
│  Example:                                                               │
│  $ ./start.sh                                                            │
│  ✓ Backend started (PID: 12345)                                         │
│  ✓ Frontend started (PID: 12346)                                        │
│  [Press Ctrl+C to stop]                                                 │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ #2 🔧 FLEXIBLE - Master Runner Script                                   │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Command:  ./run.sh [OPTIONS]                                           │
│                                                                          │
│  Options:                                                               │
│    ./run.sh              → Development (hot reload)                     │
│    ./run.sh --prod       → Production (optimized, 4 workers)           │
│    ./run.sh --help       → Show help                                    │
│    ./run.sh --health     → Check service health                         │
│    ./run.sh --version    → Show version                                 │
│                                                                          │
│  Best for:  Developers who want options                                 │
│  Startup:   ~5-8s (dev) or ~8-12s (prod)                               │
│  Access:    http://localhost:3001                                       │
│                                                                          │
│  Examples:                                                              │
│  $ ./run.sh                    # Development mode                       │
│  $ ./run.sh --prod             # Production mode                        │
│  $ ./run.sh --health           # Check health                           │
│  $ ENVIRONMENT=production ./run.sh  # Via env var                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ #3 🚀 PRODUCTION - Optimized Starter                                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Command:  ./start-prod.sh                                              │
│                                                                          │
│  What it does:                                                          │
│  ✓ Builds frontend for production                                       │
│  ✓ Starts backend with 4 Gunicorn workers                              │
│  ✓ Enables process monitoring                                           │
│  ✓ Auto-restarts crashed services                                      │
│  ✓ Optimized performance                                                │
│                                                                          │
│  Best for:  Production deployment                                       │
│  Startup:   ~8-12 seconds                                               │
│  Access:    http://localhost:3001                                       │
│                                                                          │
│  Equivalent to:  ./run.sh --prod                                        │
│                                                                          │
│  Example:                                                               │
│  $ ./start-prod.sh                                                       │
│  ✓ Building frontend...                                                 │
│  ✓ Backend started (4 workers)                                          │
│  ✓ Frontend started (production)                                        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ #4 ⚙️  MAKE COMMANDS - Traditional Interface                             │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Command:  make <target>                                                │
│                                                                          │
│  Common targets:                                                        │
│    make dev              → Development mode                             │
│    make prod             → Production mode                              │
│    make logs             → View live logs                               │
│    make stop             → Stop services                                │
│    make health-check     → Check health                                 │
│    make help             → Show all commands                            │
│                                                                          │
│  Best for:  Developers familiar with Makefiles                         │
│  Access:    http://localhost:3001                                       │
│                                                                          │
│  Example:                                                               │
│  $ make dev                                                              │
│  $ make logs              # In another terminal                         │
│  $ make stop              # To stop                                     │
│                                                                          │
│  Equivalent to:  ./start.sh  and  ./start-prod.sh                      │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ #5 🐳 DOCKER - Container-Based Deployment                               │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Command:  docker-compose up -d                                         │
│                                                                          │
│  What it does:                                                          │
│  ✓ Builds and runs containers                                           │
│  ✓ Sets up networking                                                   │
│  ✓ Includes Nginx reverse proxy                                         │
│  ✓ Container health checks                                              │
│  ✓ Volume management                                                    │
│                                                                          │
│  Best for:  Cloud deployment, Kubernetes, CI/CD                        │
│  Startup:   ~15-20 seconds (first time)                                │
│  Access:    http://localhost                                            │
│                                                                          │
│  Common commands:                                                       │
│    docker-compose up -d      → Start                                    │
│    docker-compose down       → Stop                                     │
│    docker-compose logs -f    → View logs                                │
│    docker-compose ps         → Status                                   │
│                                                                          │
│  Example:                                                               │
│  $ docker-compose up -d                                                 │
│  $ docker-compose logs -f backend                                       │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘


═════════════════════════════════════════════════════════════════════════════

🎯 QUICK DECISION MATRIX
─────────────────────────────────────────────────────────────────────────────

Situation                          → Use this command
─────────────────────────────────────────────────────────────────────────────
Just starting (quick test)         → ./start.sh
Local development                  → ./start.sh
Testing production locally         → ./start-prod.sh  or  ./run.sh --prod
Deploying to server                → ./start-prod.sh
Using Docker                       → docker-compose up -d
Need to see logs                   → make logs
Want to stop services              → make stop  or Ctrl+C
Check if services running          → ./run.sh --health  or  make health-check
Learning/exploring                 → ./run.sh --help


═════════════════════════════════════════════════════════════════════════════

📊 COMPARISON TABLE
─────────────────────────────────────────────────────────────────────────────

Feature               ./start.sh    ./run.sh    ./start-prod    make dev    Docker
───────────────────────────────────────────────────────────────────────────
Simplicity            ★★★★★        ★★★★       ★★★★            ★★★         ★★
Hot Reload            ✓             ✓          ✗               ✓           ✗
Worker Processes      1             1          4               1           4
Auto-restart          ✗             ✗          ✓               ✗           ✓
Containerized         ✗             ✗          ✗               ✗           ✓
Best For              Everyone      Devs       Deployment      Devs        Cloud
Startup Time          ~5s           ~5s        ~10s            ~5s         ~20s


═════════════════════════════════════════════════════════════════════════════

🌐 ACCESS POINTS
─────────────────────────────────────────────────────────────────────────────

Service                 URL                              Port
───────────────────────────────────────────────────────────────────────────
Frontend (UI)           http://localhost:3001            3001
Backend API             http://localhost:5010            5010
Backend Health          http://localhost:5010/api/health 5010
Docker (via Nginx)      http://localhost                 80/443


═════════════════════════════════════════════════════════════════════════════

📁 FILES CREATED
─────────────────────────────────────────────────────────────────────────────

Main Runners:
  ✓ run.sh                - Master runner (most powerful)
  ✓ start.sh              - Ultra-simple starter
  ✓ start-prod.sh         - Production starter

Supporting Scripts (existing):
  ✓ dev.sh                - Development runner
  ✓ prod.sh               - Production runner

Configuration:
  ✓ docker-compose.yml    - Docker orchestration
  ✓ Dockerfile.backend    - Backend container
  ✓ Dockerfile.frontend   - Frontend container
  ✓ Makefile              - Make commands

Documentation:
  ✓ RUN_APPLICATION.md    - This guide
  ✓ QUICK_START.md        - Quick reference
  ✓ DEPLOYMENT_METHODS.md - Detailed comparison


═════════════════════════════════════════════════════════════════════════════

💡 TIPS & TRICKS
─────────────────────────────────────────────────────────────────────────────

1. Run in background:
   $ nohup ./start.sh > app.log 2>&1 &

2. Monitor with separate logs:
   $ ./start.sh &
   $ make logs

3. Quick health check:
   $ ./run.sh --health

4. Switch to production:
   $ ./start-prod.sh

5. View specific logs:
   $ tail -f logs/backend.log
   $ tail -f logs/frontend.log

6. Port already in use:
   $ make stop
   $ ./start.sh


═════════════════════════════════════════════════════════════════════════════

✅ STATUS
─────────────────────────────────────────────────────────────────────────────

All runners are ready to use! Choose your preferred method and start:

    For most users:
    $ ./start.sh

    For developers:
    $ ./run.sh --help

    For production:
    $ ./start-prod.sh

    Or use Make:
    $ make dev


═════════════════════════════════════════════════════════════════════════════

May Allah bless this project and make it beneficial! 🤲

""")

if __name__ == "__main__":
    main()
