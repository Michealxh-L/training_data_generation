#!/bin/bash

# Demo script for testing the training data generation system

echo "=================================================="
echo "Training Data Generation System - Demo"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your API keys"
    echo ""
    read -p "Do you want to continue with sample data generation (no API calls)? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Generate sample data (no API calls)
echo -e "${GREEN}Generating sample training data examples...${NC}"
python examples/generate_samples.py

echo ""
echo -e "${GREEN}Demo complete! Check the following directories:${NC}"
echo "  - examples/sample_outputs/   : Sample JSON files"
echo ""
echo "To generate real data from a repository, run:"
echo -e "${BLUE}  python main.py --repo-path /path/to/repo --scenario both --num-qa 10 --num-design 5${NC}"
echo ""
echo "=================================================="
