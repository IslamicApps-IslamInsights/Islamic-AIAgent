#!/bin/bash

# 🌟 Noor Islamic AI Agent - Production Starter
# Type: ./start-prod.sh
# Everything is optimized and ready for deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
NC='\033[0m'

cat << EOF

${CYAN}════════════════════════════════════════════════════════════════${NC}
${GREEN}🚀 Noor Islamic AI Agent - Production Mode${NC}
${CYAN}════════════════════════════════════════════════════════════════${NC}

EOF

exec "$SCRIPT_DIR/run.sh" --prod
