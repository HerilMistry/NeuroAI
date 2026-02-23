#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Header
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           NeuroDegenRx - Complete Project Setup            ║"
echo "║                                                            ║"
echo "║  Mechanism-aware decision support for neurodegenerative    ║"
echo "║              drug discovery (Research Use Only)            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Get the script directory
SCRIPT_DIR="$(dirname "$0")"

# Function to display menu
show_menu() {
    echo -e "${CYAN}Choose how you want to run NeuroDegenRx:${NC}"
    echo ""
    echo -e "${YELLOW}1)${NC} Run Backend Only (SQLite, LOCALHOST)"
    echo -e "${YELLOW}2)${NC} Run Frontend Only (Connected to localhost:8000)"
    echo -e "${YELLOW}3)${NC} Run Both (Backend + Frontend in separate windows)"
    echo -e "${YELLOW}4)${NC} Run with Docker Compose (Recommended)"
    echo -e "${YELLOW}5)${NC} Check System Requirements"
    echo -e "${YELLOW}6)${NC} Exit"
    echo ""
    read -p "$(echo -e ${BLUE}Enter your choice [1-6]:${NC} )" choice
}

# Function to check system requirements
check_requirements() {
    echo -e "${YELLOW}Checking system requirements...${NC}"
    echo ""

    requirements_met=true

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}✓ Python 3${NC} found ($PYTHON_VERSION)"
    else
        echo -e "${RED}✗ Python 3${NC} is not installed (Required for backend)"
        echo "  Install from: https://www.python.org/"
        requirements_met=false
    fi

    # Check pip
    if command -v pip &> /dev/null; then
        echo -e "${GREEN}✓ pip${NC} found"
    else
        echo -e "${RED}✗ pip${NC} is not installed"
        requirements_met=false
    fi

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}✓ Node.js${NC} found ($NODE_VERSION)"
    else
        echo -e "${RED}✗ Node.js${NC} is not installed (Required for frontend)"
        echo "  Install from: https://nodejs.org/ (20+)"
        requirements_met=false
    fi

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✓ npm${NC} found (v$NPM_VERSION)"
    else
        echo -e "${RED}✗ npm${NC} is not installed"
        requirements_met=false
    fi

    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        echo -e "${GREEN}✓ Docker${NC} found ($DOCKER_VERSION)"
    else
        echo -e "${YELLOW}⚠ Docker${NC} is not installed (Optional, needed for Docker Compose)"
    fi

    # Check curl (for backend verification)
    if command -v curl &> /dev/null; then
        echo -e "${GREEN}✓ curl${NC} found"
    else
        echo -e "${YELLOW}⚠ curl${NC} is not installed (Optional, for backend check)"
    fi

    echo ""
    if [ "$requirements_met" = true ]; then
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✓ All required dependencies are installed!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    else
        echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}✗ Some required dependencies are missing!${NC}"
        echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    fi
    echo ""
}

# Function to run backend
run_backend() {
    echo -e "${CYAN}Starting NeuroDegenRx Backend...${NC}"
    echo ""
    if [ -f "$SCRIPT_DIR/run_backend.sh" ]; then
        chmod +x "$SCRIPT_DIR/run_backend.sh"
        "$SCRIPT_DIR/run_backend.sh"
    else
        echo -e "${RED}Error: run_backend.sh not found${NC}"
        exit 1
    fi
}

# Function to run frontend
run_frontend() {
    echo -e "${CYAN}Starting NeuroDegenRx Frontend...${NC}"
    echo ""
    if [ -f "$SCRIPT_DIR/run_frontend.sh" ]; then
        chmod +x "$SCRIPT_DIR/run_frontend.sh"
        "$SCRIPT_DIR/run_frontend.sh"
    else
        echo -e "${RED}Error: run_frontend.sh not found${NC}"
        exit 1
    fi
}

# Function to run both
run_both() {
    echo -e "${CYAN}Starting NeuroDegenRx (Backend + Frontend)...${NC}"
    echo ""
    echo -e "${YELLOW}Note:${NC} Backend will run in the foreground."
    echo -e "${YELLOW}      To run the frontend, open a new terminal and run: ${BLUE}./run_frontend.sh${NC}"
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}  Starting Backend (Press Ctrl+C to stop)${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ -f "$SCRIPT_DIR/run_backend.sh" ]; then
        chmod +x "$SCRIPT_DIR/run_backend.sh"
        "$SCRIPT_DIR/run_backend.sh"
    else
        echo -e "${RED}Error: run_backend.sh not found${NC}"
        exit 1
    fi
}

# Function to run Docker Compose
run_docker() {
    echo -e "${CYAN}Starting NeuroDegenRx with Docker Compose...${NC}"
    echo ""
    if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
        cd "$SCRIPT_DIR"
        echo -e "${YELLOW}Building and starting Docker containers...${NC}"
        docker-compose up
    else
        echo -e "${RED}Error: docker-compose.yml not found${NC}"
        exit 1
    fi
}

# Function to display startup guide
show_startup_guide() {
    echo -e "${CYAN}NeuroDegenRx Startup Guide${NC}"
    echo ""
    echo -e "${YELLOW}Option 1: Local Development (SQLite)${NC}"
    echo "  Backend:  ./run_backend.sh (Terminal 1)"
    echo "  Frontend: ./run_frontend.sh (Terminal 2)"
    echo ""
    echo -e "${YELLOW}Option 2: Docker Compose (PostgreSQL)${NC}"
    echo "  ./run_project.sh (Choose option 4)"
    echo ""
    echo -e "${YELLOW}Access URLs:${NC}"
    echo "  Frontend: http://localhost:5173"
    echo "  Backend:  http://localhost:8000"
    echo "  API:      http://localhost:8000/api/v1"
    echo "  Admin:    http://localhost:8000/admin"
    echo ""
}

# Main loop
while true; do
    show_menu
    
    case $choice in
        1)
            run_backend
            ;;
        2)
            run_frontend
            ;;
        3)
            run_both
            ;;
        4)
            run_docker
            ;;
        5)
            check_requirements
            ;;
        6)
            echo -e "${CYAN}Thank you for using NeuroDegenRx!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Please select 1-6.${NC}"
            ;;
    esac
done
