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
echo "╭──────────────────────────────────────────────────────────╮"
echo "│  NeuroDegenRx Backend Setup and Launch                   │"
echo "╰──────────────────────────────────────────────────────────╯"
echo -e "${NC}"

# Check dependencies
echo -e "${YELLOW}[1/6] Checking dependencies...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "  Install Python 3.11+ from https://www.python.org/"
    exit 1
else
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✓ Python 3 found (version $PYTHON_VERSION)${NC}"
fi

if ! command -v pip &> /dev/null; then
    echo -e "${RED}✗ pip is not installed${NC}"
    echo "  Install pip by running: python3 -m ensurepip"
    exit 1
else
    echo -e "${GREEN}✓ pip found${NC}"
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Create virtual environment if it doesn't exist
echo -e "${YELLOW}[2/6] Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    echo "  Creating new virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}[3/6] Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo -e "${YELLOW}[4/6] Installing Python dependencies...${NC}"
echo "  This may take a few minutes..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed successfully${NC}"

# Set environment variables
echo -e "${YELLOW}[5/6] Configuring environment...${NC}"
export USE_SQLITE=true
export DEBUG=True
echo -e "${GREEN}✓ Environment configured (SQLite, DEBUG mode)${NC}"

# Initialize database
echo -e "${YELLOW}[6/6] Initializing database...${NC}"
python3 manage.py migrate --noinput
echo "  Seeding sample data..."
python3 manage.py seed_sample_data
echo -e "${GREEN}✓ Database initialized and seeded${NC}"

# Start backend server
echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✓ Backend is ready!${NC}"
echo ""
echo -e "${BLUE}  Backend URL: http://localhost:8000${NC}"
echo -e "${BLUE}  Admin Panel: http://localhost:8000/admin${NC}"
echo -e "${BLUE}  API Root:    http://localhost:8000/api/v1${NC}"
echo ""
echo -e "${YELLOW}  Press Ctrl+C to stop the server${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""

python3 manage.py runserver