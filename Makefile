# 🌟 Noor Islamic AI Agent - Development & Deployment Makefile

.PHONY: help dev prod test install clean logs monitor stop

# Variables
VENV_PATH := /Users/fahadiqbal/.islamic_ai_venv
PYTHON := $(VENV_PATH)/bin/python3
PIP := $(VENV_PATH)/bin/pip
NODE := node
NPM := npm

# Colors
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║$(NC)        🌟 Noor Islamic AI Agent - Development Commands        $(BLUE)║$(NC)"
	@echo "$(BLUE)╠════════════════════════════════════════════════════════════════╣$(NC)"
	@echo "$(BLUE)║$(NC) $(YELLOW)Development$(NC)"
	@echo "$(BLUE)║$(NC)   make dev              - Start development server"
	@echo "$(BLUE)║$(NC)   make dev-backend      - Start only backend"
	@echo "$(BLUE)║$(NC)   make dev-frontend     - Start only frontend"
	@echo "$(BLUE)║$(NC)"
	@echo "$(BLUE)║$(NC) $(YELLOW)Production$(NC)"
	@echo "$(BLUE)║$(NC)   make prod             - Start production server"
	@echo "$(BLUE)║$(NC)   make build            - Build production assets"
	@echo "$(BLUE)║$(NC)"
	@echo "$(BLUE)║$(NC) $(YELLOW)Utilities$(NC)"
	@echo "$(BLUE)║$(NC)   make install          - Install dependencies"
	@echo "$(BLUE)║$(NC)   make test             - Run tests"
	@echo "$(BLUE)║$(NC)   make clean            - Clean up artifacts"
	@echo "$(BLUE)║$(NC)   make logs             - Show live logs"
	@echo "$(BLUE)║$(NC)   make monitor          - Monitor services"
	@echo "$(BLUE)║$(NC)   make stop             - Stop all services"
	@echo "$(BLUE)╚════════════════════════════════════════════════════════════════╝$(NC)"

# ============================================================================
# DEVELOPMENT TARGETS
# ============================================================================

dev: check-venv
	@echo "$(GREEN)Starting development server...$(NC)"
	@chmod +x dev.sh
	@./dev.sh

dev-backend: check-venv
	@echo "$(GREEN)Starting backend only...$(NC)"
	@$(PYTHON) -u backend/api/web_api.py

dev-frontend:
	@echo "$(GREEN)Starting frontend only...$(NC)"
	@cd frontend && npm run dev -- --port 3001

# ============================================================================
# PRODUCTION TARGETS
# ============================================================================

prod: check-venv build
	@echo "$(GREEN)Starting production server...$(NC)"
	@chmod +x prod.sh
	@ENVIRONMENT=production ./prod.sh

build: check-venv
	@echo "$(GREEN)Building frontend assets...$(NC)"
	@cd frontend && npm run build
	@echo "$(GREEN)Build complete!$(NC)"

# ============================================================================
# INSTALLATION & SETUP
# ============================================================================

install: install-backend install-frontend

install-backend: check-venv
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	@$(PIP) install -r requirements.txt

install-frontend:
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	@cd frontend && npm install

# ============================================================================
# UTILITIES
# ============================================================================

check-venv:
	@if [ ! -d "$(VENV_PATH)" ]; then \
		echo "$(YELLOW)Virtual environment not found at $(VENV_PATH)$(NC)"; \
		echo "Creating it now..."; \
		python3 -m venv $(VENV_PATH); \
		$(PIP) install --upgrade pip uv; \
		echo "$(GREEN)Virtual environment created!$(NC)"; \
	fi

test:
	@echo "$(GREEN)Running tests...$(NC)"
	@$(PYTHON) -m pytest scripts/test_*.py -v

clean:
	@echo "$(GREEN)Cleaning up artifacts...$(NC)"
	@rm -rf __pycache__ .pytest_cache .coverage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@cd frontend && npm run clean 2>/dev/null || true
	@rm -rf logs/*.log
	@echo "$(GREEN)Cleanup complete!$(NC)"

logs:
	@echo "$(BLUE)Backend logs:$(NC)"
	@tail -f logs/backend.log & \
	echo "$(BLUE)Frontend logs:$(NC)" && \
	tail -f logs/frontend.log

monitor:
	@watch -n 1 'echo "=== Backend (Port 5010) ===" && lsof -i :5010 2>/dev/null || echo "Not running"; echo ""; echo "=== Frontend (Port 3001) ===" && lsof -i :3001 2>/dev/null || echo "Not running"'

stop:
	@echo "$(YELLOW)Stopping all services...$(NC)"
	@lsof -t -i :5010 2>/dev/null | xargs kill -9 2>/dev/null || true
	@lsof -t -i :3001 2>/dev/null | xargs kill -9 2>/dev/null || true
	@pkill -f "python.*web_api.py" 2>/dev/null || true
	@pkill -f "vite" 2>/dev/null || true
	@pkill -f "npm.*dev" 2>/dev/null || true
	@echo "$(GREEN)Services stopped!$(NC)"

# ============================================================================
# DOCKER TARGETS (Optional)
# ============================================================================

docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	@docker build -t islamic-ai-agent:latest .

docker-run:
	@echo "$(GREEN)Running in Docker...$(NC)"
	@docker run -p 5010:5010 -p 3001:3001 islamic-ai-agent:latest

# ============================================================================
# DIAGNOSTICS
# ============================================================================

health-check:
	@echo "$(BLUE)Checking backend health...$(NC)"
	@curl -s http://localhost:5010/api/health | $(PYTHON) -m json.tool || echo "Backend not responding"
	@echo ""
	@echo "$(BLUE)Checking frontend...$(NC)"
	@curl -s http://localhost:3001 | head -20 || echo "Frontend not responding"

ps:
	@echo "$(BLUE)Running processes:$(NC)"
	@ps aux | grep -E "(python.*web_api|node.*vite|npm)" | grep -v grep || echo "No services running"

# ============================================================================
# DEFAULTS
# ============================================================================

.DEFAULT_GOAL := help
