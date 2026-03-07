# PayStreet Local Setup

## 1. Overview

PayStreet는 초기 운영 환경을 **local-first**로 설계한다.

즉, MVP 단계에서는 클라우드 인프라 없이도 한 대의 개발 머신 또는 로컬 서버에서 다음 구성 요소를 모두 실행할 수 있어야 한다.

- API 서버
- 작업 큐
- Worker
- 데이터베이스
- 미디어 스토리지
- 렌더링 파이프라인

이 문서는 PayStreet를 로컬에서 운영하기 위한 기본 실행 구조를 정의한다.

---

## 2. Local-first Principle

PayStreet는 다음 원칙을 따른다.

- 기본 실행 환경은 로컬 머신이다.
- 클라우드 없이도 전체 파이프라인이 동작해야 한다.
- 생성된 미디어는 로컬 디스크에 저장한다.
- 외부 API는 선택적으로만 사용한다.
- 인프라 구조는 이후 VPS 또는 클라우드로 그대로 이동 가능해야 한다.

---

## 3. Local Runtime Architecture

```text
FastAPI
    ->
Redis
    ->
Celery Worker
    ->
FFmpeg / OpenCV
    ->
PostgreSQL
    ->
Local Storage
```

각 구성 요소의 역할은 다음과 같다.

- `FastAPI`: API 요청 처리, 렌더 작업 생성
- `Redis`: 작업 큐
- `Celery Worker`: 스크립트 생성, 음성 생성, 렌더링 작업 실행
- `FFmpeg / OpenCV`: 영상 조립 및 렌더링
- `PostgreSQL`: 데이터와 작업 메타데이터 저장
- `Local Storage`: 자산, 오디오, 자막, 최종 영상 저장

---

## 4. Recommended Local Stack

- Python
- FastAPI
- Celery
- Redis
- PostgreSQL
- FFmpeg
- OpenCV
- Docker Compose or Podman Compose

선택적 외부 API

- OpenAI
- ElevenLabs

오픈소스 대체 가능 옵션

- LLM: Ollama, vLLM
- TTS: Piper, Coqui TTS

---

## 5. Python Virtual Environment

PayStreet의 개발 환경은 반드시 **virtualenv 기반**으로 구성한다.

모든 Python 명령 실행 기준

- 패키지 설치
- 테스트 실행
- Alembic 마이그레이션
- seed script 실행
- FastAPI 실행
- Celery worker 실행

모두 `.venv` 안에서 수행해야 한다.

### Recommended Commands

Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .[dev]
```

### Execution Rule

다음 형태로 실행하는 것을 기본 규칙으로 한다.

```text
.venv activated
    ->
python -m ...
```

예

```bash
python -m pytest
python -m uvicorn paystreet.app.main:app --reload
python -m alembic upgrade head
python -m paystreet.scripts.seed_data
```

---

## 6. Local Storage Layout

로컬 스토리지는 파일 기반으로 운영한다.

```text
paystreet/
  assets/
  data/
  outputs/
  exports/
  temp/
  logs/
```

### Directory Roles

- `assets/`: 배경, 로고, 실루엣, 카드 UI 등 정적 자산
- `data/`: 입력 데이터, import 파일, 캐시 데이터
- `outputs/`: 렌더링 중간 산출물
- `exports/`: 최종 mp4 결과물
- `temp/`: 임시 오디오, 자막, 작업 파일
- `logs/`: 작업 로그

---

## 7. Container Runtime Strategy

로컬 운영은 `Docker Compose` 기준으로 설계하는 것이 가장 단순하다.

단, macOS에서 Docker가 없으면 `Podman`과 `podman compose`를 대체 런타임으로 사용한다.

권장 기준

- Linux: Docker 우선
- macOS: Docker 우선, 없으면 Podman 사용

### Recommended Services

- `api`
- `worker`
- `redis`
- `postgres`

### Optional Host-level Dependencies

- FFmpeg
- OpenCV runtime

필요 시 `worker` 이미지 안에 FFmpeg를 포함할 수 있다.

---

## 8. Vendor-neutral Principle

PayStreet는 이후 클라우드로 이동하더라도 벤더 락인이 없도록 설계한다.

### Rules

- 스토리지는 로컬 파일시스템 인터페이스를 기본으로 둔다.
- 오브젝트 스토리지는 adapter로 연결한다.
- LLM/TTS는 provider별 wrapper를 둔다.
- PostgreSQL 표준 SQL 위주로 설계한다.
- Docker Compose 또는 Podman Compose 기반 구조를 유지해 어느 VM에서도 실행 가능하게 한다.

### Storage Abstraction Example

```text
Storage Interface
    ->
Local File Storage
or
S3-compatible Storage
or
Other Object Storage
```

### AI Provider Abstraction Example

```text
LLM Interface
    ->
OpenAI Adapter
or
Anthropic Adapter
or
Local Model Adapter
```

---

## 9. Local Operations Model

로컬 운영 기준 기본 흐름은 다음과 같다.

1. Topic 생성
2. Salary data 조회
3. Script 생성
4. TTS 생성
5. Subtitle 생성
6. Video composition
7. 최종 영상 저장

운영자는 로컬 API 또는 CLI를 통해 작업을 실행할 수 있다.

---

## 10. Migration Path

로컬에서 시작한 뒤 다음 단계로 확장할 수 있다.

### Stage 1

로컬 개발 머신

### Stage 2

로컬 전용 서버 또는 사내 NAS/워크스테이션

### Stage 3

일반 VPS 또는 VM

### Stage 4

클라우드 인프라

이 과정에서도 코드 구조는 동일하게 유지하고,  
변경되는 것은 주로 실행 환경과 스토리지 adapter뿐이다.

---

## 11. MVP Recommendation

초기 MVP는 다음 구성이 가장 현실적이다.

- `FastAPI` 로컬 실행
- `Redis` 로컬 실행
- `Celery Worker` 로컬 실행
- `PostgreSQL` 로컬 실행
- `FFmpeg` 로컬 설치
- `.venv` 활성화 상태에서 모든 Python 작업 실행
- `outputs/`, `exports/` 폴더 기반 결과 저장

이 구성만으로도 PayStreet의 데이터, 콘텐츠 생성, 영상 조립 파이프라인을 모두 테스트할 수 있다.

---

## 12. Conclusion

PayStreet는 초기부터 클라우드 의존적으로 설계할 필요가 없다.

가장 좋은 시작점은 `local-first + vendor-neutral` 구조다.

이 방식은 다음 장점을 가진다.

- 초기 비용 절감
- 개발 및 디버깅 속도 향상
- 렌더링 파이프라인 검증 용이
- 이후 클라우드 이전 시 구조 변경 최소화

즉, PayStreet는 로컬에서 충분히 운영 가능해야 하며,  
필요할 때만 환경을 확장하는 방식이 가장 현실적이다.
