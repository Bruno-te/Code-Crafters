#!/bin/bash

# MoMo SMS ETL Pipeline Runner Script
# This script runs the complete ETL pipeline for processing MoMo SMS data

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

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}MoMo SMS ETL Pipeline Runner${NC}"
echo -e "${BLUE}================================${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
cd "$PROJECT_DIR"

if ! python3 -c "import lxml, dateutil" 2>/dev/null; then
    echo -e "${YELLOW}Installing required packages...${NC}"
    pip3 install -r requirements.txt
fi

# Check if XML file exists
XML_FILE="$PROJECT_DIR/data/raw/momo.xml"
if [ ! -f "$XML_FILE" ]; then
    echo -e "${YELLOW}Warning: XML file not found at $XML_FILE${NC}"
    echo -e "${YELLOW}Please place your momo.xml file in the data/raw/ directory${NC}"
    echo -e "${YELLOW}Creating sample XML file for testing...${NC}"
    
    # Create sample XML file for testing
    mkdir -p "$PROJECT_DIR/data/raw"
    cat > "$XML_FILE" << 'EOF'
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
    echo -e "${GREEN}Sample XML file created at $XML_FILE${NC}"
fi

# Run ETL pipeline
echo -e "${BLUE}Starting ETL pipeline...${NC}"
echo -e "${BLUE}Input XML: $XML_FILE${NC}"
echo -e "${BLUE}Output DB: $PROJECT_DIR/data/db.sqlite3${NC}"
echo -e "${BLUE}Dashboard JSON: $PROJECT_DIR/data/processed/dashboard.json${NC}"
echo ""

# Run the Python ETL script
python3 "$PROJECT_DIR/etl/run.py" --xml "$XML_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}ETL Pipeline completed successfully!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "1. Start the frontend: ${YELLOW}./scripts/serve_frontend.sh${NC}"
    echo -e "2. Open your browser to: ${YELLOW}http://localhost:8000${NC}"
    echo -e "3. View the dashboard and analytics"
else
    echo ""
    echo -e "${RED}================================${NC}"
    echo -e "${RED}ETL Pipeline failed!${NC}"
    echo -e "${RED}================================${NC}"
    echo ""
    echo -e "${YELLOW}Check the logs at: $PROJECT_DIR/data/logs/etl.log${NC}"
    exit 1
fi
