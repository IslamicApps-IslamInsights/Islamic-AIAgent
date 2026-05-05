#!/bin/bash

# 🌟 Noor Islamic AI Agent - Optimized Development Runner
# Modern concurrent execution with better logging and process management

set -e  # Exit on error

# ============================================================================
# CONFIGURATION
# ============================================================================

VENV_PATH="/Users/fahadiqbal/.islamic_ai_venv"
BACKEND_PORT=5010
FRONTEND_PORT=3001
LOG_DIR="logs"
PID_DIR=".pids"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

log_step() {
    echo -e "${BLUE}▸ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    if [ -f "$PID_DIR/backend.pid" ]; then
        kill $(cat "$PID_DIR/backend.pid") 2>/dev/null || true
        rm "$PID_DIR/backend.pid"
        log_success "Backend stopped"
    fi
    
    if [ -f "$PID_DIR/frontend.pid" ]; then
        kill $(cat "$PID_DIR/frontend.pid") 2>/dev/null || true
        rm "$PID_DIR/frontend.pid"
        log_success "Frontend stopped"
    fi
    
    # Kill any lingering processes on our ports
    lsof -t -i :$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -t -i :$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

trap cleanup EXIT INT TERM

check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found at $VENV_PATH"
        log_info "Run: python3 -m venv $VENV_PATH"
        exit 1
    fi
    log_success "Virtual environment found"
}

check_dependencies() {
    log_step "Checking dependencies..."
    
    "$VENV_PATH/bin/python3" -c "
import sys
required = ['flask', 'flask_cors', 'google.generativeai', 'chromadb']
missing = []
for pkg in required:
    try:
        __import__(pkg.replace('.', '_'))
    except ImportError:
        missing.append(pkg)
        
if missing:
    print('Missing packages: ' + ', '.join(missing))
    sys.exit(1)
" || {
        log_error "Missing dependencies. Run: pip install -r requirements.txt"
        exit 1
    }
    
    log_success "All dependencies installed"
}

start_backend() {
    log_step "Starting Backend API on port $BACKEND_PORT..."
    
    mkdir -p "$PID_DIR"
    
    nohup "$VENV_PATH/bin/python3" -u backend/api/web_api.py \
        --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
    
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    
    log_success "Backend started (PID: $BACKEND_PID)"
}

start_frontend() {
    log_step "Starting Frontend on port $FRONTEND_PORT..."
    
    mkdir -p "$PID_DIR"
    
    cd frontend
    nohup npm run dev -- --port "$FRONTEND_PORT" > "../$LOG_DIR/frontend.log" 2>&1 &
    cd ..
    
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    
    log_success "Frontend started (PID: $FRONTEND_PID)"
}

wait_for_health() {
    log_step "Waiting for services to initialize..."
    
    local max_retries=30
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        # Check backend health
        if curl -s "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
            log_success "Backend is ready"
            return 0
        fi
        
        retry=$((retry + 1))
        sleep 1
    done
    
    log_error "Services did not initialize within timeout"
    return 1
}

show_dashboard() {
    cat << EOF

${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}
${GREEN}║${NC}           🌟 Noor Islamic AI Agent - Ready! 🌟           ${GREEN}║${NC}
${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}
${GREEN}║${NC} ${BLUE}Frontend UI${NC}            → http://localhost:$FRONTEND_PORT
${GREEN}║${NC} ${BLUE}Backend API${NC}            → http://localhost:$BACKEND_PORT
${GREEN}║${NC} ${BLUE}Backend Health${NC}         → http://localhost:$BACKEND_PORT/api/health
${GREEN}║${NC} ${BLUE}Backend Logs${NC}           → $LOG_DIR/backend.log
${GREEN}║${NC} ${BLUE}Frontend Logs${NC}          → $LOG_DIR/frontend.log
${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}
${GREEN}║${NC} Press ${YELLOW}Ctrl+C${NC} to stop all services gracefully
${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}

EOF
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  🌟 Noor Islamic AI Agent - Development Server${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
    
    # Setup
    check_venv
    check_dependencies
    
    # Create directories
    mkdir -p "$LOG_DIR" "$PID_DIR"
    
    # Clean old logs
    > "$LOG_DIR/backend.log"
    > "$LOG_DIR/frontend.log"
    
    # Start services
    start_backend
    start_frontend
    
    # Wait for readiness
    if ! wait_for_health; then
        log_error "Services failed to initialize. Check logs:"
        log_info "Backend: tail -f $LOG_DIR/backend.log"
        log_info "Frontend: tail -f $LOG_DIR/frontend.log"
        exit 1
    fi
    
    # Show dashboard
    show_dashboard
    
    # Keep process running
    wait
}

# ============================================================================
# ENTRY POINT
# ============================================================================

main "$@"
