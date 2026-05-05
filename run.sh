#!/bin/bash

# 🌟 Noor Islamic AI Agent - Master Application Runner
# Ultimate unified script to run the entire application
# Auto-detects environment and uses optimal configuration

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Auto-detect venv
if [ -d "$SCRIPT_DIR/.venv" ]; then
    VENV_PATH="$SCRIPT_DIR/.venv"
elif [ -d "/Users/fahadiqbal/.islamic_ai_venv" ]; then
    VENV_PATH="/Users/fahadiqbal/.islamic_ai_venv"
else
    VENV_PATH="$SCRIPT_DIR/.venv"
fi

BACKEND_PORT=5010
FRONTEND_PORT=3001
LLM_PORT=8080
LOG_DIR="${SCRIPT_DIR}/logs"
PID_DIR="${SCRIPT_DIR}/.pids"

DEFAULT_MODEL_PATH="$SCRIPT_DIR/backend/models/qwen2.5-7b-ins-v3-Q4_K_M.gguf"
DEFAULT_MODEL_URL="https://huggingface.co/bartowski/qwen2.5-7b-ins-v3-GGUF/resolve/main/qwen2.5-7b-ins-v3-Q4_K_M.gguf?download=true"
AUTO_SETUP="${AUTO_SETUP:-1}"
AUTO_DOWNLOAD_LLM_MODEL="${AUTO_DOWNLOAD_LLM_MODEL:-1}"
AUTO_INSTALL_LLAMA_CPP="${AUTO_INSTALL_LLAMA_CPP:-1}"
AUTO_INGEST_RAG="${AUTO_INGEST_RAG:-1}"
AUTO_INITIALIZE_AGENTS="${AUTO_INITIALIZE_AGENTS:-1}"
RAG_MIN_DOCS="${RAG_MIN_DOCS:-1000}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

log() { echo -e "${BLUE}▸ $1${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ $1${NC}"; }

ensure_llama_cpp() {
    if command -v llama-server &> /dev/null; then
        return 0
    fi
    if [ "${AUTO_INSTALL_LLAMA_CPP}" != "1" ]; then
        return 1
    fi
    if ! command -v brew &> /dev/null; then
        return 1
    fi
    log "Installing llama.cpp (required for local LLM server)..."
    brew install llama.cpp > /dev/null 2>&1 || return 1
    command -v llama-server &> /dev/null
}

ensure_llm_model() {
    local model_path="${LOCAL_LLM_MODEL_PATH:-$DEFAULT_MODEL_PATH}"
    local model_url="${LOCAL_LLM_MODEL_URL:-$DEFAULT_MODEL_URL}"

    mkdir -p "$(dirname "$model_path")"

    if [ -f "$model_path" ]; then
        return 0
    fi
    if [ "${AUTO_DOWNLOAD_LLM_MODEL}" != "1" ]; then
        info "Local LLM model not found. Set LOCAL_LLM_MODEL_PATH or place a GGUF at: $model_path"
        return 1
    fi
    if ! command -v curl &> /dev/null; then
        info "curl not found. Please install curl or download the model manually to: $model_path"
        return 1
    fi

    log "Downloading local LLM model (GGUF) to backend/models/ (this is a large file)..."
    local tmp_path="${model_path}.part"
    curl -L --fail --retry 5 --retry-delay 2 -C - -o "$tmp_path" "$model_url" || {
        error "Model download failed"
        info "You can resume by re-running ./run.sh (curl will continue) or set LOCAL_LLM_MODEL_URL"
        return 1
    }
    mv "$tmp_path" "$model_path"
    success "Model downloaded: $(basename "$model_path")"
    return 0
}

check_rag_ready() {
    "$VENV_PATH/bin/python3" - <<PY
from backend.utils.enhanced_hybrid_rag import check_rag_system
st = check_rag_system()
ready = bool(st.get("ready"))
bm25 = int(st.get("bm25_docs") or 0)
chroma = int(st.get("chromadb_docs") or 0)
min_docs = int("${RAG_MIN_DOCS}")
if ready and (bm25 + chroma) >= min_docs:
    raise SystemExit(0)
raise SystemExit(1)
PY
}

ensure_rag_ingested() {
    if [ "${AUTO_INGEST_RAG}" != "1" ]; then
        return 0
    fi

    if check_rag_ready; then
        return 0
    fi

    log "RAG ingestion not ready. Running full ingestion (first-time setup)..."
    export INGEST_BATCH_SIZE="${INGEST_BATCH_SIZE:-64}"
    export INGEST_EMBED_BATCH_SIZE="${INGEST_EMBED_BATCH_SIZE:-16}"
    export INGEST_DEVICE="${INGEST_DEVICE:-cpu}"

    "$VENV_PATH/bin/python3" backend/knowledge/full_data_ingestion.py || {
        error "RAG ingestion failed"
        info "Check logs above and retry. You can also reduce memory with: INGEST_BATCH_SIZE=32 INGEST_EMBED_BATCH_SIZE=8"
        exit 1
    }
    success "RAG ingestion completed"
}

initialize_agents() {
    if [ "${AUTO_INITIALIZE_AGENTS}" != "1" ]; then
        return 0
    fi

    local url="http://localhost:$BACKEND_PORT/api/initialize"
    log "Initializing agent system (post-start bootstrap)..."
    local max_retries=20
    local retry=0
    while [ $retry -lt $max_retries ]; do
        if curl -s -X POST "$url" -H "Content-Type: application/json" > /dev/null 2>&1; then
            success "Agent initialization triggered"
            return 0
        fi
        retry=$((retry + 1))
        sleep 1
    done
    info "Agent initialization endpoint did not respond (continuing anyway)"
    return 0
}

cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    
    # Kill local LLM
    if [ -f "$PID_DIR/llm.pid" ]; then
        kill $(cat "$PID_DIR/llm.pid") 2>/dev/null || true
        rm -f "$PID_DIR/llm.pid"
    fi

    # Kill backend
    if [ -f "$PID_DIR/backend.pid" ]; then
        kill $(cat "$PID_DIR/backend.pid") 2>/dev/null || true
        rm -f "$PID_DIR/backend.pid"
    fi
    
    # Kill frontend
    if [ -f "$PID_DIR/frontend.pid" ]; then
        kill $(cat "$PID_DIR/frontend.pid") 2>/dev/null || true
        rm -f "$PID_DIR/frontend.pid"
    fi
    
    # Kill remaining processes on ports
    lsof -t -i :$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -t -i :$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -t -i :$LLM_PORT 2>/dev/null | xargs kill -9 2>/dev/null || true
    
    success "Services stopped"
    exit 0
}

trap cleanup EXIT INT TERM

# Detect mode
detect_mode() {
    # Check for --prod flag or ENVIRONMENT variable
    if [ "$1" = "--prod" ] || [ "$ENVIRONMENT" = "production" ]; then
        echo "production"
    else
        echo "development"
    fi
}

# Check prerequisites
check_setup() {
    log "Checking prerequisites..."

    # Prefer Python >= 3.10 for modern deps
    local py_bin="${PYTHON_BIN:-python3}"
    local py_ver
    py_ver="$($py_bin -c 'import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")' 2>/dev/null || echo "")"

    if [ -z "$py_ver" ]; then
        py_bin="python3"
        py_ver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")"
    fi

    if [ -n "$py_ver" ]; then
        local major="${py_ver%.*}"
        local minor="${py_ver#*.}"
        if [ "$major" -lt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -lt 10 ]; }; then
            if command -v python3.11 &> /dev/null; then
                py_bin="python3.11"
            elif command -v python3.12 &> /dev/null; then
                py_bin="python3.12"
            elif command -v python3.10 &> /dev/null; then
                py_bin="python3.10"
            elif [ "$AUTO_SETUP" = "1" ] && command -v brew &> /dev/null; then
                log "Installing Python 3.11 (recommended for this project)..."
                brew install python@3.11 > /dev/null 2>&1 || true
                if command -v python3.11 &> /dev/null; then
                    py_bin="python3.11"
                fi
            fi
        fi
    fi

    local chosen_ver
    chosen_ver="$($py_bin -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")"
    if [ -n "$chosen_ver" ]; then
        local cmaj="${chosen_ver%.*}"
        local cmin="${chosen_ver#*.}"
        if [ "$cmaj" -lt 3 ] || { [ "$cmaj" -eq 3 ] && [ "$cmin" -lt 10 ]; }; then
            error "Python >= 3.10 is required (found: $chosen_ver)"
            info "Install Python 3.11 (recommended): brew install python@3.11"
            info "Or set PYTHON_BIN to a Python 3.10+ binary path/name"
            exit 1
        fi
    fi
    
    # Check venv
    if [ ! -d "$VENV_PATH" ]; then
        info "Virtual environment not found. Creating at $VENV_PATH"
        "$py_bin" -m venv "$VENV_PATH" || {
            error "Failed to create virtual environment at $VENV_PATH"
            exit 1
        }
        "$VENV_PATH/bin/python3" -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1 || true
        log "Installing Python dependencies..."
        "$VENV_PATH/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" || {
            error "Python dependencies installation failed"
            info "Try manually: $VENV_PATH/bin/pip install -r requirements.txt"
            exit 1
        }
    else
        if [ "$AUTO_SETUP" = "1" ]; then
            local venv_ver
            venv_ver="$("$VENV_PATH/bin/python3" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")"
            if [ -n "$venv_ver" ]; then
                local vmaj="${venv_ver%.*}"
                local vmin="${venv_ver#*.}"
                if [ "$vmaj" -lt 3 ] || { [ "$vmaj" -eq 3 ] && [ "$vmin" -lt 10 ]; }; then
                    info "Existing venv uses Python $venv_ver (too old). Recreating venv with $chosen_ver..."
                    mv "$VENV_PATH" "${VENV_PATH}_backup_py${venv_ver//./}" 2>/dev/null || rm -rf "$VENV_PATH"
                    "$py_bin" -m venv "$VENV_PATH" || {
                        error "Failed to recreate virtual environment at $VENV_PATH"
                        exit 1
                    }
                    "$VENV_PATH/bin/python3" -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1 || true
                    log "Installing Python dependencies..."
                    "$VENV_PATH/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" || {
                        error "Python dependencies installation failed"
                        info "Try manually: $VENV_PATH/bin/pip install -r requirements.txt"
                        exit 1
                    }
                fi
            fi
        fi
    fi
    
    # Check Python dependencies
    "$VENV_PATH/bin/python3" -c "
import sys
required = [
    ('flask', 'flask'),
    ('flask_cors', 'flask_cors'),
    ('chromadb', 'chromadb')
]
missing = []
for pkg_name, import_name in required:
    try:
        __import__(import_name)
    except ImportError:
        missing.append(pkg_name)
if missing:
    print('Missing: ' + ', '.join(missing))
    sys.exit(1)
" || {
        info "Missing Python dependencies. Installing..."
        "$VENV_PATH/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" || {
            error "Python dependencies installation failed"
            info "Try manually: $VENV_PATH/bin/pip install -r requirements.txt"
            exit 1
        }
    }
    
    # Check Node/npm
    if ! command -v npm &> /dev/null; then
        error "Node.js/npm not found"
        info "Install Node.js from https://nodejs.org"
        exit 1
    fi
    
    # Check frontend dependencies
    if [ ! -d "frontend/node_modules" ]; then
        log "Installing frontend dependencies..."
        cd frontend && npm install > /dev/null 2>&1 && cd ..
    fi
    
    success "All prerequisites met"
}

# ============================================================================
# DEVELOPMENT MODE
# ============================================================================

run_development() {
    log "Starting in DEVELOPMENT mode (Hot reload enabled)"
    log "Clearing previous sessions..."
    
    mkdir -p "$LOG_DIR" "$PID_DIR"
    > "$LOG_DIR/backend.log"
    > "$LOG_DIR/frontend.log"
    > "$LOG_DIR/llm.log"

    if [ "$AUTO_SETUP" = "1" ]; then
        ensure_llm_model || true
        ensure_rag_ingested
    fi

    # Start local LLM (llama.cpp)
    local model_path="${LOCAL_LLM_MODEL_PATH:-$DEFAULT_MODEL_PATH}"
    if [ -f "$model_path" ] && (command -v llama-server &> /dev/null || ensure_llama_cpp); then
        log "Starting Local LLM (llama.cpp) on port $LLM_PORT..."
        export LOCAL_LLM_BACKEND="llama_cpp_server"
        export LOCAL_LLM_MODEL_PATH="$model_path"
        export LLAMA_CPP_SERVER_URL="http://localhost:$LLM_PORT"
        export LOCAL_LLM_MAX_TOKENS="${LOCAL_LLM_MAX_TOKENS:-700}"
        export LOCAL_LLM_TEMPERATURE="${LOCAL_LLM_TEMPERATURE:-0.4}"

        nohup llama-server -m "$model_path" --host 0.0.0.0 --port "$LLM_PORT" --ctx-size 4096 > "$LOG_DIR/llm.log" 2>&1 &
        LLM_PID=$!
        echo $LLM_PID > "$PID_DIR/llm.pid"
        success "Local LLM started (PID: $LLM_PID)"
    else
        info "Local LLM not started (model missing or llama-server not installed)"
        info "Model expected at: $model_path"
        info "Install llama.cpp: brew install llama.cpp"
    fi
    
    # Start backend
    log "Starting Backend API on port $BACKEND_PORT..."
    nohup "$VENV_PATH/bin/python3" -u backend/api/web_api.py \
        --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    success "Backend started (PID: $BACKEND_PID)"
    
    # Start frontend
    log "Starting Frontend on port $FRONTEND_PORT..."
    cd frontend
    nohup npm run dev -- --port "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
    cd ..
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    success "Frontend started (PID: $FRONTEND_PID)"
    
    # Wait for health
    log "Waiting for services to initialize..."
    local max_retries=30
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        if curl -s "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
            success "Backend is ready"
            break
        fi
        retry=$((retry + 1))
        sleep 1
    done

    initialize_agents
    
    show_dashboard "development"
}

# ============================================================================
# PRODUCTION MODE
# ============================================================================

run_production() {
    log "Starting in PRODUCTION mode (Optimized)"
    
    mkdir -p "$LOG_DIR" "$PID_DIR"
    > "$LOG_DIR/backend.log"
    > "$LOG_DIR/frontend.log"
    > "$LOG_DIR/llm.log"

    if [ "$AUTO_SETUP" = "1" ]; then
        ensure_llm_model || true
        ensure_rag_ingested
    fi

    # Start local LLM (llama.cpp)
    local model_path="${LOCAL_LLM_MODEL_PATH:-$DEFAULT_MODEL_PATH}"
    if [ -f "$model_path" ] && (command -v llama-server &> /dev/null || ensure_llama_cpp); then
        log "Starting Local LLM (llama.cpp) on port $LLM_PORT..."
        export LOCAL_LLM_BACKEND="llama_cpp_server"
        export LOCAL_LLM_MODEL_PATH="$model_path"
        export LLAMA_CPP_SERVER_URL="http://localhost:$LLM_PORT"
        export LOCAL_LLM_MAX_TOKENS="${LOCAL_LLM_MAX_TOKENS:-700}"
        export LOCAL_LLM_TEMPERATURE="${LOCAL_LLM_TEMPERATURE:-0.4}"

        nohup llama-server -m "$model_path" --host 0.0.0.0 --port "$LLM_PORT" --ctx-size 4096 > "$LOG_DIR/llm.log" 2>&1 &
        LLM_PID=$!
        echo $LLM_PID > "$PID_DIR/llm.pid"
        success "Local LLM started (PID: $LLM_PID)"
    else
        info "Local LLM not started (model missing or llama-server not installed)"
    fi
    
    # Build frontend
    log "Building frontend for production..."
    cd frontend
    npm run build > /dev/null 2>&1
    cd ..
    success "Frontend built"
    
    # Start backend with Gunicorn if available
    log "Starting Backend API (4 workers)..."
    if "$VENV_PATH/bin/python3" -c "import gunicorn" 2>/dev/null; then
        nohup "$VENV_PATH/bin/gunicorn" \
            --workers 4 --threads 4 --bind "127.0.0.1:$BACKEND_PORT" \
            --timeout 120 --access-logfile "$LOG_DIR/backend_access.log" \
            "backend.api.web_api:app" > "$LOG_DIR/backend.log" 2>&1 &
    else
        nohup "$VENV_PATH/bin/python3" -u backend/api/web_api.py \
            --port "$BACKEND_PORT" > "$LOG_DIR/backend.log" 2>&1 &
    fi
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    success "Backend started (PID: $BACKEND_PID)"
    
    # Start frontend with serve
    log "Starting Frontend..."
    cd frontend
    if ! command -v serve &> /dev/null; then
        npm install -g serve > /dev/null 2>&1
    fi
    nohup serve -s dist -l "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 &
    cd ..
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    success "Frontend started (PID: $FRONTEND_PID)"
    
    # Wait for health
    log "Waiting for services to initialize..."
    local max_retries=30
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        if curl -s "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
            success "Backend is ready"
            break
        fi
        retry=$((retry + 1))
        sleep 1
    done

    initialize_agents
    
    show_dashboard "production"
}

# ============================================================================
# DASHBOARD
# ============================================================================

show_dashboard() {
    local mode=$1
    
    cat << EOF

${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}
${GREEN}║${NC}          🌟 Noor Islamic AI Agent - Running 🌟              ${GREEN}║${NC}
${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}
${GREEN}║${NC} Mode:  $(printf "%-50s" "$mode") ${GREEN}║${NC}
${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}
${GREEN}║${NC}
${GREEN}║${NC}  ${CYAN}Frontend${NC}     http://localhost:$FRONTEND_PORT
${GREEN}║${NC}  ${CYAN}Backend${NC}      http://localhost:$BACKEND_PORT
${GREEN}║${NC}  ${CYAN}Local LLM${NC}    http://localhost:$LLM_PORT
${GREEN}║${NC}  ${CYAN}Health${NC}       http://localhost:$BACKEND_PORT/api/health
${GREEN}║${NC}
${GREEN}║${NC}  ${CYAN}Frontend Log${NC}  tail -f $LOG_DIR/frontend.log
${GREEN}║${NC}  ${CYAN}Backend Log${NC}   tail -f $LOG_DIR/backend.log
${GREEN}║${NC}  ${CYAN}LLM Log${NC}       tail -f $LOG_DIR/llm.log
${GREEN}║${NC}
${GREEN}╠════════════════════════════════════════════════════════════════╣${NC}
${GREEN}║${NC}  Press ${YELLOW}Ctrl+C${NC} to stop all services
${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}

EOF
}

# ============================================================================
# SHOW HELP
# ============================================================================

show_help() {
    cat << EOF

${CYAN}🌟 Noor Islamic AI Agent - Master Runner${NC}

${BLUE}USAGE:${NC}
  ./run.sh [OPTIONS]

${BLUE}OPTIONS:${NC}
  (none)           Start in DEVELOPMENT mode (hot reload, default)
  --prod           Start in PRODUCTION mode (optimized, multi-worker)
  --help           Show this help message
  --health         Check service health only
  --version        Show version

${BLUE}EXAMPLES:${NC}
  ./run.sh                    # Development mode
  ./run.sh --prod             # Production mode
  ENVIRONMENT=production ./run.sh  # Production mode (env var)

${BLUE}FEATURES:${NC}
  Development:
    • Hot reload on file changes
    • Concurrent execution
    • Live logs to console
    • Auto health checks

  Production:
    • Multi-worker processes (Gunicorn)
    • Optimized builds
    • Health monitoring
    • Process management

${BLUE}SHORTCUTS:${NC}
  Using Make (if Makefile exists):
    make dev              # Development
    make prod             # Production
    make logs             # View logs
    make stop             # Stop services

${BLUE}LOGGING:${NC}
  Logs are saved to: $LOG_DIR/
  • backend.log       - Backend server logs
  • frontend.log      - Frontend server logs
  • backend_access.log - Backend access logs (production)

EOF
}

# ============================================================================
# HEALTH CHECK
# ============================================================================

health_check() {
    echo ""
    log "Checking service health..."
    echo ""
    
    # Backend health
    if curl -s "http://localhost:$BACKEND_PORT/api/health" > /dev/null 2>&1; then
        success "Backend API (port $BACKEND_PORT) - ONLINE"
    else
        error "Backend API (port $BACKEND_PORT) - OFFLINE"
    fi
    
    # Frontend health
    if curl -s "http://localhost:$FRONTEND_PORT" > /dev/null 2>&1; then
        success "Frontend (port $FRONTEND_PORT) - ONLINE"
    else
        error "Frontend (port $FRONTEND_PORT) - OFFLINE"
    fi
    
    echo ""
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    # Parse arguments
    case "${1:-}" in
        --help)
            show_help
            exit 0
            ;;
        --version)
            echo "Noor Islamic AI Agent - v1.0.0"
            exit 0
            ;;
        --health)
            health_check
            exit 0
            ;;
        *)
            ;;
    esac
    
    # Banner
    cat << EOF

${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}
${CYAN}║${NC}         🌟 Noor Islamic AI Agent - Master Runner 🌟         ${CYAN}║${NC}
${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}

EOF
    
    # Check setup
    check_setup
    
    # Detect mode
    MODE=$(detect_mode "$1")
    
    # Run application
    if [ "$MODE" = "production" ]; then
        run_production
    else
        run_development
    fi
    
    # Keep running
    while true; do
        sleep 1
    done
}

# ============================================================================
# ENTRY POINT
# ============================================================================

main "$@"
