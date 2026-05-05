#!/bin/bash

# 🌟 Noor Islamic AI Agent - Production Runner
# Optimized for deployment with health checks, graceful shutdown, and monitoring

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

VENV_PATH="${VENV_PATH:-.venv}"
BACKEND_PORT="${BACKEND_PORT:=5010}"
FRONTEND_PORT="${FRONTEND_PORT:=3001}"
WORKERS="${WORKERS:=4}"
LOG_DIR="logs"
PID_DIR=".pids"
ENVIRONMENT="${ENVIRONMENT:=production}"

# Colors (disabled in production)
if [ "$ENVIRONMENT" = "production" ]; then
    GREEN=''
    BLUE=''
    RED=''
    YELLOW=''
    NC=''
else
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
fi

# ============================================================================
# LOGGING
# ============================================================================

log_step() { echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ▸ $1${NC}" | tee -a "$LOG_DIR/app.log"; }
log_success() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $1${NC}" | tee -a "$LOG_DIR/app.log"; }
log_error() { echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $1${NC}" | tee -a "$LOG_DIR/app.log"; }
log_info() { echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ $1${NC}" | tee -a "$LOG_DIR/app.log"; }

# ============================================================================
# CLEANUP
# ============================================================================

cleanup() {
    log_step "Initiating graceful shutdown..."
    
    # Kill processes gracefully
    if [ -f "$PID_DIR/backend.pid" ]; then
        kill -TERM $(cat "$PID_DIR/backend.pid") 2>/dev/null || true
        sleep 2
        kill -9 $(cat "$PID_DIR/backend.pid") 2>/dev/null || true
        rm "$PID_DIR/backend.pid"
    fi
    
    if [ -f "$PID_DIR/frontend.pid" ]; then
        kill -TERM $(cat "$PID_DIR/frontend.pid") 2>/dev/null || true
        sleep 2
        kill -9 $(cat "$PID_DIR/frontend.pid") 2>/dev/null || true
        rm "$PID_DIR/frontend.pid"
    fi
    
    log_success "Shutdown complete"
    exit 0
}

trap cleanup SIGTERM SIGINT

# ============================================================================
# HEALTH MONITORING
# ============================================================================

check_process_health() {
    local pid=$1
    local name=$2
    
    if ! kill -0 $pid 2>/dev/null; then
        log_error "$name process (PID $pid) is not running"
        return 1
    fi
    return 0
}

monitor_processes() {
    while true; do
        if [ -f "$PID_DIR/backend.pid" ]; then
            if ! check_process_health $(cat "$PID_DIR/backend.pid") "Backend"; then
                log_error "Backend has crashed, attempting restart..."
                start_backend
            fi
        fi
        
        if [ -f "$PID_DIR/frontend.pid" ]; then
            if ! check_process_health $(cat "$PID_DIR/frontend.pid") "Frontend"; then
                log_error "Frontend has crashed, attempting restart..."
                start_frontend
            fi
        fi
        
        sleep 10
    done
}

# ============================================================================
# SERVICE STARTUP
# ============================================================================

start_backend() {
    log_step "Starting Backend API (Workers: $WORKERS)..."
    
    mkdir -p "$PID_DIR"
    
    # Use gunicorn for production (if available), fallback to Flask
    if "$VENV_PATH/bin/python3" -c "import gunicorn" 2>/dev/null; then
        nohup "$VENV_PATH/bin/gunicorn" \
            --workers "$WORKERS" \
            --threads 4 \
            --bind "127.0.0.1:$BACKEND_PORT" \
            --timeout 120 \
            --access-logfile "$LOG_DIR/backend_access.log" \
            --error-logfile "$LOG_DIR/backend_error.log" \
            "backend.api.web_api:app" > "$LOG_DIR/backend.log" 2>&1 &
    else
        nohup "$VENV_PATH/bin/python3" -u backend/api/web_api.py \
            --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
    fi
    
    local pid=$!
    echo $pid > "$PID_DIR/backend.pid"
    log_success "Backend started (PID: $pid)"
}

start_frontend() {
    log_step "Starting Frontend (Production Build)..."
    
    mkdir -p "$PID_DIR"
    
    cd frontend
    
    # Build if not already built
    if [ ! -d "dist" ]; then
        npm run build > "../$LOG_DIR/frontend_build.log" 2>&1
    fi
    
    # Serve with a simple HTTP server
    nohup npx serve -s dist -l "$FRONTEND_PORT" > "../$LOG_DIR/frontend.log" 2>&1 &
    
    cd ..
    
    local pid=$!
    echo $pid > "$PID_DIR/frontend.pid"
    log_success "Frontend started (PID: $pid)"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo "Starting Noor Islamic AI Agent - $ENVIRONMENT mode"
    
    mkdir -p "$LOG_DIR" "$PID_DIR"
    
    # Start services
    start_backend
    start_frontend
    
    log_success "All services started"
    
    # Monitor processes
    monitor_processes
}

main "$@"
