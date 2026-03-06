# PayStreet Data Architecture

## 1. Overview

PayStreet는 직무, 연차, 지역, 기업 규모 등의 연봉 데이터를 기반으로  
인터뷰 스타일 콘텐츠를 생성하는 시스템이다.

따라서 데이터 시스템은 다음 목표를 가진다.

- 신뢰 가능한 연봉 데이터 확보
- 범위 기반 연봉 데이터 제공
- 직무/연차 기반 콘텐츠 생성 지원
- 데이터 업데이트 가능 구조

PayStreet의 데이터 시스템은 **Salary Knowledge Base** 역할을 한다.

---

## 2. Data Sources

PayStreet는 여러 공개 데이터 소스를 결합하여 연봉 데이터를 구축한다.

### 2.1 Government Data

대표적인 공공 데이터

- 고용노동부 임금직무정보
- 통계청 임금구조 기본통계
- 한국고용정보원 직무 임금 데이터

이 데이터는 다음 정보를 제공한다.

- 직무 평균 임금
- 연차별 임금
- 산업별 임금
- 지역별 임금

장점

- 신뢰성 높음
- 공식 통계 기반

단점

- 최신성이 낮을 수 있음
- 직무 분류가 거칠 수 있음

---

### 2.2 Career Platforms

채용 플랫폼 평균 연봉 데이터

예

- 잡코리아
- 사람인
- 원티드
- 로켓펀치

제공 정보

- 기업 평균 연봉
- 직무 평균 연봉
- 연차별 연봉 범위

장점

- 비교적 최신 데이터

단점

- 데이터 편향 가능

---

### 2.3 Corporate Data

상장기업 사업보고서

예

- 평균 급여
- 직원 수
- 산업 분류

장점

- 실제 기업 데이터

단점

- 직무별 구분 없음

---

## 3. Data Strategy

PayStreet는 **정확한 연봉 수치 대신 범위 기반 데이터**를 사용한다.

예

```text
6500만원
```

대신

```text
6500 ~ 7500만원
```

이 방식의 장점

- 현실적인 표현
- 데이터 오류 감소
- 콘텐츠 신뢰도 향상

또한 문서 간 역할은 다음과 같이 구분한다.

- 내부 저장 모델: `salary_min`, `salary_max`
- 콘텐츠 생성 인터페이스: `salary_range`

즉 `ARCH.md`의 `Salary Data Engine`은 내부적으로 `salary_min`, `salary_max`를 저장하고,  
`PRD.md`의 `Script Generator`에는 `salary_range` 형태로 가공된 값을 전달한다.

---

## 4. Core Data Model

PayStreet 데이터 모델은 다음 구조를 가진다.

### SalaryRecord

```text
job_title
experience_years
region
company_size
industry
salary_min
salary_max
currency
source
last_updated
```

### Example

```yaml
job_title: Backend Developer
experience_years: 4
region: Pangyo
company_size: Large
industry: IT
salary_min: 6500
salary_max: 7500
currency: KRW
source: gov_stats
last_updated: 2026-01-10
```

---

## 5. Supporting Data Tables

### Job Title Table

직무 정규화 테이블

```text
job_id
job_title
job_category
description
```

Example

```yaml
job_id: 101
job_title: Backend Developer
job_category: Software Engineering
```

---

### Region Table

지역 데이터

```text
region_id
region_name
country
region_type
```

Example

```yaml
region_name: Pangyo
country: Korea
region_type: Tech Hub
```

---

### Company Size Table

기업 규모

```text
company_size_id
size_name
employee_range
```

Example

```text
Large
1000+
```

---

## 6. Data Normalization

데이터 정규화는 다음 기준을 따른다.

### Job Title Normalization

다양한 직무명을 통합한다.

예

```text
Backend Developer
Backend Engineer
Server Developer
```

→

```text
Backend Developer
```

---

### Region Normalization

예

```text
Seoul
Gangnam
Pangyo
```

→

```text
Seoul Metro
```

---

### Salary Normalization

모든 연봉은 다음 기준으로 통일한다.

- 연 단위
- 세전
- KRW 기준

---

## 7. Data Ingestion Pipeline

데이터 수집 파이프라인

```text
Data Source
↓
Data Collection
↓
Data Cleaning
↓
Normalization
↓
Salary Range Calculation
↓
Database Storage
```

이 파이프라인은 `ARCH.md`의 `Salary Data Engine`에 해당한다.

---

## 8. Salary Range Calculation

연봉 범위 계산 방법

### Method 1

평균 ± 표준편차

예

```text
평균 7000
표준편차 500
```

→

```text
6500 ~ 7500
```

---

### Method 2

Percentile 기반

예

```text
25% percentile
75% percentile
```

→

```text
salary_min
salary_max
```

---

## 9. Content Data Interface

콘텐츠 생성 엔진은 다음 데이터만 사용한다.

```text
job_title
experience_years
salary_range
region
company_type
```

Example

```text
Backend Developer
4 years
6500 ~ 7500
Pangyo
Large company
```

이 데이터는 `PRD.md`와 `ARCH.md`에서 정의된 `Script Generator`에 전달된다.

---

## 10. Data Quality Rules

데이터 품질 기준

### Rule 1

`salary_min < salary_max`

---

### Rule 2

`salary_max < 2 × salary_min`

비현실적 데이터 제거

---

### Rule 3

연차 범위 제한

```text
0 ~ 20 years
```

---

## 11. Database Architecture

추천 DB

```text
PostgreSQL
```

이유

- 구조화 데이터
- 확장 가능
- JSON 지원

이 선택은 `ARCH.md`의 추천 DB와도 일치한다.

---

## 12. Example Tables

### salary_records

```text
id
job_title
experience_years
region
company_size
salary_min
salary_max
industry
source
last_updated
```

---

### job_titles

```text
id
name
category
```

---

### regions

```text
id
name
country
```

---

## 13. Data Update Strategy

데이터 업데이트 방식

### Manual Update

분기별 데이터 업데이트

---

### Automated Update

크롤링 기반 업데이트

예

- 채용 플랫폼 데이터
- 공개 보고서

---

## 14. Transparency Policy

PayStreet 콘텐츠는 데이터 기반 인터뷰이다.

콘텐츠 설명에 다음을 명시한다.

```text
Salary ranges are based on public data sources.
This interview is a simulated reconstruction.
```

이 정책은 `PRD.md`의 `Misleading Content`, `Data Accuracy` 리스크 대응과 연결된다.

---

## 15. Future Expansion

### Phase 2

직무 만족도 데이터

예

```text
stress level
work-life balance
job stability
```

---

### Phase 3

직무 비교 데이터

예

```text
Backend Developer vs PM
```

---

### Phase 4

Salary Intelligence Platform

---

## 16. Document Fit

PayStreet 문서 구조는 다음과 같이 정리된다.

```text
PRD.md
ARCH.md
DATA.md
VIDEO_TEMPLATE_SYSTEM.md
```

이 4개 문서가 함께 있을 때 제품 요구사항, 전체 시스템 구조, 데이터 계층, 영상 조립 계층이 모두 연결된다.
