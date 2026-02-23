#!/usr/bin/env bash
set -e

# Navigate to frontend directory
cd "$(dirname "$0")/frontend"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start frontend dev server
echo ""
echo "========================================="
echo "  Frontend running at http://localhost:5173"
echo "  Press Ctrl+C to stop"
echo "========================================="
echo ""
npm run dev
