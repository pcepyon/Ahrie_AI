#!/bin/bash

# Script to run ngrok for Telegram webhook development

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -E '^(NGROK_AUTHTOKEN|NGROK_DOMAIN|API_PORT)' | xargs)
fi

# Check if ngrok auth token is set
if [ -z "$NGROK_AUTHTOKEN" ]; then
    echo "❌ NGROK_AUTHTOKEN not found in .env file"
    echo "Please add your ngrok authtoken to .env file"
    echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Set default port if not specified
API_PORT=${API_PORT:-8000}

echo "🌐 Starting ngrok tunnel..."
echo "📍 Forwarding to localhost:$API_PORT"

# Check if custom domain is set
if [ -n "$NGROK_DOMAIN" ]; then
    echo "🔗 Using custom domain: $NGROK_DOMAIN"
    ngrok http $API_PORT --authtoken=$NGROK_AUTHTOKEN --domain=$NGROK_DOMAIN
else
    echo "🔗 Using random ngrok URL"
    ngrok http $API_PORT --authtoken=$NGROK_AUTHTOKEN
fi