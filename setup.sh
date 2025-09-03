#!/bin/bash

# MoMo SMS Project Setup Script
# This script sets up the initial project environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}MoMo SMS Project Setup - Code Crafters${NC}"
echo -e "${BLUE}================================${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    echo -e "${YELLOW}Please install Python 3.8+ and try again${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${BLUE}Python version: $PYTHON_VERSION${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}Installing project dependencies...${NC}"
pip install -r requirements.txt

# Create necessary directories
echo -e "${YELLOW}Creating project directories...${NC}"
mkdir -p data/raw data/processed data/logs/dead_letter web/assets

# Make scripts executable
echo -e "${YELLOW}Setting up scripts...${NC}"
chmod +x scripts/*.sh

# Create sample data files
echo -e "${YELLOW}Creating sample data files...${NC}"

# Create sample XML if it doesn't exist
if [ ! -f "data/raw/momo.xml" ]; then
    cat > "data/raw/momo.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<momo_transactions>
    <transaction>
        <id>TXN001</id>
        <date>2024-01-15 14:30:00</date>
        <amount>1500.00</amount>
        <phone>+233241234567</phone>
        <message>Payment received for utility bill</message>
        <status>success</status>
        <type>payment</type>
    </transaction>
    <transaction>
        <id>TXN002</id>
        <date>2024-01-15 15:45:00</date>
        <amount>2500.00</amount>
        <phone>+233251234567</phone>
        <message>Money transfer completed</message>
        <status>success</status>
        <type>transfer</type>
    </transaction>
</momo_transactions>
EOF
    echo -e "${GREEN}Sample XML file created at data/raw/momo.xml${NC}"
fi

# Run initial ETL to create database and dashboard data
echo -e "${YELLOW}Running initial ETL pipeline...${NC}"
if ./scripts/run_etl.sh; then
    echo -e "${GREEN}Initial ETL pipeline completed successfully!${NC}"
else
    echo -e "${YELLOW}ETL pipeline had issues, but project setup continues...${NC}"
fi

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Project setup completed!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Activate virtual environment: ${YELLOW}source venv/bin/activate${NC}"
echo -e "2. Start the frontend: ${YELLOW}./scripts/serve_frontend.sh${NC}"
echo -e "3. Open your browser to: ${YELLOW}http://localhost:8000${NC}"
echo ""
echo -e "${BLUE}Project structure created:${NC}"
echo -e "  - ETL pipeline modules"
echo -e "  - Frontend dashboard"
echo -e "  - Database and data storage"
echo -e "  - Utility scripts"
echo -e "  - Unit tests"
echo ""
echo -e "${BLUE}Happy coding! 🚀${NC}"
