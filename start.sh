#!/bin/bash

# 🌟 Noor Islamic AI Agent - Ultra-Simple Runner
# Just type ./start.sh and everything works!
# No arguments needed, no configuration required

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

cat << EOF

${CYAN}════════════════════════════════════════════════════════════════${NC}
${GREEN}🌟 Noor Islamic AI Agent - Starting...${NC}
${CYAN}════════════════════════════════════════════════════════════════${NC}

EOF

# For development (hot reload)
if [ "$1" = "prod" ]; then
    exec "$SCRIPT_DIR/run.sh" --prod
else
    exec "$SCRIPT_DIR/run.sh"
fi
