# Ahrie AI - K-Beauty Medical Tourism Chatbot

## Project Overview
Ahrie AI는 사우디아라비아와 UAE 고객을 위한 한국 미용 의료 관광 챗봇입니다. Telegram을 인터페이스로 사용하며, Agno 프레임워크 기반의 멀티 에이전트 시스템으로 구축되었습니다.

## Architecture

### 1. Multi-Agent System (Agno Framework)
- **Coordinator Agent**: 사용자 대화를 조정하고 적절한 전문 에이전트로 라우팅
- **Medical Expert Agent**: 의료 시술 정보, 클리닉 추천, 의료 상담 제공
- **Review Analyst Agent**: YouTube 리뷰 분석 및 환자 경험 인사이트 제공
- **Cultural Advisor Agent**: 할랄 가이드, 기도 시설, 문화적 조언 제공

### 2. Technology Stack
- **Backend**: FastAPI, Uvicorn
- **Bot Interface**: python-telegram-bot (v20+)
- **Database**: PostgreSQL (asyncpg)
- **Vector Store**: LanceDB
- **AI/ML**: OpenAI API
- **Web Scraping**: YouTube Data API, BeautifulSoup4

### 3. Key Features
- 🌐 다국어 지원 (Arabic, English, Korean)
- 📹 YouTube 리뷰 실시간 분석
- 🕌 할랄 레스토랑 및 기도 시설 정보
- 👩‍⚕️ 여성 의료진 정보 제공
- 💰 실시간 가격 비교
- 📍 위치 기반 서비스

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Ngrok (for local development)

### Required API Keys
- Telegram Bot Token
- OpenAI API Key
- YouTube Data API Key
- Ngrok Auth Token

### Installation Steps
```bash
# 1. Clone repository
git clone <repository-url>
cd ahrie-ai

# 2. Run setup script
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start services
docker-compose up -d postgres redis

# 5. Run application
python src/main.py

# 6. Start ngrok (in another terminal)
./scripts/run_ngrok.sh

# 7. Set webhook
curl -X POST http://localhost:8000/api/v1/webhook/set
```

## Known Issues & Solutions

### 1. Import Errors
- **SQLAlchemy metadata reserved word**: Changed `metadata` field to `message_metadata` in Message model
- **Telegram ParseMode import**: Updated to `from telegram.constants import ParseMode` for v20+
- **Agno framework imports**: Currently commented out pending actual package structure verification

### 2. Module Import Path Issues
- Added `sys.path.append` to main.py to handle module imports
- Alternative: Use `python -m src.main` to run as module

### 3. Type Hints
- Added missing `List` import in translation manager

## Project Structure
```
ahrie-ai/
├── src/
│   ├── agents/          # Agno agents (Coordinator, Medical, Review, Cultural)
│   ├── api/             # FastAPI application and routes
│   ├── bot/             # Telegram bot handlers and keyboards
│   ├── database/        # SQLAlchemy models and connection
│   ├── scrapers/        # YouTube and medical info scrapers
│   ├── knowledge/       # LanceDB vector store
│   ├── translations/    # i18n support (AR/EN/KO)
│   └── utils/           # Config and logging
├── tests/               # Test suite
├── scripts/             # Setup and utility scripts
├── data/                # Data storage
└── logs/                # Application logs
```

## API Endpoints
- `POST /api/v1/webhook/telegram` - Telegram webhook handler
- `POST /api/v1/webhook/set` - Set Telegram webhook
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/detailed` - Detailed health status

## Database Schema
- **users**: Telegram user information
- **conversations**: Chat sessions
- **messages**: Conversation messages
- **clinics**: Medical clinic information
- **procedures**: Medical procedure details
- **reviews**: User reviews and YouTube analyses
- **halal_places**: Halal restaurants and facilities
- **translation_cache**: Translation cache

## Development Commands
```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/

# Start PostgreSQL
docker-compose up -d postgres

# View logs
tail -f logs/app.log
```

## Deployment Notes
- Set `ENVIRONMENT=production` in .env
- Configure proper SSL certificates
- Set up monitoring (Prometheus/Grafana)
- Configure backup strategy for PostgreSQL
- Use proper webhook URL instead of ngrok

## TODO
1. Verify and implement actual Agno framework imports
2. Add comprehensive test coverage
3. Implement actual YouTube scraping logic
4. Set up CI/CD pipeline
5. Add monitoring and alerting
6. Implement rate limiting and caching
7. Add admin dashboard
8. Enhance NLP capabilities

## Troubleshooting
- If module import fails: Check PYTHONPATH or use `python -m`
- If database connection fails: Verify PostgreSQL is running
- If webhook fails: Check ngrok is running and URL is correct
- If translations missing: Verify locale JSON files exist

## Contact
For questions or issues, please create a GitHub issue or contact the development team.