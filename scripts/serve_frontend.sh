#!/bin/bash

# MoMo SMS Frontend Server Script
# This script serves the dashboard frontend using Python's built-in HTTP server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Default port
PORT=${1:-8000}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}MoMo SMS Dashboard Server${NC}"
echo -e "${BLUE}================================${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if dashboard files exist
if [ ! -f "$PROJECT_DIR/index.html" ]; then
    echo -e "${RED}Error: Dashboard files not found${NC}"
    echo -e "${YELLOW}Please run the ETL pipeline first: ./scripts/run_etl.sh${NC}"
    exit 1
fi

# Check if dashboard data exists
if [ ! -f "$PROJECT_DIR/data/processed/dashboard.json" ]; then
    echo -e "${YELLOW}Warning: Dashboard data not found${NC}"
    echo -e "${YELLOW}The dashboard will use sample data${NC}"
fi

# Change to project directory
cd "$PROJECT_DIR"

echo -e "${BLUE}Starting dashboard server...${NC}"
echo -e "${BLUE}Project directory: $PROJECT_DIR${NC}"
echo -e "${BLUE}Port: $PORT${NC}"
echo -e "${BLUE}Dashboard URL: http://localhost:$PORT${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down dashboard server...${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start Python HTTP server
echo -e "${GREEN}Dashboard server started successfully!${NC}"
echo -e "${GREEN}Open your browser and navigate to: http://localhost:$PORT${NC}"
echo ""

python3 -m http.server "$PORT" --bind 127.0.0.1
