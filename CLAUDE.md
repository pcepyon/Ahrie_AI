# Ahrie AI - K-Beauty Medical Tourism Chatbot

## Project Overview
Ahrie AI는 사우디아라비아와 UAE 고객을 위한 한국 미용 의료 관광 챗봇입니다. Telegram을 인터페이스로 사용하며, Agno 프레임워크 기반의 멀티 에이전트 시스템으로 구축되었습니다.

## 🚀 Quick Start
```bash
# API 연결 테스트
python ahrie-ai/test_llm_connection.py

# 오케스트레이터 테스트
python ahrie-ai/test_team_orchestrator_v2.py

# 메인 애플리케이션 실행
python ahrie-ai/src/main.py
```

## Architecture

### 1. Multi-Agent System (Agno Framework)
- **Team Orchestrator V2**: Agno 프레임워크 기반의 향상된 팀 오케스트레이터
  - LangDB 통합으로 모니터링 및 관찰 가능성 제공
  - 자동 에이전트 선택 및 조정
  - 세션 상태 관리 및 인사이트 제공

### 2. Technology Stack
- **Backend**: FastAPI, Uvicorn
- **Bot Interface**: python-telegram-bot (v20+)
- **Database**: PostgreSQL (asyncpg)
- **Vector Store**: LanceDB
- **AI/ML**: OpenAI API via LangDB (Agno Framework)
- **Web Scraping**: YouTube Data API, BeautifulSoup4
- **Monitoring**: LangDB (실시간 API 추적 및 모니터링)

### 3. Key Features
- 🌐 다국어 지원 (Arabic, English, Korean)
- 📹 YouTube 리뷰 실시간 분석
- 🕌 할랄 레스토랑 및 기도 시설 정보
- 👩‍⚕️ 여성 의료진 정보 제공
- 💰 실시간 가격 비교
- 📍 위치 기반 서비스
- 📊 LangDB를 통한 실시간 API 모니터링
- 🤖 Agno Framework 기반 지능형 에이전트 시스템

## Development Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Ngrok (for local development)

### Required API Keys
- Telegram Bot Token
- OpenAI API Key (또는 LangDB API Key)
- YouTube Data API Key
- Ngrok Auth Token
- LangDB API Key & Project ID (선택사항, 모니터링용)

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
- **Agno framework imports**: Successfully integrated with team_orchestrator_v2.py

### 2. Module Import Path Issues
- Added `sys.path.append` to main.py to handle module imports
- Alternative: Use `python -m src.main` to run as module

### 3. Type Hints
- Added missing `List` import in translation manager

## Project Structure
```
Ahrie_AI/
├── ahrie-ai/
│   ├── src/
│   │   ├── agents/          # Agno agents (Team Orchestrator V2)
│   │   │   ├── team_orchestrator_v2.py  # 메인 오케스트레이터
│   │   │   └── CLAUDE.md    # Agent API 설정 가이드
│   │   ├── api/             # FastAPI application and routes
│   │   ├── bot/             # Telegram bot handlers and keyboards
│   │   ├── database/        # SQLAlchemy models and connection
│   │   ├── scrapers/        # YouTube and medical info scrapers
│   │   ├── knowledge/       # LanceDB vector store
│   │   ├── translations/    # i18n support (AR/EN/KO)
│   │   └── utils/           # Config and logging
│   ├── test_llm_connection.py    # LangDB/OpenRouter 연결 테스트
│   ├── test_team_orchestrator_v2.py  # 오케스트레이터 테스트
│   ├── scripts/             # Setup and utility scripts
│   ├── data/                # Data storage
│   ├── logs/                # Application logs
│   └── tests/               # Empty test directory (to be populated)
├── frontend/                # Next.js frontend application
└── CLAUDE.md               # This file
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
# Navigate to project directory
cd ahrie-ai/

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
python test_llm_connection.py    # LangDB 연결 테스트
python test_team_orchestrator_v2.py  # 오케스트레이터 테스트

# Format code
black src/

# Type checking
mypy src/

# Start PostgreSQL
docker-compose up -d postgres

# View logs
tail -f logs/app.log

# Run main application
python src/main.py
```

## Deployment Notes
- Set `ENVIRONMENT=production` in .env
- Configure proper SSL certificates
- Set up monitoring (Prometheus/Grafana)
- Configure backup strategy for PostgreSQL
- Use proper webhook URL instead of ngrok

## TODO
1. ~~Verify and implement actual Agno framework imports~~ ✅ Completed with team_orchestrator_v2.py
2. Add comprehensive test coverage
3. Implement actual YouTube scraping logic
4. Set up CI/CD pipeline
5. ~~Add monitoring and alerting~~ ✅ Partially completed with LangDB integration
6. Implement rate limiting and caching
7. Add admin dashboard
8. Enhance NLP capabilities
9. Complete tests/ directory structure with proper test files
10. Integrate frontend with backend API
11. Implement Telegram bot webhook handlers
12. Add user authentication and session management

## Troubleshooting
- If module import fails: Check PYTHONPATH or use `python -m`
- If database connection fails: Verify PostgreSQL is running
- If webhook fails: Check ngrok is running and URL is correct
- If translations missing: Verify locale JSON files exist
- If LangDB connection fails: Check LANGDB_API_KEY and LANGDB_PROJECT_ID in .env
- If OpenRouter models fail: Use OpenAI models (gpt-4o-mini) as fallback

## Recent Updates
- ✅ Cleaned up test files - removed outdated tests that don't match current architecture
- ✅ Integrated Team Orchestrator V2 with Agno framework
- ✅ Added LangDB monitoring for API tracking
- ✅ Updated documentation to reflect current project state

## Contact
For questions or issues, please create a GitHub issue or contact the development team.