# PayStreet PRD

## 1. Overview

PayStreet는 공개된 연봉 및 커리어 데이터를 기반으로, "길거리 인터뷰 스타일"의 숏폼 콘텐츠를 자동 생성하는 AI 콘텐츠 엔진이다.

이 시스템은 실제 인터뷰를 촬영하는 방식이 아니라, 데이터 기반 재연 인터뷰(Data-driven Simulated Interview) 방식으로 콘텐츠를 생성한다. 핵심 목적은 연봉, 직무, 커리어 정보를 짧고 흥미로운 엔터테인먼트형 콘텐츠로 재구성해 대량 생산 가능한 파이프라인을 만드는 것이다.

생성된 콘텐츠는 다음 플랫폼 배포를 기본 전제로 한다.

- YouTube Shorts
- Instagram Reels
- TikTok

초기 단계의 PayStreet는 "콘텐츠 생성 엔진 구축"과 "채널 운영 자동화"에 집중하며, SaaS화는 Future Phase에서만 검토한다.

## 2. Problem Statement

취업 준비생, 직장인, 커리어 전환 고민 사용자들은 다음과 같은 정보를 지속적으로 궁금해한다.

- 직무별 연봉
- 연차별 연봉
- 대기업 vs 스타트업 연봉 차이
- 지역별 연봉 차이
- 직무 현실 및 커리어 정보

하지만 현재 시장의 정보 제공 방식에는 다음과 같은 문제가 있다.

- 대부분 텍스트 중심이라 소비성이 낮다.
- 실제 인터뷰 기반 콘텐츠는 제작 비용과 시간이 많이 든다.
- 데이터 기반 커리어 숏폼 콘텐츠가 충분히 많지 않다.
- 공개된 데이터를 엔터테인먼트형 콘텐츠로 가공하는 시스템이 부족하다.

따라서 PayStreet는 공개 데이터 기반의 인터뷰형 숏폼 콘텐츠를 자동 생성하는 시스템을 구축해, 정보성과 대중성을 동시에 확보하는 것을 목표로 한다.

## 3. Goals

### Primary Goals

- 데이터 기반 연봉 인터뷰 콘텐츠 생성
- Shorts/Reels/TikTok용 숏폼 영상 자동 조립 및 렌더링
- 반복 가능한 콘텐츠 생산 자동화 파이프라인 구축

### Secondary Goals

- 커리어 정보 기반 콘텐츠 채널 운영
- 직무 현실, 커리어 비교 콘텐츠로 주제 확장
- 향후 데이터 기반 직무 콘텐츠 플랫폼의 기반 확보

## 4. Non Goals

초기 MVP에서 다음은 목표 범위에 포함하지 않는다.

- 사용자 생성 콘텐츠 플랫폼
- 커뮤니티 기능
- 실시간 인터뷰 기능
- B2C/B2B SaaS 판매

PayStreet의 초기 목표는 어디까지나 "콘텐츠 생성 엔진"을 안정적으로 만드는 것이다.

## 5. Target Audience

### Primary Audience

- 취업 준비생
- 직장인
- 이직 또는 커리어 전환을 고민하는 사용자

### Secondary Audience

- 직무 정보에 관심 있는 일반 사용자
- 연봉/회사 문화/직무 현실 콘텐츠를 즐기는 숏폼 소비자

## 6. Core Product Concept

PayStreet는 데이터 기반 재연 인터뷰 형식의 콘텐츠를 생성한다.

### Example Format

**Intro**

> "4년차 백엔드 개발자 연봉 얼마예요?"

**Interview**

Q: 무슨 일 하세요?  
A: 판교에서 백엔드 개발자로 일하고 있습니다.

Q: 몇 년 차세요?  
A: 4년차입니다.

Q: 연봉은 어느 정도 되세요?  
A: 세전 기준 약 7천 정도 됩니다.

**Outro**

> "여러분 연봉은 어떤가요?"

### Format Characteristics

- 길거리 인터뷰처럼 보이는 숏폼 스타일
- 인터뷰 대상은 익명 처리된 페르소나
- 모자이크 또는 익명 비주얼 사용
- 실제 인터뷰가 아닌 데이터 기반 재연 인터뷰
- 연봉과 직무 정보를 짧고 자극적으로 전달하는 구성

## 7. Data Sources

연봉 데이터는 공개 데이터와 커리어 플랫폼 데이터를 조합해 구축한다.

### Public Data

- 고용노동부 임금정보
- 통계청 임금 데이터
- 한국고용정보원 데이터

### Career Platforms

- 잡코리아
- 사람인
- 원티드

### Corporate Data

- 상장기업 사업보고서 내 평균 급여 데이터

## 8. Data Model

PayStreet의 핵심 데이터 단위는 특정 직무/연차/지역/기업 규모에 대한 연봉 레코드다.

### Salary Record Fields

- `job_title`
- `experience_years`
- `company_size`
- `region`
- `salary_range`
- `industry`

### Example

```yaml
job_title: Backend Developer
experience_years: 4
company_size: Large
region: Pangyo
salary_range: 6500 ~ 7500
industry: IT
```

## 9. System Architecture

PayStreet는 다음 생성 파이프라인을 기반으로 동작한다.

```text
Input (job title, experience, region, company size)
    ->
Salary Data Engine
    ->
Interview Script Generator (LLM)
    ->
Voice Generator (TTS)
    ->
Video Composer
    ->
Subtitle Generator
    ->
Shorts Export
```

### Component Summary

- `Salary Data Engine`: 입력 조건에 맞는 연봉 범위와 메타데이터 조회
- `Interview Script Generator`: 연봉 데이터를 바탕으로 인터뷰형 대본 생성
- `Voice Generator`: 인터뷰어/인터뷰이 2인 대화형 음성 생성
- `Video Composer`: 템플릿 기반 인터뷰 영상 조립, 모자이크 처리, 자막 합성, 숏폼 렌더링
- `Subtitle Generator`: 핵심 문구 강조 자막 생성
- `Shorts Export`: 9:16 포맷으로 최종 영상 출력

## 10. Key Features

### 10.1 Script Generator

입력된 직무/연차/지역/연봉 범위를 바탕으로 인터뷰 스타일 대화를 생성한다.

**Input**

- 직무
- 연차
- 지역
- 기업 규모
- 연봉 범위

**Output**

- 숏폼용 인터뷰형 스크립트
- Hook, 본문, Outro 구조
- 플랫폼별 길이에 맞춘 대사 길이 조정

### 10.2 Voice Generator

인터뷰어와 인터뷰이의 음성을 생성한다.

**Requirements**

- 자연스러운 대화 톤
- 화자 간 음색 구분
- 짧고 끊기는 숏폼 리듬 반영

### 10.3 Video Composer

스크립트, 음성, 자막, 비주얼 템플릿을 결합해 숏폼 영상을 조립한다.

**Requirements**

- 템플릿 기반 인터뷰 영상 조립
- 인터뷰 대상 모자이크 및 익명 비주얼 처리
- 자막 합성
- 9:16 숏폼 렌더링
- 대량 렌더링 가능한 구조

### 10.4 Subtitle Generator

스크립트 또는 음성 결과를 기반으로 자동 자막을 생성한다.

**Requirements**

- 연봉 숫자 강조
- 직무/연차 키워드 강조
- Shorts 친화적인 고가독성 스타일

## 11. MVP Scope

### Included in MVP

- 연봉 데이터 저장 및 조회 DB
- 데이터 기반 인터뷰 스크립트 생성
- 인터뷰어/인터뷰이 음성 생성
- 템플릿 기반 영상 조립
- 최종 숏폼 영상 출력

### MVP Success Target

- 하루 20~50개의 콘텐츠 생성 가능
- 동일 주제군에 대해 반복 생성 가능
- 운영자가 최소한의 입력만으로 파이프라인 실행 가능

## 12. Content Strategy

초기에는 반응이 높은 연봉/비교형 주제에 집중한다.

### Initial Content Types

- 직무별 연봉
- 연차별 연봉
- 기업 규모별 연봉 비교
- 지역별 연봉 비교
- 직무 간 비교 콘텐츠

### Example Topics

- 4년차 백엔드 개발자 연봉
- 3년차 마케터 연봉
- 5년차 PM 연봉
- 대기업 vs 스타트업
- 서울 vs 지방
- 개발자 vs 디자이너

## 13. Content Pipeline

콘텐츠 생성 및 운영 프로세스는 다음과 같다.

```text
Topic Selection
    ->
Salary Data Retrieval
    ->
Script Generation
    ->
Voice Generation
    ->
Video Composition
    ->
Publishing
```

운영 단계에서는 주제 선정과 게시 스케줄링까지 포함하는 확장형 파이프라인으로 발전시킨다.

## 14. Success Metrics

PayStreet의 성과는 콘텐츠 품질과 생산성을 함께 측정해야 한다.

### Core Metrics

- Shorts 조회수
- 평균 시청 지속 시간
- 영상 완시율
- 채널 구독자 증가
- 콘텐츠 생산 속도
- 주제별 성과 편차

## 15. Risks and Mitigations

### 15.1 Misleading Content

AI 재연 인터뷰가 실제 인터뷰로 오해될 가능성이 있다.

**Mitigation**

- 영상 설명 및 자막에 "데이터 기반 재연 인터뷰" 명시
- 실제 인터뷰가 아니라는 점을 브랜딩 레벨에서 일관되게 노출

### 15.2 Data Accuracy

연봉 데이터의 편차, 시차, 표본 오류로 인해 정확성 이슈가 발생할 수 있다.

**Mitigation**

- 단일 수치가 아닌 범위 기반 연봉 사용
- 출처별 데이터 교차 검증
- 스크립트에 단정 표현 대신 추정형 표현 사용

## 16. Future Expansion

### Phase 2

- 직무 현실 콘텐츠 확장
- 예: 개발자 하루, PM 현실, 스타트업 vs 대기업 문화

### Phase 3

- 연봉 및 직무 정보 탐색형 데이터 플랫폼 구축

### Phase 4

- 콘텐츠 생성 SaaS 제공

## 17. Product Positioning Summary

PayStreet는 단순한 연봉 정보 서비스가 아니라, 공개 데이터를 소비성 높은 인터뷰형 숏폼 콘텐츠로 변환하는 엔진이다.

이 프로젝트의 핵심 강점은 다음과 같다.

- AI 자동화에 적합한 구조
- 반복 생산 가능한 콘텐츠 모델
- 지속 수요가 있는 커리어/연봉 주제
- 숏폼 플랫폼과 높은 포맷 적합성

초기 단계에서는 "데이터 정확성", "재연 인터뷰라는 점의 명확한 고지", "빠른 생성 파이프라인"이 제품 성공의 핵심이다.
