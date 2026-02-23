#!/usr/bin/env bash
set -e

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables
export USE_SQLITE=true
export DEBUG=True

# Initialize database
echo "Running migrations..."
python3 manage.py migrate

# Seed sample data (safe to run multiple times — uses get_or_create)
echo "Seeding sample data..."
python3 manage.py seed_sample_data

# Start backend server
echo ""
echo "========================================="
echo "  Backend running at http://localhost:8000"
echo "  Press Ctrl+C to stop"
echo "========================================="
echo ""
python3 manage.py runserver