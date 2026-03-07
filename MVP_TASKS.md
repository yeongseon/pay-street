# PayStreet MVP Tasks

## 1. Foundation

- Python 프로젝트 초기화
- `.venv` 생성 및 활성화 규칙 문서화
- `pyproject.toml` 설정
- `.env.example` 작성
- Docker Compose 또는 Podman Compose 구성
- FastAPI 앱 엔트리포인트 생성
- Celery worker 엔트리포인트 생성

## 2. Data

- PostgreSQL 스키마 생성
- salary data import 스크립트 작성
- job title normalization 구현
- region normalization 구현
- salary range calculation 구현
- repository 계층 작성

## 3. Content Engine

- topic template 정의
- topic generator 구현
- topic expander 구현
- topic scoring 구현
- topic deduplication 구현
- topic queue 테이블 및 상태값 정의

## 4. Script

- prompt template 작성
- LLM adapter 인터페이스 정의
- OpenAI adapter 구현
- fallback mock adapter 구현
- script validation 구현

## 5. Voice

- TTS adapter 인터페이스 정의
- primary provider adapter 구현
- local/fallback adapter 구현
- 화자 2종 출력 구조 정의

## 6. Subtitle

- subtitle segmentation 구현
- srt writer 구현
- keyword highlighting metadata 생성

## 7. Video

- `street_interview_v1.yaml` 작성
- scene planner 구현
- timeline builder 구현
- layer resolver 구현
- ffmpeg render command builder 구현
- final export 구현

## 8. Operations

- job status tracking
- retry 정책
- 로그 디렉토리 구조
- 로컬 CLI 또는 admin endpoint

## 9. Verification

- topic generation test
- salary range calculation test
- script formatting test
- render smoke test
- end-to-end local pipeline test
