# PayStreet API Spec

## 1. Overview

PayStreet API는 로컬 운영 기준의 내부 API다.

기본 경로

```text
/api/v1
```

응답 형식

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

---

## 2. Health

### `GET /health`

시스템 상태 확인

Response

```json
{
  "success": true,
  "data": {
    "status": "ok"
  },
  "error": null
}
```

---

## 3. Salary Data

### `GET /salary-records`

Query

- `job_title`
- `experience_years`
- `region`
- `company_size`

Response

```json
{
  "success": true,
  "data": {
    "job_title": "Backend Developer",
    "experience_years": 4,
    "region": "Pangyo",
    "company_size": "Large",
    "salary_min": 6500,
    "salary_max": 7500,
    "salary_range": "6500 ~ 7500"
  },
  "error": null
}
```

---

## 4. Topics

### `POST /topics/generate`

Body

```json
{
  "content_type": "salary_interview",
  "job_title": "Backend Developer",
  "region": "Pangyo",
  "experience_range": [3, 5],
  "company_size": "Large",
  "limit": 10
}
```

### `GET /topics`

생성된 topic 목록 조회

### `POST /topics/{topic_id}/enqueue`

특정 topic을 content pipeline 큐에 넣음

---

## 5. Scripts

### `POST /scripts/generate`

Body

```json
{
  "topic_id": "topic_001"
}
```

### `GET /scripts/{script_id}`

스크립트 조회

---

## 6. Audio

### `POST /audio/generate`

Body

```json
{
  "script_id": "script_001",
  "voice_provider": "primary"
}
```

### `GET /audio/{audio_job_id}`

오디오 생성 작업 상태 조회

---

## 7. Subtitles

### `POST /subtitles/generate`

Body

```json
{
  "script_id": "script_001",
  "audio_job_id": "audio_001"
}
```

### `GET /subtitles/{subtitle_id}`

자막 결과 조회

---

## 8. Renders

### `POST /renders/create`

Body

```json
{
  "topic_id": "topic_001",
  "script_id": "script_001",
  "audio_job_id": "audio_001",
  "subtitle_id": "subtitle_001",
  "template_id": "street_interview_v1"
}
```

### `GET /renders/{render_job_id}`

렌더 작업 상태 조회

### `POST /renders/{render_job_id}/retry`

실패한 렌더 작업 재시도

---

## 9. Full Pipeline

### `POST /pipeline/run`

단일 topic 기준 전체 파이프라인 실행

Body

```json
{
  "topic_id": "topic_001",
  "template_id": "street_interview_v1"
}
```

### `POST /pipeline/batch-run`

여러 topic을 배치로 실행

---

## 10. Admin

### `GET /jobs`

전체 작업 목록 조회

### `GET /metrics`

기본 운영 지표 조회

