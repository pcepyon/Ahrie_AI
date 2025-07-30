#!/bin/bash

# Script to automate development server startup with ngrok
# This script:
# 1. Starts ngrok in the background
# 2. Extracts the ngrok URL
# 3. Updates the .env file with the new URL
# 4. Starts the development server
# 5. Sets the Telegram webhook

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check if we're in the right directory
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please run this script from the ahrie-ai directory"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -E '^(NGROK_AUTHTOKEN|API_PORT|TELEGRAM_BOT_TOKEN)' | xargs)

# Check required environment variables
if [ -z "$NGROK_AUTHTOKEN" ]; then
    print_error "NGROK_AUTHTOKEN not found in .env file"
    print_error "Please add your ngrok authtoken to .env file"
    print_error "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    print_error "TELEGRAM_BOT_TOKEN not found in .env file"
    exit 1
fi

# Set default port if not specified
API_PORT=${API_PORT:-8000}

# Kill any existing ngrok processes
print_status "Checking for existing ngrok processes..."
if pgrep -x "ngrok" > /dev/null; then
    print_warning "Found existing ngrok process. Killing it..."
    pkill -x ngrok
    sleep 2
fi

# Kill any existing Python processes on the API port
print_status "Checking for processes on port $API_PORT..."
if lsof -Pi :$API_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Found process on port $API_PORT. Killing it..."
    lsof -Pi :$API_PORT -sTCP:LISTEN -t | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start ngrok in the background
print_status "Starting ngrok tunnel on port $API_PORT..."
ngrok http $API_PORT --authtoken=$NGROK_AUTHTOKEN --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
print_status "Waiting for ngrok to initialize..."
sleep 5

# Check if ngrok is running
if ! ps -p $NGROK_PID > /dev/null; then
    print_error "Failed to start ngrok. Check ngrok.log for details"
    cat ngrok.log
    exit 1
fi

# Get ngrok URL using the API
print_status "Fetching ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data['tunnels']:
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'https':
                print(tunnel['public_url'])
                break
    else:
        print('')
except:
    print('')
")

if [ -z "$NGROK_URL" ]; then
    print_error "Failed to get ngrok URL. Check if ngrok is running properly"
    print_error "ngrok log:"
    tail -20 ngrok.log
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

print_status "Ngrok URL: $NGROK_URL"

# Backup the original .env file
cp .env .env.backup
print_status "Backed up .env to .env.backup"

# Update the WEBHOOK_BASE_URL in .env
print_status "Updating WEBHOOK_BASE_URL in .env..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|^WEBHOOK_BASE_URL=.*|WEBHOOK_BASE_URL=$NGROK_URL|" .env
else
    # Linux
    sed -i "s|^WEBHOOK_BASE_URL=.*|WEBHOOK_BASE_URL=$NGROK_URL|" .env
fi

# Verify the update
NEW_URL=$(grep "^WEBHOOK_BASE_URL=" .env | cut -d'=' -f2)
if [ "$NEW_URL" != "$NGROK_URL" ]; then
    print_error "Failed to update WEBHOOK_BASE_URL in .env"
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

print_status "Successfully updated WEBHOOK_BASE_URL to: $NGROK_URL"

# Function to cleanup on exit
cleanup() {
    print_warning "Shutting down..."
    
    # Kill the Python process
    if [ ! -z "$PYTHON_PID" ] && ps -p $PYTHON_PID > /dev/null; then
        print_status "Stopping Python server..."
        kill $PYTHON_PID 2>/dev/null || true
    fi
    
    # Kill ngrok
    if [ ! -z "$NGROK_PID" ] && ps -p $NGROK_PID > /dev/null; then
        print_status "Stopping ngrok..."
        kill $NGROK_PID 2>/dev/null || true
    fi
    
    # Clean up log file
    rm -f ngrok.log
    
    print_status "Cleanup complete"
}

# Set up trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start the Python application
print_status "Starting the development server..."
python3 src/main.py &
PYTHON_PID=$!

# Wait for the server to start
print_status "Waiting for server to start..."
sleep 5

# Check if the server is running
if ! ps -p $PYTHON_PID > /dev/null; then
    print_error "Failed to start the Python server"
    exit 1
fi

# Set the Telegram webhook
print_status "Setting Telegram webhook..."
WEBHOOK_RESPONSE=$(curl -s -X POST http://localhost:$API_PORT/api/v1/webhook/set)
echo "Webhook response: $WEBHOOK_RESPONSE"

# Display status
echo ""
print_status "🚀 Development server is running!"
echo ""
echo "  📍 Local server: http://localhost:$API_PORT"
echo "  🌐 Ngrok URL: $NGROK_URL"
echo "  🤖 Telegram Bot: https://t.me/$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['username'])" 2>/dev/null || echo "your_bot")"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""

# Keep the script running
wait $PYTHON_PID