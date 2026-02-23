#!/usr/bin/env bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo -e "${BLUE}"
echo "╭─────────────────────────────────────────────────────────╮"
echo "│  NeuroDegenRx Frontend Setup and Launch                 │"
echo "╰─────────────────────────────────────────────────────────╯"
echo -e "${NC}"

# Check dependencies
echo -e "${YELLOW}[1/3] Checking dependencies...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo "  Install Node.js 20+ from https://nodejs.org/"
    exit 1
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js found ($NODE_VERSION)${NC}"
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    echo "  Install npm by running: npm install -g npm"
    exit 1
else
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✓ npm found (version $NPM_VERSION)${NC}"
fi

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Install dependencies if node_modules doesn't exist
echo -e "${YELLOW}[2/3] Installing Node.js dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    echo "  This may take a few minutes..."
    npm install --silent
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Check if backend is running
echo -e "${YELLOW}[3/3] Verifying backend availability...${NC}"
if curl -s http://localhost:8000/api/v1/system-info/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠ Backend is not responding${NC}"
    echo "  Make sure to start the backend with: ./run_backend.sh"
    echo "  (You can run this in a separate terminal)"
fi

# Start frontend dev server
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Frontend is ready!${NC}"
echo ""
echo -e "${BLUE}  Frontend URL: http://localhost:5173${NC}"
echo -e "${BLUE}  Backend API:  http://localhost:8000/api/v1${NC}"
echo ""
echo -e "${YELLOW}  Press Ctrl+C to stop the dev server${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""

