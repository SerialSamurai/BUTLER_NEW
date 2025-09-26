#!/bin/bash

echo "============================================================"
echo "                  BUTLER System Launcher"
echo "            Texas Association of Counties"
echo "============================================================"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "[1] Checking Python installation..."
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}Python found!${NC}"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    echo -e "${GREEN}Python found!${NC}"
    PYTHON_CMD=python
else
    echo -e "${RED}ERROR: Python is not installed${NC}"
    echo "Please install Python 3.8+ from python.org"
    exit 1
fi
echo ""

echo "[2] Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}Ollama found!${NC}"
else
    echo -e "${YELLOW}WARNING: Ollama not found${NC}"
    echo "Please install Ollama from: https://ollama.ai"
    echo ""
    echo "For macOS: brew install ollama"
    echo "For Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo ""

echo "[3] Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet
echo -e "${GREEN}Dependencies checked!${NC}"
echo ""

echo "[4] Starting Ollama service..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
echo "Waiting for Ollama to start..."
sleep 5
echo ""

echo "[5] Checking for Llama model..."
if ! ollama list | grep -q "llama3.2:latest"; then
    echo "Llama model not found. Pulling model (this may take a while)..."
    ollama pull llama3.2:latest
fi
echo -e "${GREEN}Model ready!${NC}"
echo ""

echo "[6] Starting BUTLER API Server..."
$PYTHON_CMD ollama_with_docs.py > butler.log 2>&1 &
API_PID=$!
echo "Waiting for API to initialize..."
sleep 3
echo ""

echo "[7] Opening BUTLER Interface..."
# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5019
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:5019 2>/dev/null || echo "Please open http://localhost:5019 in your browser"
else
    echo "Please open http://localhost:5019 in your browser"
fi
echo ""

echo "============================================================"
echo -e "${GREEN}       BUTLER System Started Successfully!${NC}"
echo "============================================================"
echo ""
echo "Access Points:"
echo "  - Web Interface: http://localhost:5019"
echo "  - API Status: http://localhost:5019/api/status"
echo "  - Main Interface: Open butler-final.html in browser"
echo ""
echo "Process IDs:"
echo "  - Ollama: $OLLAMA_PID"
echo "  - BUTLER API: $API_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo "============================================================"
echo ""

# Trap Ctrl+C and clean up
trap cleanup INT

cleanup() {
    echo ""
    echo "Stopping BUTLER services..."
    kill $API_PID 2>/dev/null
    kill $OLLAMA_PID 2>/dev/null
    echo "Services stopped."
    exit 0
}

# Keep script running
while true; do
    sleep 1
done