#!/bin/bash

echo "🚀 Setting up LangDB for Ahrie AI monitoring..."
echo "=============================================="

# Install pylangdb with agno support
echo "📦 Installing pylangdb[agno]..."
pip install 'pylangdb[agno]'

# Check if LangDB credentials are set
if [ -z "$LANGDB_API_KEY" ] || [ -z "$LANGDB_PROJECT_ID" ]; then
    echo ""
    echo "⚠️  LangDB credentials not found in environment!"
    echo ""
    echo "To enable LangDB monitoring, please set:"
    echo "  export LANGDB_API_KEY='your-langdb-api-key'"
    echo "  export LANGDB_PROJECT_ID='your-project-id'"
    echo ""
    echo "Get your credentials from: https://app.langdb.ai"
    echo ""
    
    # Check if credentials exist in .env.backup
    if [ -f ".env.backup" ]; then
        if grep -q "LANGDB_API_KEY" .env.backup; then
            echo "💡 Found LangDB credentials in .env.backup"
            echo "   Run: source .env.backup"
        fi
    fi
else
    echo "✅ LangDB credentials found!"
    echo "   API Key: ${LANGDB_API_KEY:0:10}..."
    echo "   Project ID: $LANGDB_PROJECT_ID"
fi

echo ""
echo "✨ Setup complete! You can now run:"
echo "   python test_team_orchestrator_v2.py"
echo ""
echo "📊 Monitor your agent traces at:"
echo "   https://app.langdb.ai/projects/$LANGDB_PROJECT_ID"