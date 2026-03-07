# PayStreet Implementation Plan

## 1. Overview

이 문서는 PayStreet MVP를 실제로 구현하기 위한 단계별 실행 계획을 정의한다.

기준 문서

- `PRD.md`
- `ARCH.md`
- `DATA.md`
- `CONTENT_ENGINE.md`
- `VIDEO_TEMPLATE_SYSTEM.md`
- `LOCAL_SETUP.md`

핵심 원칙

- local-first
- vendor-neutral
- template-based video composition
- batch-oriented content pipeline

---

## 2. MVP Goal

MVP의 목표는 다음 한 줄로 요약된다.

```text
정규화된 연봉 데이터를 기반으로
주제를 생성하고
인터뷰 대본, 음성, 자막, 템플릿 영상을 조립해
20~40초 숏폼 mp4를 로컬에서 반복 생성한다.
```

---

## 3. Delivery Phases

### Phase 1. Foundation

- Python 프로젝트 초기화
- `.venv` 기반 개발 환경 구성
- FastAPI 기본 서버 구성
- PostgreSQL/Redis 연결
- Docker Compose 또는 Podman Compose 로컬 실행 환경 구성
- 기본 설정 파일 구조 확정

### Phase 2. Data Layer

- `salary_records`, `job_titles`, `regions`, `content_topics` 테이블 생성
- 데이터 import 스크립트 작성
- 정규화 로직 구현
- `Salary Data Engine` 조회 API 구현

### Phase 3. Content Engine

- Topic template 정의
- Topic expansion 로직 구현
- Topic deduplication 구현
- Topic scoring 구현
- Topic queue 저장 및 조회 구현

### Phase 4. Script and Voice

- Script Generator 프롬프트 구현
- LLM provider adapter 구현
- TTS provider adapter 구현
- 스크립트/오디오 산출물 저장 구조 구현

### Phase 5. Subtitle and Video

- Subtitle segmentation 구현
- `street_interview_v1` 템플릿 구현
- Timeline builder 구현
- Render engine 구현
- mp4 export 구현

### Phase 6. Operations

- 작업 상태 추적
- 재시도 로직
- 로그 구조
- 운영용 CLI 또는 내부 API

---

## 4. Recommended Build Order

1. 로컬 실행 환경
2. DB 스키마
3. Salary Data Engine
4. Topic Engine
5. Script Generator
6. TTS
7. Subtitle Generator
8. Video Composer
9. Export pipeline
10. 운영/모니터링

---

## 5. MVP Deliverables

- 로컬에서 실행되는 FastAPI 서버
- 로컬에서 실행되는 Celery worker
- PostgreSQL 기반 데이터 계층
- 최소 1개 템플릿 기반 영상 렌더링
- topic -> script -> audio -> subtitle -> video 전체 파이프라인
- 20~40초 mp4 결과물

---

## 6. Technical Milestones

### Milestone 1

`docker compose up` 또는 `podman compose up`으로 API, Redis, PostgreSQL, Worker가 기동된다.

### Milestone 2

정규화된 salary data를 조회해 `salary_range`를 반환할 수 있다.

### Milestone 3

Content Engine이 topic을 자동 생성하고 큐에 넣을 수 있다.

### Milestone 4

Script Generator가 인터뷰형 스크립트를 생성한다.

### Milestone 5

TTS와 subtitle 결과물이 생성된다.

### Milestone 6

`street_interview_v1` 템플릿으로 최종 mp4가 렌더링된다.

---

## 7. Risks

- 데이터 품질 부족
- LLM 출력 품질 불안정
- TTS 비용 증가
- FFmpeg 렌더링 속도 저하
- 모든 영상이 비슷해 보이는 문제

---

## 8. Success Criteria

- 하루 20개 이상 영상 생성 가능
- 동일 입력에 대해 일관된 형식 출력
- 렌더 작업 성공률 90% 이상
- 사람이 손으로 영상 편집하지 않고도 usable 결과물 확보
