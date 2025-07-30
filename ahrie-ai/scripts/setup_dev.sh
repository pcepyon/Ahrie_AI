#!/bin/bash

# Development setup script for Ahrie AI

set -e  # Exit on error

echo "🚀 Setting up Ahrie AI development environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements-dev.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your API keys and configuration"
else
    echo "✅ .env file exists"
fi

# Start PostgreSQL with Docker
echo "🐘 Starting PostgreSQL with Docker..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Run database migrations
echo "🗄️ Setting up database..."
python scripts/init_db.py

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Download ngrok if not present
if ! command -v ngrok &> /dev/null; then
    echo "📥 Downloading ngrok..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -s https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip -o ngrok.zip
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -s https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz -o ngrok.tgz
        tar xvzf ngrok.tgz
        rm ngrok.tgz
    fi
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        unzip -o ngrok.zip
        rm ngrok.zip
    fi
    
    chmod +x ngrok
    echo "✅ ngrok downloaded"
else
    echo "✅ ngrok is already installed"
fi

echo "
✨ Development environment setup complete!

Next steps:
1. Update .env file with your API keys:
   - TELEGRAM_BOT_TOKEN
   - OPENAI_API_KEY
   - YOUTUBE_API_KEY
   - NGROK_AUTHTOKEN

2. Start the development server:
   ./scripts/run_dev.sh

3. In another terminal, start ngrok:
   ./scripts/run_ngrok.sh

4. Set your Telegram webhook:
   curl -X POST http://localhost:8000/api/v1/webhook/set

Happy coding! 🎉
"