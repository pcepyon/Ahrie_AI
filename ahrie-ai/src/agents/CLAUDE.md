# Ahrie AI Agents - API Configuration Guide

## Overview
이 문서는 Ahrie AI의 에이전트들이 LangDB를 통해 API를 사용하는 방법을 설명합니다.

## Prerequisites

### 1. 환경 변수 설정
`.env` 파일에 다음 변수들이 필요합니다:
```bash
# LangDB Configuration
LANGDB_API_KEY=langdb_MjZmUmlOeXVJNDMxZ1c=
LANGDB_PROJECT_ID=a859ac1e-1986-4443-983f-21b0ca28ab74

# OpenRouter API (참고용, 실제로는 LangDB를 통해 사용)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### 2. 필요한 패키지
```bash
pip install agno
pip install langdb  # 버전이 낮아도 괜찮음
```

## Agent 구조

### 기본 구조
모든 에이전트는 다음 패턴을 따릅니다:

```python
from agno.models.langdb import LangDB
from pylangdb.agno import init

# LangDB 추적 초기화
try:
    init()
except ImportError:
    logger.warning("pylangdb not installed, tracing will not be available")

# 에이전트 클래스 내에서
class YourAgent:
    def __init__(self):
        # API 키 가져오기
        self.langdb_api_key = getattr(settings, 'LANGDB_API_KEY', None)
        self.langdb_project_id = getattr(settings, 'LANGDB_PROJECT_ID', None)
        
        # 에이전트 생성
        self.agent = Agent(
            name="AgentName",
            model=LangDB(
                id="모델명",
                api_key=self.langdb_api_key,
                project_id=self.langdb_project_id
            ),
            # ... 기타 설정
        )
```

## 에이전트별 모델 설정

### 1. Coordinator Agent
- **모델**: `gpt-4o-mini`
- **역할**: 사용자 대화 조정 및 라우팅
- **특징**: OpenAI 모델 사용 (OpenRouter 모델은 현재 LangDB에서 지원 확인 중)

### 2. Medical Expert Agent
- **모델**: `gpt-4o-mini`
- **역할**: 의료 시술 정보 제공
- **특징**: OpenAI 모델 직접 사용

### 3. Review Analyst Agent
- **모델**: `gpt-4o-mini`
- **역할**: YouTube 리뷰 분석
- **특징**: OpenAI 모델 직접 사용

### 4. Cultural Advisor Agent
- **모델**: `gpt-4o-mini`
- **역할**: 문화적 조언 제공
- **특징**: OpenAI 모델 직접 사용

### 5. Orchestrator Agent
- **모델**: `gpt-4o-mini`
- **역할**: 전체 에이전트 오케스트레이션
- **특징**: 메타 에이전트로 다른 에이전트들 조정

## LangDB 통합의 장점

1. **통합 모니터링**: 모든 API 호출이 LangDB 대시보드에서 추적됨
2. **다양한 모델 지원**: OpenRouter, OpenAI, Anthropic 등 250+ 모델
3. **비용 관리**: 실시간 사용량 및 비용 추적
4. **성능 분석**: 응답 시간, 에러율 등 메트릭 제공
5. **보안**: 엔터프라이즈급 API 관리

## 모델 변경 방법

특정 에이전트의 모델을 변경하려면:

```python
# 예: Coordinator Agent를 Claude 3로 변경
self.model = "anthropic/claude-3-opus"

# 예: Medical Expert를 GPT-4로 업그레이드
self.model = "gpt-4"
```

## 문제 해결

### 1. API 키 오류
```
ValueError: LANGDB_API_KEY and LANGDB_PROJECT_ID must be set
```
→ `.env` 파일에 LangDB 설정이 있는지 확인

### 2. 모델을 찾을 수 없음
```
Model not found: xxx
```
→ 올바른 모델 ID를 사용하는지 확인
→ 현재 LangDB에서 지원하는 모델:
  - OpenAI: `gpt-4`, `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
  - Anthropic: `claude-3-opus`, `claude-3-sonnet`, `claude-3-haiku`
  - 기타: 공식 문서에서 확인 필요

### 3. 추적이 작동하지 않음
```
pylangdb not installed, tracing will not be available
```
→ 정상적인 경고 메시지, 기능에는 영향 없음

## 추가 설정

### 디버그 모드
```python
self.agent = Agent(
    # ...
    show_tool_calls=True,  # Tool 호출 표시
    markdown=True,         # Markdown 포맷 사용
    debug_mode=True       # 디버그 정보 출력
)
```

### 커스텀 헤더
특별한 헤더가 필요한 경우:
```python
model=LangDB(
    id="모델명",
    api_key=self.langdb_api_key,
    project_id=self.langdb_project_id,
    default_headers={"Custom-Header": "value"}
)
```

## 참고 링크
- [LangDB Documentation](https://docs.langdb.ai/)
- [Agno Framework](https://github.com/agno-agi/agno)
- [OpenRouter Models](https://openrouter.ai/models)