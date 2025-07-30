#!/bin/bash
# Development server wrapper - starts both main app and Agno Playground

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Move to script directory
cd "$(dirname "$0")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Ahrie AI Development Environment                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Check if Playground port is available
if check_port 7777; then
    echo -e "${YELLOW}⚠️  Port 7777 is already in use. Killing existing process...${NC}"
    lsof -Pi :7777 -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start Agno Playground in background
echo -e "${GREEN}🎮 Starting Agno Playground on port 7777...${NC}"
python3 playground.py > playground.log 2>&1 &
PLAYGROUND_PID=$!

# Give Playground time to start
sleep 3

# Check if Playground started successfully
if ps -p $PLAYGROUND_PID > /dev/null; then
    echo -e "${GREEN}✅ Agno Playground started successfully!${NC}"
    echo -e "   📍 Local URL: http://localhost:7777"
    echo -e "   🌐 Web UI: https://app.agno.com/playground"
    echo ""
else
    echo -e "${YELLOW}⚠️  Failed to start Agno Playground. Check playground.log for details.${NC}"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down development environment...${NC}"
    
    # Kill Playground if running
    if [ ! -z "$PLAYGROUND_PID" ] && ps -p $PLAYGROUND_PID > /dev/null; then
        echo -e "${GREEN}   Stopping Agno Playground...${NC}"
        kill $PLAYGROUND_PID 2>/dev/null || true
    fi
    
    # The main server cleanup will be handled by start_dev_server.sh
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Set up trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start the main development server
echo -e "${GREEN}🚀 Starting main development server...${NC}"
echo ""
./scripts/start_dev_server.sh