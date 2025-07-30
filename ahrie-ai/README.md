# Ahrie AI - K-Beauty Medical Tourism Chatbot

🤖 AI-powered Telegram chatbot helping Saudi Arabian and UAE clients navigate Korean beauty medical tourism with confidence.

## 🌟 Features

- **Multi-Agent System**: Powered by Agno framework with specialized agents:
  - 🧭 **Coordinator Agent**: Orchestrates conversations and routes queries
  - 🏥 **Medical Expert Agent**: Provides procedure information and clinic recommendations
  - 📹 **Review Analyst Agent**: Analyzes YouTube reviews and patient experiences
  - 🕌 **Cultural Advisor Agent**: Offers halal guidance and cultural support

- **Multi-Language Support**: 🌐 Arabic, English, and Korean interfaces
- **Real-Time Translation**: Seamless communication across languages
- **YouTube Review Analysis**: Aggregate insights from real patient experiences
- **Halal & Cultural Guidance**: Prayer times, halal restaurants, and cultural etiquette
- **Clinic Database**: Verified information about top Korean plastic surgery clinics
- **Smart Search**: Vector-based semantic search using LanceDB

## 🏗️ Architecture

```
ahrie-ai/
├── src/
│   ├── agents/          # Agno-based AI agents
│   ├── api/             # FastAPI application
│   ├── bot/             # Telegram bot handlers
│   ├── database/        # PostgreSQL models
│   ├── scrapers/        # YouTube and web scrapers
│   ├── knowledge/       # Vector store (LanceDB)
│   ├── translations/    # i18n support
│   └── utils/           # Utilities and config
├── tests/               # Test suite
├── scripts/             # Setup and utility scripts
└── data/                # Data storage
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Telegram Bot Token
- OpenAI API Key
- YouTube Data API Key
- Ngrok (for local development)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ahrie-ai.git
   cd ahrie-ai
   ```

2. **Run the setup script**
   ```bash
   chmod +x scripts/setup_dev.sh
   ./scripts/setup_dev.sh
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start the services**
   ```bash
   # Terminal 1: Start the application
   source venv/bin/activate
   python src/main.py

   # Terminal 2: Start ngrok tunnel
   ./scripts/run_ngrok.sh
   ```

5. **Set up Telegram webhook**
   ```bash
   curl -X POST http://localhost:8000/api/v1/webhook/set
   ```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret

# OpenAI
OPENAI_API_KEY=your_openai_key

# YouTube
YOUTUBE_API_KEY=your_youtube_key

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ahrie_ai

# Ngrok (development)
NGROK_AUTHTOKEN=your_ngrok_token
NGROK_DOMAIN=your-domain.ngrok.io
```

### Docker Compose Services

- **PostgreSQL**: Main database
- **Redis**: Caching and rate limiting
- **Ngrok**: Webhook tunneling for development

## 💬 Usage

### Bot Commands

- `/start` - Start conversation
- `/help` - Show help menu
- `/language` - Change language
- `/procedures` - Browse procedures
- `/clinics` - View top clinics
- `/about` - About Ahrie AI

### Example Queries

- "Tell me about rhinoplasty in Korea"
- "Find halal restaurants near Gangnam clinics"
- "Show me Arabic reviews for facial contouring"
- "What are prayer times in Seoul?"
- "I need a female doctor for my procedure"

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents/test_coordinator.py
```

## 📊 API Documentation

Once running, visit:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

## 🚢 Deployment

### Production Checklist

1. Set `ENVIRONMENT=production` in `.env`
2. Configure proper `WEBHOOK_BASE_URL`
3. Set up SSL certificates
4. Configure production database
5. Set up monitoring (Prometheus/Grafana)
6. Configure backup strategy

### Using Docker

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style

- Follow PEP 8
- Use Black for formatting
- Run pre-commit hooks
- Add type hints
- Write docstrings

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Agno Framework for multi-agent orchestration
- Telegram Bot API
- OpenAI for language models
- YouTube Data API
- Korean medical tourism industry partners

## 📞 Support

- Email: support@ahrieai.com
- Telegram: @AhrieAISupport
- Issues: [GitHub Issues](https://github.com/yourusername/ahrie-ai/issues)

---

Built with ❤️ for bridging cultures in K-Beauty medical tourism