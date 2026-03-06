# PayStreet Schema

## 1. Overview

이 문서는 PayStreet MVP의 PostgreSQL 스키마를 정의한다.

---

## 2. Tables

### `salary_records`

필드

- `id` UUID PK
- `job_title` TEXT
- `experience_years` INT
- `region` TEXT
- `company_size` TEXT
- `industry` TEXT
- `salary_min` INT
- `salary_max` INT
- `currency` TEXT
- `source` TEXT
- `last_updated` DATE
- `created_at` TIMESTAMP

인덱스

- `(job_title, experience_years, region, company_size)`

### `job_titles`

- `id` UUID PK
- `name` TEXT UNIQUE
- `category` TEXT
- `description` TEXT
- `created_at` TIMESTAMP

### `regions`

- `id` UUID PK
- `name` TEXT
- `country` TEXT
- `region_type` TEXT
- `created_at` TIMESTAMP

### `content_topics`

- `id` UUID PK
- `content_type` TEXT
- `title` TEXT
- `job_title` TEXT
- `experience_years` INT NULL
- `region` TEXT NULL
- `company_size` TEXT NULL
- `industry` TEXT NULL
- `score` NUMERIC NULL
- `status` TEXT
- `created_at` TIMESTAMP
- `published_at` TIMESTAMP NULL

인덱스

- `(content_type, status)`
- `(job_title, experience_years, region)`

### `scripts`

- `id` UUID PK
- `topic_id` UUID FK -> `content_topics.id`
- `provider` TEXT
- `model` TEXT
- `prompt_version` TEXT
- `content` JSONB
- `status` TEXT
- `created_at` TIMESTAMP

### `audio_jobs`

- `id` UUID PK
- `script_id` UUID FK -> `scripts.id`
- `provider` TEXT
- `status` TEXT
- `interviewer_path` TEXT
- `interviewee_path` TEXT
- `created_at` TIMESTAMP

### `subtitle_assets`

- `id` UUID PK
- `script_id` UUID FK -> `scripts.id`
- `audio_job_id` UUID FK -> `audio_jobs.id`
- `format` TEXT
- `file_path` TEXT
- `status` TEXT
- `created_at` TIMESTAMP

### `render_jobs`

- `id` UUID PK
- `topic_id` UUID FK -> `content_topics.id`
- `script_id` UUID FK -> `scripts.id`
- `audio_job_id` UUID FK -> `audio_jobs.id`
- `subtitle_id` UUID FK -> `subtitle_assets.id`
- `template_id` TEXT
- `status` TEXT
- `output_path` TEXT
- `error_message` TEXT NULL
- `created_at` TIMESTAMP
- `completed_at` TIMESTAMP NULL

### `job_events`

- `id` UUID PK
- `job_type` TEXT
- `job_id` UUID
- `event_type` TEXT
- `payload` JSONB
- `created_at` TIMESTAMP

---

## 3. Status Values

공통 상태값 예시

- `PENDING`
- `QUEUED`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `SKIPPED`

---

## 4. Constraints

- `salary_min < salary_max`
- `experience_years BETWEEN 0 AND 20`
- `salary_max < salary_min * 2`

