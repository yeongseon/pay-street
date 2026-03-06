# PayStreet Content Engine

## 1. Overview

PayStreet Content Engine은  
직무, 연차, 지역, 기업 규모 등의 데이터를 기반으로  
자동으로 콘텐츠 주제를 생성하는 시스템이다.

이 시스템의 목적은 다음과 같다.

- 콘텐츠 주제 자동 생성
- 반복 가능한 콘텐츠 포맷 생성
- 콘텐츠 다양성 확보
- 숏폼 콘텐츠 대량 생산 지원

PayStreet Content Engine은  
데이터 기반 인터뷰 콘텐츠를 생성하는 핵심 시스템이다.

이 문서는 `PRD.md`의 `Topic Selection`, `ARCH.md`의 `Content Generation Pipeline` 시작 지점을 구체화한다.  
즉, 흐름은 다음과 같다.

```text
DATA.md
    ->
CONTENT_ENGINE.md
    ->
Script Generator
    ->
Voice Generator
    ->
Video Composer
```

---

## 2. Content Model

PayStreet 콘텐츠는 다음 구조를 가진다.

```text
Topic
→ Interview Script
→ Voice
→ Video
```

콘텐츠 생성의 시작점은 **Topic Engine**이다.

즉, `Script Generator`보다 앞단에서  
"어떤 주제를 만들 것인가"를 결정하는 계층이 Content Engine이다.

---

## 3. Content Types

PayStreet는 다음 콘텐츠 유형을 지원한다.

### 3.1 Salary Interview

가장 기본 콘텐츠

예

```text
4년차 백엔드 개발자 연봉 얼마예요
```

구조

```text
직무
연차
연봉
```

---

### 3.2 Salary Comparison

직무 또는 조건 비교

예

```text
스타트업 개발자 vs 대기업 개발자
```

또는

```text
서울 vs 지방 개발자 연봉
```

---

### 3.3 Career Reality

직무 현실 콘텐츠

예

```text
PM 현실
디자이너 스트레스
마케터 야근
```

---

### 3.4 Salary Range Content

연봉 범위 설명

예

```text
3년차 개발자 연봉 범위
```

이 분류는 `PRD.md`의 초기 콘텐츠 유형과 Future Expansion 방향을 반영한다.

---

## 4. Topic Generation

Topic Engine은 다음 변수를 기반으로 콘텐츠를 생성한다.

### Core Variables

```text
job_title
experience_years
region
company_size
industry
```

이 값들은 `DATA.md`의 정규화된 데이터 모델에서 공급받는다.

---

## 5. Example Topic Generation

Example 1

```text
4년차 백엔드 개발자 연봉 얼마예요
```

Example 2

```text
3년차 PM 연봉 얼마예요
```

Example 3

```text
판교 개발자 연봉 현실
```

생성된 Topic은 이후 `Salary Data Engine` 조회 조건으로 사용되고,  
가공된 `salary_range`와 함께 `Script Generator`로 전달된다.

---

## 6. Topic Template System

콘텐츠 주제는 템플릿 기반으로 생성한다.

### Template 1

```text
{experience}년차 {job_title} 연봉 얼마예요
```

---

### Template 2

```text
{region} {job_title} 연봉 현실
```

---

### Template 3

```text
{job_title} {experience}년차 연봉 범위
```

---

### Template 4

```text
{job_title} vs {job_title_2} 연봉 비교
```

이 구조는 `ARCH.md`의 비용 최적화 전략과도 일치한다.  
즉, 주제도 템플릿 기반으로 만들수록 반복 생산성과 운영 효율이 높아진다.

---

## 7. Topic Expansion

Topic Engine은 기본 주제를 확장할 수 있다.

### Example Expansion

Base

```text
Backend Developer
```

Expansion

```text
3년차 백엔드 개발자
4년차 백엔드 개발자
5년차 백엔드 개발자
```

---

또는

```text
서울 백엔드 개발자
판교 백엔드 개발자
```

이 확장 로직은 동일 직무를 여러 연차, 지역, 기업 규모 조합으로 변형해  
대량 Topic을 생성하는 핵심 메커니즘이다.

---

## 8. Content Volume Strategy

콘텐츠 생산 전략

예

직무

```text
30 jobs
```

연차

```text
1~10 years
```

지역

```text
5 regions
```

가능 콘텐츠 수

```text
30 × 10 × 5
= 1500 topics
```

이 구조는 `PRD.md`의 하루 20~50개 콘텐츠 생성 목표를 뒷받침한다.

---

## 9. Topic Scoring

모든 주제가 동일한 가치가 있는 것은 아니다.

Topic Engine은 다음 기준으로 점수를 계산한다.

### Scoring Factors

- 직무 인기
- 검색량
- 플랫폼 트렌드
- 콘텐츠 신선도

초기 MVP에서는 단순 규칙 기반 점수로 시작하고,  
후속 단계에서 성과 데이터 기반 최적화로 확장한다.

---

## 10. Topic Queue System

콘텐츠 생성 큐 시스템

```text
Topic Generator
↓
Topic Queue
↓
Content Pipeline
```

Queue 역할

- 콘텐츠 생성 순서 관리
- 중복 콘텐츠 방지
- 콘텐츠 생산 스케줄링

이 큐는 `ARCH.md`의 Task Queue 개념과 논리적으로 연결된다.  
다만 여기서는 "주제 큐"이고, 아키텍처 문서의 큐는 "렌더링 작업 큐"라는 점이 다르다.

---

## 11. Content Scheduling

콘텐츠 업로드 전략

예

```text
하루 3~5개 영상
```

주간 콘텐츠

```text
20~30 videos
```

이 스케줄링은 Topic Queue 우선순위와 게시 정책에 따라 운영된다.

---

## 12. Topic Deduplication

중복 콘텐츠 방지

예

```text
4년차 백엔드 개발자 연봉
```

이미 생성된 경우

```text
topic skip
```

중복 판정 기준은 `job_title`, `experience_years`, `region`, `content_type` 조합을 기본으로 한다.

---

## 13. Content Metadata

각 콘텐츠는 메타데이터를 가진다.

```text
topic_id
job_title
experience_years
region
content_type
created_at
published_at
```

필요 시 다음 필드를 추가할 수 있다.

```text
score
platform
template_id
status
```

---

## 14. Platform Optimization

플랫폼별 제목 최적화

### YouTube Shorts

```text
4년차 백엔드 개발자 연봉 얼마예요
```

---

### Instagram

```text
백엔드 개발자 연봉 현실
```

---

### TikTok

```text
개발자 연봉 공개
```

동일 Topic이라도 플랫폼별 훅 문구는 다르게 최적화할 수 있다.

---

## 15. Content Engine Workflow

Content Engine의 실제 흐름은 다음과 같다.

```text
Normalized Salary Data
    ↓
Topic Template Selection
    ↓
Topic Expansion
    ↓
Topic Scoring
    ↓
Topic Deduplication
    ↓
Topic Queue
    ↓
Script Generator Input
```

이 구조는 `DATA.md`의 정규화 데이터 계층과 `ARCH.md`의 콘텐츠 파이프라인 사이를 연결한다.

---

## 16. MVP Scope

MVP에서는 다음만 우선 지원한다.

- 콘텐츠 유형 2개: `Salary Interview`, `Salary Comparison`
- 템플릿 4개
- 연차, 직무, 지역 기반 Topic 생성
- 단순 규칙 기반 Topic Scoring
- 중복 Topic Skip
- 기본 Topic Queue

### MVP Out of Scope

- 실시간 트렌드 반영 자동화
- 외부 검색량 API 연동
- 성과 기반 추천 알고리즘
- AI 기반 주제 추천 개인화

---

## 17. Future Expansion

### Phase 2

직무 만족도 데이터 추가

```text
stress level
work-life balance
job stability
```

---

### Phase 3

직무 비교 콘텐츠

```text
Developer vs PM
```

---

### Phase 4

AI 콘텐츠 추천 시스템

```text
AI가 다음 콘텐츠 주제 추천
```

---

## 18. Conclusion

PayStreet Content Engine은  
데이터 기반 인터뷰 콘텐츠를 자동 생성하는 시스템이다.

이 시스템은 다음을 가능하게 한다.

- 콘텐츠 주제 자동 생성
- 콘텐츠 다양성 확보
- 숏폼 콘텐츠 대량 생산
- 채널 성장 가속

PayStreet에서는 영상 기술도 중요하지만,  
무엇을 만들지 결정하는 Content Engine이 실제 채널 성장의 핵심 레이어다.
