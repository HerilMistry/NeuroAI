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
    echo -e "   \u2514\u2500 Installs: Python, pip, Django, DRF, vllm"
    echo ""
    echo -e "${YELLOW}2)${NC} Run Frontend Only (Connected to localhost:8000)"
    echo -e "   \u2514\u2500 Installs: Node.js, npm, React, Vite, TypeScript"
    echo ""
    echo -e "${YELLOW}3)${NC} Run Both (Backend + Frontend in separate windows)"
    echo -e "   \u2514\u2500 Installs: All Python and Node.js dependencies"
    echo ""
    echo -e "${YELLOW}4)${NC} Run with Docker Compose (Recommended)"
    echo -e "   \u2514\u2500 Builds Docker images with all dependencies"
    echo ""
    echo -e "${YELLOW}5)${NC} Check System Requirements"
    echo -e "   \u2514\u2500 Verify if all tools are installed"
    echo ""
    echo -e "${YELLOW}6)${NC} Exit"
    echo ""
    read -p "$(echo -e ${BLUE}Enter your choice [1-6]:${NC} )" choice
}

# Function to check system requirements
check_requirements() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}System Requirements Check${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Verifying required tools and versions...${NC}"
    echo ""

    requirements_met=true

    echo -e "${MAGENTA}REQUIRED TOOLS${NC}"
    echo -e "${MAGENTA}\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500${NC}"
    echo ""

    # Check Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}\u2713 Python 3${NC} ($PYTHON_VERSION)"
        echo "    \u2514\u2500 Needed for: Backend, Django, scientific computing"
    else
        echo -e "${RED}\u2717 Python 3${NC} is not installed"
        echo "    \u2514\u2500 Install from: https://www.python.org/"
        requirements_met=false
    fi
    echo ""

    # Check pip
    if command -v pip &> /dev/null; then
        PIP_VERSION=$(pip --version 2>&1 | awk '{print $2}')
        echo -e "${GREEN}\u2713 pip${NC} (v$PIP_VERSION)"
        echo "    \u2514\u2500 Needed for: Installing Python packages (Django, vllm, etc.)"
    else
        echo -e "${RED}\u2717 pip${NC} is not installed"
        requirements_met=false
    fi
    echo ""

    # Check Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        echo -e "${GREEN}\u2713 Node.js${NC} ($NODE_VERSION)"
        echo "    \u2514\u2500 Needed for: Frontend, React, Vite"
    else
        echo -e "${RED}\u2717 Node.js${NC} is not installed"
        echo "    \u2514\u2500 Install from: https://nodejs.org/ (20+)"
        requirements_met=false
    fi
    echo ""

    # Check npm
    if command -v npm &> /dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}\u2713 npm${NC} (v$NPM_VERSION)"
        echo "    \u2514\u2500 Needed for: Installing Node.js packages (React, TailwindCSS, etc.)"
    else
        echo -e "${RED}\u2717 npm${NC} is not installed"
        requirements_met=false
    fi
    echo ""

    echo -e "${MAGENTA}OPTIONAL TOOLS${NC}"
    echo -e "${MAGENTA}\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500${NC}"
    echo ""

    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        echo -e "${GREEN}\u2713 Docker${NC} ($DOCKER_VERSION)"
        echo "    \u2514\u2500 Needed for: Docker Compose (full stack deployment)"
    else
        echo -e "${YELLOW}\u26a0 Docker${NC} is not installed"
        echo "    \u2514\u2500 Recommended for: Production-like environment"
        echo "    \u2514\u2500 Install from: https://www.docker.com/"
    fi
    echo ""

    # Check Docker Compose (optional)
    if command -v docker-compose &> /dev/null; then
        DC_VERSION=$(docker-compose --version)
        echo -e "${GREEN}\u2713 Docker Compose${NC} ($DC_VERSION)"
        echo "    \u2514\u2500 Needed for: Running PostgreSQL + Backend + Frontend together"
    else
        echo -e "${YELLOW}\u26a0 Docker Compose${NC} is not installed"
        echo "    \u2514\u2500 Deploy full stack with: docker-compose up"
    fi
    echo ""

    # Check curl (for backend verification)
    if command -v curl &> /dev/null; then
        echo -e "${GREEN}\u2713 curl${NC}"
        echo "    \u2514\u2500 Needed for: Checking backend API availability"
    else
        echo -e "${YELLOW}\u26a0 curl${NC} is not installed"
        echo "    \u2514\u2500 Optional for: Testing API endpoints"
    fi
    echo ""

    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    if [ "$requirements_met" = true ]; then
        echo -e "${GREEN}✓ All required dependencies are installed!${NC}"
        echo -e "${GREEN}Ready to run NeuroDegenRx${NC}"
    else
        echo -e "${RED}✗ Some required dependencies are missing!${NC}"
        echo -e "${YELLOW}Please install the missing tools before proceeding${NC}"
    fi
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Function to run backend
run_backend() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Starting NeuroDegenRx Backend${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Verifying backend dependencies:${NC}"
    echo -e "  • Python 3"
    echo -e "  • pip package manager"
    echo -e "  • Virtual environment"
    echo -e "  • Python requirements (Django, DRF, vllm, etc.)"
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
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Starting NeuroDegenRx Frontend${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Verifying frontend dependencies:${NC}"
    echo -e "  • Node.js 20+"
    echo -e "  • npm package manager"
    echo -e "  • node_modules (React, Vite, TypeScript, etc.)"
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
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Starting NeuroDegenRx (Backend + Frontend)${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  Installation Mode: Backend (Foreground) + Frontend (Separate Window)${NC}"
    echo ""
    echo -e "${YELLOW}Dependencies to install:${NC}"
    echo -e "${YELLOW}Backend:${NC}"
    echo -e "  • Python 3, pip"
    echo -e "  • Django, Django REST Framework"
    echo -e "  • vllm (MedGemma inference engine)"
    echo -e "  • Database adapters, scientific libraries"
    echo ""
    echo -e "${YELLOW}Frontend (after backend starts):${NC}"
    echo -e "  • Node.js packages (React, Vite, TypeScript)"
    echo -e "  • TailwindCSS, development dependencies"
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
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}Starting NeuroDegenRx with Docker Compose${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}Docker services to initialize:${NC}"
    echo -e "  • PostgreSQL 15 (Database)"
    echo -e "  • Backend (Django + vllm, port 8000)"
    echo -e "  • Frontend (React/Vite, port 5173)"
    echo ""
    echo -e "${YELLOW}Installation steps:${NC}"
    echo -e "  1) Building Docker images..."
    echo -e "  2) Installing Python dependencies (Django, DRF, vllm, etc.)"
    echo -e "  3) Installing Node.js packages (React, Vite, TypeScript, etc.)"
    echo -e "  4) Initializing PostgreSQL database"
    echo -e "  5) Starting all services"
    echo ""
    
    if [ -f "$SCRIPT_DIR/docker-compose.yml" ]; then
        cd "$SCRIPT_DIR"
        echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
        echo -e "${MAGENTA}  Building and starting Docker containers${NC}"
        echo -e "${MAGENTA}═══════════════════════════════════════════════════════════${NC}"
        echo ""
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
