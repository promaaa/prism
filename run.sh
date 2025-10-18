#!/bin/bash

# Prism - Convenience run script
# This script activates the virtual environment and runs the application

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Prism - Personal Finance & Investment App${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Creating virtual environment..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Virtual environment created${NC}"
    echo ""
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    # Activate virtual environment
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import PyQt6" 2>/dev/null; then
    echo -e "${RED}❌ Dependencies not installed!${NC}"
    echo "Installing dependencies..."
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install dependencies${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

echo ""
echo -e "${GREEN}🚀 Starting Prism...${NC}"
echo ""

# Run the application
python main.py

# Deactivate virtual environment on exit
deactivate
