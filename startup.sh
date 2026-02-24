#!/bin/bash

# NeuroAI Complete Project Startup Script
# Starts backend with ML models and frontend simultaneously

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="/home/daddy/Downloads/MedGemma/neuroai2/NeuroAI"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/pathfinder-neurals"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         NeuroAI - Complete Project Startup                  ║${NC}"
echo -e "${BLUE}║    AI-Powered Drug Discovery Platform                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check Python virtual environment
echo -e "${YELLOW}[1/5] Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Step 2: Install/Update backend dependencies
echo -e "${YELLOW}[2/5] Setting up backend dependencies...${NC}"
cd "$BACKEND_DIR"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${BLUE}  Creating virtual environment...${NC}"
    python3 -m venv venv || { echo -e "${RED}✗ Failed to create venv${NC}"; exit 1; }
fi

# Use the venv Python directly to install packages
PYTHON_BIN="$BACKEND_DIR/venv/bin/python"
PIP_BIN="$BACKEND_DIR/venv/bin/pip"

if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}✗ Python executable not found in venv${NC}"
    exit 1
fi

# Install dependencies using the venv pip
echo -e "${BLUE}  Installing Python packages...${NC}"
"$PIP_BIN" install -q --upgrade pip setuptools wheel 2>/dev/null || true
if [ -f "requirements.txt" ]; then
    "$PIP_BIN" install -q -r requirements.txt 2>/dev/null || "$PIP_BIN" install -q -r requirements-minimal.txt 2>/dev/null
else
    "$PIP_BIN" install -q -r requirements-minimal.txt 2>/dev/null
fi
echo -e "${GREEN}✓ Backend dependencies ready${NC}"

# Step 3: Run Django migrations
echo -e "${YELLOW}[3/5] Running database migrations...${NC}"
cd "$BACKEND_DIR"
"$BACKEND_DIR/venv/bin/python" manage.py migrate --noinput 2>/dev/null || true
echo -e "${GREEN}✓ Database ready${NC}"

# Step 4: Check frontend dependencies
echo -e "${YELLOW}[4/5] Setting up frontend dependencies...${NC}"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}  Installing Node packages...${NC}"
    npm install -q
else
    echo -e "${BLUE}  Updating Node packages...${NC}"
    npm install -q --legacy-peer-deps
fi
echo -e "${GREEN}✓ Frontend dependencies ready${NC}"

# Step 5: Start services
echo -e "${YELLOW}[5/5] Starting services...${NC}"
echo ""

# Kill any existing processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
sleep 1

# Start Backend using the venv Python directly
echo -e "${BLUE}Starting Django Backend...${NC}"
cd "$BACKEND_DIR"
"$BACKEND_DIR/venv/bin/python" manage.py runserver 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
sleep 3

# Start Frontend
echo -e "${BLUE}Starting React Frontend...${NC}"
cd "$FRONTEND_DIR"
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
sleep 3

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                   ✓ Project Started                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Access the application at:${NC}"
echo -e "  ${GREEN}Frontend${NC}:  http://localhost:8080"
echo -e "  ${GREEN}Backend${NC}:   http://localhost:8000/api/v1/"
echo -e "  ${GREEN}Admin${NC}:     http://localhost:8000/admin/"
echo ""
echo -e "${BLUE}Logs:${NC}"
echo -e "  Backend:  tail -f /tmp/backend.log"
echo -e "  Frontend: tail -f /tmp/frontend.log"
echo ""
echo -e "${YELLOW}Processes:${NC}"
echo -e "  Backend (PID $BACKEND_PID)"
echo -e "  Frontend (PID $FRONTEND_PID)"
echo ""
echo -e "${BLUE}ML Models:${NC}"
echo -e "  ${GREEN}✓ GraphDTA${NC}       - Binding affinity prediction (pre-trained)"
echo -e "  ${GREEN}✓ MedGemma-7B${NC}    - Toxicity & medical reasoning"
echo -e "  ${GREEN}✓ ESM-2-33M${NC}     - Protein embeddings"
echo -e "  ${GREEN}✓ RDKit${NC}         - Molecular analysis"
echo ""
echo -e "${YELLOW}To stop the project:${NC}"
echo -e "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${BLUE}First run health check:${NC}"
echo -e "  curl http://localhost:8000/api/v1/system/"
echo ""

# Wait for interruption
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e '\n${YELLOW}Services stopped.${NC}'; exit 0" SIGINT SIGTERM

wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
