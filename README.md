# Ahrie AI - K-뷰티 의료 관광 챗봇

🤖 사우디아라비아와 UAE 고객을 위한 AI 기반 텔레그램 챗봇으로, 한국 미용 의료 관광을 자신 있게 안내합니다.

## 🌟 주요 기능

- **멀티 에이전트 시스템**: Agno 프레임워크 기반의 전문 에이전트:
  - 🧭 **코디네이터 에이전트**: 대화를 조율하고 쿼리를 라우팅
  - 🏥 **의료 전문가 에이전트**: 시술 정보 및 병원 추천 제공
  - 📹 **리뷰 분석 에이전트**: YouTube 리뷰 및 환자 경험 분석
  - 🕌 **문화 어드바이저 에이전트**: 할랄 안내 및 문화적 지원 제공

- **다국어 지원**: 🌐 아랍어, 영어, 한국어 인터페이스
- **실시간 번역**: 언어 간 원활한 소통
- **YouTube 리뷰 분석**: 실제 환자 경험에서 얻은 통합 인사이트
- **할랄 및 문화 안내**: 기도 시간, 할랄 레스토랑, 문화 에티켓
- **병원 데이터베이스**: 검증된 한국 성형외과 병원 정보
- **스마트 검색**: LanceDB를 사용한 벡터 기반 의미론적 검색

## 🏗️ 아키텍처

```
ahrie-ai/
├── src/
│   ├── agents/          # Agno 기반 AI 에이전트
│   ├── api/             # FastAPI 애플리케이션
│   ├── bot/             # Telegram 봇 핸들러
│   ├── database/        # PostgreSQL 모델
│   ├── scrapers/        # YouTube 및 웹 스크래퍼
│   ├── knowledge/       # 벡터 저장소 (LanceDB)
│   ├── translations/    # 다국어 지원
│   └── utils/           # 유틸리티 및 설정
├── tests/               # 테스트 스위트
├── scripts/             # 설정 및 유틸리티 스크립트
└── data/                # 데이터 저장소
```

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- PostgreSQL 15+
- Docker & Docker Compose
- Telegram Bot Token
- OpenAI API Key
- YouTube Data API Key
- Ngrok (로컬 개발용)

### 설치 방법

1. **저장소 클론**
   ```bash
   git clone https://github.com/yourusername/ahrie-ai.git
   cd ahrie-ai
   ```

2. **설정 스크립트 실행**
   ```bash
   chmod +x scripts/setup_dev.sh
   ./scripts/setup_dev.sh
   ```

3. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일을 열어 API 키를 입력하세요
   ```

4. **서비스 시작**
   ```bash
   # 터미널 1: 애플리케이션 시작
   source venv/bin/activate
   python src/main.py

   # 터미널 2: ngrok 터널 시작
   ./scripts/run_ngrok.sh
   ```

5. **Telegram 웹훅 설정**
   ```bash
   curl -X POST http://localhost:8000/api/v1/webhook/set
   ```

## 🔧 설정

### 환경 변수

`.env` 파일의 주요 환경 변수:

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

# Ngrok (개발용)
NGROK_AUTHTOKEN=your_ngrok_token
NGROK_DOMAIN=your-domain.ngrok.io
```

### Docker Compose 서비스

- **PostgreSQL**: 메인 데이터베이스
- **Redis**: 캐싱 및 속도 제한
- **Ngrok**: 개발용 웹훅 터널링

## 💬 사용법

### 봇 명령어

- `/start` - 대화 시작
- `/help` - 도움말 메뉴 표시
- `/language` - 언어 변경
- `/procedures` - 시술 목록 보기
- `/clinics` - 주요 병원 보기
- `/about` - Ahrie AI 소개

### 예시 쿼리

- "한국의 코 성형에 대해 알려주세요"
- "강남 병원 근처 할랄 레스토랑 찾기"
- "안면 윤곽 수술에 대한 아랍어 리뷰 보기"
- "서울의 기도 시간은 언제인가요?"
- "시술을 위한 여성 의사가 필요해요"

## 🧪 테스트

```bash
# 모든 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=src

# 특정 테스트 파일 실행
pytest tests/test_agents/test_coordinator.py
```

## 📊 API 문서

애플리케이션 실행 후 방문:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health

## 🚢 배포

### 프로덕션 체크리스트

1. `.env`에서 `ENVIRONMENT=production` 설정
2. 적절한 `WEBHOOK_BASE_URL` 구성
3. SSL 인증서 설정
4. 프로덕션 데이터베이스 구성
5. 모니터링 설정 (Prometheus/Grafana)
6. 백업 전략 구성

### Docker 사용

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 기여하기

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 열기

### 코드 스타일

- PEP 8 준수
- Black을 사용한 포매팅
- pre-commit 훅 실행
- 타입 힌트 추가
- Docstring 작성

## 📝 라이선스

이 프로젝트는 MIT 라이선스로 제공됩니다 - 자세한 내용은 LICENSE 파일을 참조하세요.

## 🙏 감사의 말

- 멀티 에이전트 오케스트레이션을 위한 Agno Framework
- Telegram Bot API
- 언어 모델을 위한 OpenAI
- YouTube Data API
- 한국 의료 관광 산업 파트너

## 📞 지원

- 이메일: support@ahrieai.com
- 텔레그램: @AhrieAISupport
- 이슈: [GitHub Issues](https://github.com/yourusername/ahrie-ai/issues)

---

K-뷰티 의료 관광에서 문화를 연결하기 위해 ❤️로 만들었습니다