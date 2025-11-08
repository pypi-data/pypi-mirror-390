#!/bin/bash
################################################################################
# MHA Toolbox Pro - Professional Launch Script (Linux/Mac)
################################################################################
#
# This script launches the MHA Toolbox web interface with optimal settings
# for production deployment and multi-user access.
#
# Usage:
#   ./launch.sh                     - Start with default settings
#   ./launch.sh --port 8080         - Start on custom port
#   ./launch.sh --public            - Allow external connections
#   ./launch.sh --multi-user        - Enable multi-user mode with cleanup
#
################################################################################

echo ""
echo "============================================================================"
echo "  MHA TOOLBOX PRO - Meta-Heuristic Algorithm Optimization Suite"
echo "============================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Python 3 is not installed or not in PATH"
    echo ""
    echo "Please install Python 3.8 or higher"
    echo ""
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}[INFO]${NC} Virtual environment not found. Creating one..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to create virtual environment"
        exit 1
    fi
    echo -e "${GREEN}[SUCCESS]${NC} Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}[INFO]${NC} Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
echo -e "${BLUE}[INFO]${NC} Checking dependencies..."
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[INFO]${NC} Installing dependencies..."
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERROR]${NC} Failed to install dependencies"
        exit 1
    fi
    echo -e "${GREEN}[SUCCESS]${NC} Dependencies installed"
    echo ""
fi

# Default settings
PORT=8501
ADDRESS="localhost"
MULTI_USER=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --public)
            ADDRESS="0.0.0.0"
            shift
            ;;
        --multi-user)
            MULTI_USER=1
            shift
            ;;
        *)
            echo -e "${RED}[ERROR]${NC} Unknown option: $1"
            exit 1
            ;;
    esac
done

# Clean up expired sessions if multi-user mode
if [ "$MULTI_USER" -eq 1 ]; then
    echo -e "${BLUE}[INFO]${NC} Multi-user mode enabled - cleaning up expired sessions..."
    python3 -m mha_toolbox.user_profile_optimized --cleanup
    echo ""
fi

echo -e "${BLUE}[INFO]${NC} Starting MHA Toolbox Web Interface..."
echo ""
echo "============================================================================"
echo "  Server Configuration:"
echo "  - Address: $ADDRESS"
echo "  - Port: $PORT"
echo "  - Multi-User: $MULTI_USER"
echo "============================================================================"
echo ""
echo -e "${GREEN}[INFO]${NC} Opening browser... Please wait..."
echo ""
echo -e "${YELLOW}[TIP]${NC} Press Ctrl+C to stop the server"
echo ""

# Launch streamlit with optimal settings
streamlit run mha_web_interface.py \
    --server.port=$PORT \
    --server.address=$ADDRESS \
    --server.headless=true \
    --server.enableCORS=true \
    --server.enableXsrfProtection=true \
    --server.maxUploadSize=200 \
    --browser.gatherUsageStats=false \
    --theme.base=light \
    --theme.primaryColor="#FF4B4B" \
    --theme.backgroundColor="#FFFFFF" \
    --theme.secondaryBackgroundColor="#F0F2F6"

echo ""
echo "============================================================================"
echo "  Server stopped"
echo "============================================================================"
echo ""
