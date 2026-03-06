# PayStreet Architecture

## 1. Overview

PayStreet는 공개된 연봉 데이터를 기반으로  
인터뷰 스타일의 숏폼 콘텐츠를 자동 생성하는 **AI 콘텐츠 파이프라인 시스템**이다.

PayStreet는 AI 모델 중심 서비스가 아니라  
**Content Generation Pipeline** 중심 시스템이다.

### 핵심 목표

- 데이터 기반 인터뷰 콘텐츠 생성
- 숏폼 콘텐츠 자동 생성
- 콘텐츠 생산 자동화

### 출력 콘텐츠

- YouTube Shorts
- Instagram Reels
- TikTok

---

## 2. High Level Architecture

전체 시스템 구조

```text
Salary Data Store
│
▼
Script Generator (LLM)
│
▼
Voice Generator (TTS)
│
▼
Video Composer
(FFmpeg / OpenCV)
│
▼
Subtitle Generator
│
▼
Shorts Export Engine
│
▼
Publishing Engine
```

---

## 3. System Components

### 3.1 Salary Data Engine

연봉 데이터를 저장하고 조회하는 시스템

#### Data Sources

- 고용노동부 임금 데이터
- 통계청 임금 데이터
- 채용 플랫폼 평균 연봉
- 기업 사업보고서 평균 급여

#### Data Model

```text
job_title
experience_years
region
company_size
salary_min
salary_max
industry
```

#### Example

```yaml
job_title: Backend Developer
experience_years: 4
region: Pangyo
company_size: Large
salary_min: 6500
salary_max: 7500
```

---

### 3.2 Script Generator

LLM 기반 인터뷰 대본 생성 모듈

#### Input

```text
job_title
experience_years
salary_range
region
tone
```

#### Output Example

```text
Q: 무슨 일 하세요?

A: 판교에서 백엔드 개발자로 일하고 있고
4년차입니다.

Q: 연봉은 어느 정도 되세요?

A: 세전 기준 약 7천 정도 됩니다.
```

#### Recommended LLM

- OpenAI
- Anthropic
- Google

---

### 3.3 Voice Generator

인터뷰 음성 생성

두 화자 필요

- Interviewer
- Interviewee

#### Output

```text
interviewer.wav
interviewee.wav
```

#### Recommended APIs

- ElevenLabs
- Azure TTS
- OpenAI TTS

---

### 3.4 Video Composer

영상 조립 시스템

PayStreet에서 **가장 핵심 모듈**

AI 영상 생성이 아니라 **템플릿 기반 영상 합성 방식**

#### 기능

- 템플릿 기반 인터뷰 영상 조립
- 인터뷰 대상 모자이크
- 자막 합성
- 숏폼 영상 렌더링

#### Pipeline

```text
Background Video
+
Interview Audio
+
Character Overlay
+
Face Mosaic
+
Subtitle Overlay
```

#### Tools

- FFmpeg
- OpenCV

#### Output

```text
video.mp4
```

---

### 3.5 Subtitle Generator

자동 자막 생성 시스템

#### Input

```text
script
audio
```

#### Output

```text
subtitle.srt
```

Subtitle 특징

- 연봉 강조
- 직무 강조
- Shorts 스타일

---

### 3.6 Shorts Export Engine

숏폼 플랫폼에 맞게 영상 변환

#### Requirements

```text
Aspect Ratio: 9:16
Resolution: 1080x1920
Duration: 20 ~ 40 sec
Format: mp4
```

---

### 3.7 Publishing Engine

콘텐츠 업로드 시스템

지원 플랫폼

- YouTube Shorts
- Instagram Reels
- TikTok

#### Upload Options

- Manual upload
- API upload

---

## 4. Content Generation Pipeline

콘텐츠 생성 흐름

```text
Topic Selection
│
▼
Salary Data Retrieval
│
▼
Script Generation
│
▼
Voice Generation
│
▼
Video Composition
│
▼
Subtitle Generation
│
▼
Shorts Export
│
▼
Publishing
```

---

## 5. Storage Architecture

### Database

연봉 데이터 저장

추천

```text
PostgreSQL
or
SQLite
```

### Media Storage

생성된 미디어 저장

추천

```text
Local filesystem
S3-compatible object storage
Azure Blob-compatible adapter
```

기본 운영은 로컬 파일시스템 기준으로 한다.

예

```text
assets/
outputs/
temp/
exports/
```

클라우드로 확장하더라도 특정 벤더 SDK에 직접 종속되지 않고,  
파일 저장 인터페이스를 통해 S3 호환 스토리지 또는 다른 오브젝트 스토리지로 교체 가능하도록 설계한다.

---

## 6. Compute Architecture

영상 조립과 렌더링은 CPU 작업이 많다.

추천 구조

```text
API Server (FastAPI)
│
▼
Task Queue (Redis)
│
▼
Worker Nodes
```

#### Example Stack

- FastAPI
- Celery
- Redis
- Docker or Podman

기본 운영 환경은 로컬 머신 또는 로컬 서버다.

---

## 7. Deployment Principle

PayStreet는 **Local-first**로 운영한다.

즉 초기 MVP는 클라우드 서비스 의존 없이 한 대의 로컬 머신 또는 사내 서버에서 실행 가능해야 한다.

### Local-first Principle

- API 서버는 로컬에서 실행
- Worker는 로컬에서 실행
- DB와 Queue도 로컬에서 실행
- 미디어 파일은 로컬 디스크에 저장
- 모든 파이프라인은 인터넷 없이도 기본 동작 가능해야 함

### Vendor-neutral Principle

클라우드로 확장하더라도 벤더 락인이 없도록 다음 원칙을 따른다.

- 스토리지는 추상화된 파일 저장 인터페이스 사용
- LLM/TTS는 provider adapter 패턴 사용
- DB는 PostgreSQL 표준 기능 위주 사용
- 메시지 큐는 Redis 기반 공통 패턴 유지
- 컨테이너 실행은 Docker Compose 또는 Podman Compose 기준으로 정의

즉, 특정 클라우드 서비스의 고유 기능에 의존하지 않고  
로컬 -> VPS -> 어느 클라우드로도 이동 가능한 구조를 목표로 한다.

---

## 8. Why Python

PayStreet에서 실제로 수행하는 핵심 작업은 다음과 같다.

```text
데이터 처리
↓
LLM 호출
↓
TTS 호출
↓
영상 합성
↓
자막 생성
↓
영상 렌더링
```

이 구조에서 중요한 부분은 다음 세 가지다.

- 영상 처리
- AI API 연동
- 데이터 파이프라인

Python은 이 세 영역에 모두 강하다.

### 7.1 AI API 연동

대부분의 AI API는 Python SDK 지원이 가장 좋다.

예:

- OpenAI
- Anthropic
- ElevenLabs

예시:

```python
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    input="Generate interview script"
)
```

### 7.2 영상 처리

Python은 영상 처리 라이브러리 생태계가 강하다.

예:

- FFmpeg
- OpenCV
- moviepy

예시:

```python
import cv2
import subprocess
```

### 7.3 파이프라인 처리

콘텐츠 생성은 일반적으로 batch pipeline 구조다. Python은 비동기 작업, 큐 처리, 워커 기반 파이프라인 구축에 적합하다.

예:

- Celery
- RQ
- Airflow
- Prefect

---

## 9. Recommended Tech Stack

PayStreet의 추천 스택은 다음과 같다.

### Backend

- FastAPI

### Worker

- Celery
- Redis

### Video

- FFmpeg
- OpenCV

### AI

- OpenAI
- ElevenLabs

### Database

- PostgreSQL

### Storage

- Local filesystem
- S3-compatible object storage

---

## 10. Runtime Architecture

Python 중심 시스템 구조는 다음과 같다.

```text
FastAPI
      │
      ▼
Task Queue
      │
      ▼
Worker
      │
      ▼
Video Rendering
```

로컬 운영 기준 예시는 다음과 같다.

```text
FastAPI (localhost)
      │
      ▼
Redis (localhost)
      │
      ▼
Celery Worker (localhost)
      │
      ▼
FFmpeg / OpenCV
      │
      ▼
PostgreSQL (localhost)
      │
      ▼
Local Storage (assets/, outputs/)
```

---

## 11. Project Structure Example

Python 프로젝트 기준으로는 다음과 같은 구조가 적합하다.

```text
paystreet/

app/
    api/
    services/
    models/
    pipelines/

video/
    composer.py
    subtitle.py

ai/
    llm.py
    tts.py

data/
    salary_repository.py

workers/
    video_worker.py
```

---

## 12. Why Not Node.js

Node.js로도 구현은 가능하지만, 이 프로젝트에서는 Python이 더 적합하다.

이유:

- 영상 처리 생태계
- AI 파이프라인 연동
- 데이터 처리 및 배치 작업

이 세 분야는 Python이 더 강하다.

---

## 13. Cost Optimization Strategy

AI 비용 최소화 전략

### Strategy

1. Script Template 사용
2. LLM 호출 최소화
3. 동일 구조 콘텐츠 생성

#### Example

```text
script template
+
salary data
```

---

## 14. Scalability

콘텐츠 생성은 병렬 처리 가능

Worker Pool  
Queue System

예

```text
10 workers
→ 동시에 10개 영상 생성
```

---

## 15. Security and Transparency

AI 재연 인터뷰가 실제 인터뷰로 오해될 수 있음

대응

- 콘텐츠 설명에 데이터 기반 인터뷰 명시
- 연봉 데이터 범위 기반 사용
- 데이터 출처 표시

---

## 16. Future Architecture

### Phase 2

Career Content Engine

Example

```text
developer daily life
pm reality
designer stress
```

### Phase 3

Salary Data Platform

### Phase 4

Content Generation SaaS

---

## 핵심 아키텍처 포인트

PayStreet는

```text
AI 서비스
❌

콘텐츠 자동 생성 파이프라인
⭕
```

즉 핵심은

- 데이터
- 영상 조립
- 자동화 파이프라인

추가로, PayStreet에 가장 적합한 기본 기술 조합은 다음과 같다.

```text
Python
+
FastAPI
+
FFmpeg
```
