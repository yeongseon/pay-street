# PayStreet Video Template System

## 1. Overview

PayStreet의 영상 시스템은 생성형 비디오 모델 중심이 아니라  
**Template-based Video Composition System** 중심으로 설계한다.

즉, PayStreet는 텍스트 프롬프트 하나로 영상을 통째로 생성하는 구조가 아니라,  
다음 요소를 조합하여 최종 숏폼 영상을 렌더링한다.

- 배경 영상 또는 배경 이미지
- 인터뷰어 레이어
- 인터뷰이 레이어
- 모자이크 또는 블러 처리
- 자막 레이어
- 강조 카드 레이어
- 오디오 트랙
- 전환 효과
- 아웃트로 카드

이 구조를 채택하는 이유는 다음과 같다.

- 비용 통제 가능
- 품질 일관성 확보
- 대량 생산 가능
- 브랜딩 일관성 유지
- 영상 포맷 반복 생산에 최적화

---

## 2. Goals

### Primary Goals

- PayStreet의 인터뷰형 숏폼 영상을 템플릿 기반으로 자동 조립 및 렌더링한다.
- 동일한 콘텐츠 포맷을 대량 생산 가능하도록 한다.
- 자막, 모자이크, 카드 UI, 배경을 일관성 있게 유지한다.
- 영상 품질과 렌더링 속도를 안정적으로 유지한다.

### Secondary Goals

- 템플릿 종류를 점진적으로 확장할 수 있도록 한다.
- 직무별, 톤별, 플랫폼별 변형이 가능하도록 한다.
- 향후 SaaS화 시 사용자 선택형 템플릿 구조로 확장 가능하도록 한다.

---

## 3. Non Goals

초기 버전에서는 다음을 목표로 하지 않는다.

- 텍스트 투 비디오 생성형 AI 모델 기반 실사 영상 생성
- 무한한 스타일 자유도를 제공하는 영상 편집기
- 사용자가 자유롭게 타임라인을 편집하는 기능
- 복잡한 모션 그래픽 시스템
- 완전한 NLE(Non-Linear Editor) 수준 편집기

---

## 4. Core Principle

PayStreet의 영상은 "생성"보다 **조립(Composition)** 이 핵심이다.

### Wrong Mental Model

- AI가 영상 전체를 만들어 준다
- 장면도 자동 생성한다
- 인물 움직임도 모두 AI 비디오 모델이 담당한다

### Correct Mental Model

- 정해진 영상 레이아웃이 있다
- 레이어 요소를 규칙에 따라 배치한다
- 음성 길이와 대본 구조에 따라 타임라인을 자동 생성한다
- 최종 영상을 렌더링한다

즉, PayStreet의 Video Template System은  
**규칙 기반 영상 조립 엔진**이다.

---

## 5. System Scope

Video Template System은 `PRD.md`와 `ARCH.md`에서 정의된 `Video Composer`의 내부 설계 문서이며, 다음 책임을 가진다.

1. 템플릿 정의
2. 장면(Scene) 구조 정의
3. 레이어 배치 규칙 정의
4. 타임라인 생성
5. 자막 동기화
6. 모자이크 처리
7. 렌더링 출력

이 시스템은 상위 파이프라인의 `Script Generator`, `Voice Generator`, `Subtitle Generator` 결과물을 입력으로 받아 최종 mp4를 조립 및 렌더링한다.

### Inputs

- `script.json`
- `audio files`
- `subtitle data` (`Subtitle Generator` output)
- `template config`
- `visual assets`
- `rendering options`

### Output

- `final_video.mp4`

---

## 6. Template System Architecture

전체 구조는 `Video Composer` 내부에서 다음과 같이 동작한다.

```text
Topic / Script
      ↓
Scene Planner
      ↓
Template Selector
      ↓
Timeline Builder
      ↓
Layer Resolver
      ↓
Subtitle Mapper
      ↓
Render Engine
      ↓
Final Shorts Video
```

각 모듈의 책임은 다음과 같다.

### Scene Planner

스크립트를 분석하여 장면 단위로 나눈다.

### Template Selector

주제, 톤, 길이에 맞는 템플릿을 선택한다.

### Timeline Builder

장면별 지속 시간과 전환 타이밍을 계산한다.

### Layer Resolver

각 장면에 필요한 비주얼 레이어를 결정한다.

### Subtitle Mapper

`Subtitle Generator`가 생성한 자막 세그먼트를 장면 타임라인에 매핑하고 시작/종료 타이밍을 맞춘다.

### Render Engine

레이어와 타임라인을 기준으로 최종 비디오를 조립하고 렌더링한다.

---

## 7. Template Model

각 영상은 하나의 템플릿을 기반으로 조립된다.

### Template Definition

템플릿은 다음 속성을 가진다.

- `template_id`
- `template_name`
- `template_type`
- `supported_duration_range`
- `scene_layouts`
- `subtitle_style`
- `overlay_style`
- `mosaic_policy`
- `transition_style`
- `branding_assets`

### Example

```json
{
  "template_id": "street_interview_v1",
  "template_name": "Street Interview Basic",
  "template_type": "interview",
  "supported_duration_range": [20, 40],
  "subtitle_style": "bold_bottom_caption",
  "overlay_style": "salary_card_v1",
  "mosaic_policy": "interviewee_face_blur",
  "transition_style": "hard_cut",
  "branding_assets": ["logo_white.png"]
}
```

---

## 8. Scene Model

PayStreet 영상은 Scene 단위로 구성한다.

### Standard Scene Types

- Intro Scene
- Question Scene
- Answer Scene
- Highlight Scene
- Outro Scene

### Example Flow

```text
Intro
→ Q1
→ A1
→ Q2
→ A2
→ Highlight Card
→ Outro
```

### Scene Definition

각 Scene은 다음 정보를 가진다.

- `scene_id`
- `scene_type`
- `duration`
- `audio_segment`
- `subtitle_segment`
- `background_asset`
- `character_layout`
- `overlay_elements`
- `mosaic_target`
- `transition_in`
- `transition_out`

---

## 9. Layer Model

각 Scene은 여러 레이어를 가진다.

### Layer Types

- Background Layer
- Character Layer
- Mosaic Layer
- Subtitle Layer
- Overlay Card Layer
- Logo Layer
- Audio Layer
- Effect Layer

### Rendering Order

아래 순서로 렌더링한다.

```text
Background
→ Character
→ Mosaic
→ Overlay Card
→ Subtitle
→ Branding / Logo
→ Effects
```

이 순서를 고정함으로써 시각적 일관성을 유지한다.

---

## 10. Template Types

초기 설계 기준으로는 3개의 템플릿을 정의하며, MVP 구현은 이 중 1개만 우선 지원한다.

### 10.1 Street Interview Basic

가장 기본 템플릿

특징

- 길거리 인터뷰 느낌
- 인터뷰어/인터뷰이 2인 구조
- 인터뷰이 얼굴 모자이크
- 하단 자막
- 숫자 강조 카드

사용 목적

- 연봉 얼마예요
- 직무 인터뷰
- 지역/직군별 비교

### 10.2 Anonymous Salary Talk

익명 토크형 템플릿

특징

- 인터뷰이 실루엣 강조
- 블러 배경
- 익명성 강조
- 더 차분한 톤

사용 목적

- 민감한 연봉 주제
- 현실 토크
- 워라밸, 스트레스 등

### 10.3 Salary Facts Card Mix

인터뷰 + 카드형 정보 요약

특징

- 중간에 데이터 카드 삽입
- 숫자/범위 강조
- 비교 콘텐츠에 적합

사용 목적

- 대기업 vs 스타트업
- 지역별 차이
- 직무별 비교

---

## 11. Visual Asset Strategy

영상의 비주얼 요소는 정적 또는 반정적 에셋으로 관리한다.

### Asset Categories

- `background_videos/`
- `background_images/`
- `interviewer_assets/`
- `interviewee_assets/`
- `silhouettes/`
- `overlay_cards/`
- `logos/`
- `transitions/`
- `icons/`

### Asset Rules

- 모든 에셋은 9:16 기준으로 설계한다.
- 템플릿마다 허용된 에셋 세트를 정의한다.
- 배경은 과도하게 복잡하지 않아야 한다.
- 인물 자산은 브랜딩과 일관된 스타일을 유지한다.
- 인터뷰이는 익명성 연출을 위해 얼굴 노출을 피하거나 블러 처리한다.

---

## 12. Mosaic Policy

PayStreet의 핵심 연출 중 하나는 인터뷰이 익명성이다.

### Supported Mosaic Policies

- `face_blur`
- `face_pixelate`
- `upper_body_blur`
- `silhouette_only`

### Default Policy

초기 버전 기본값은 다음과 같다.

- `interviewee`: `silhouette_only` 또는 `face_pixelate`
- `interviewer`: `no blur`

### Policy Selection Rule

- 신뢰감 강조 -> `face_pixelate`
- 익명성 강조 -> `silhouette_only`
- 민감한 주제 -> `upper_body_blur`

### Note

초기 MVP에서는 얼굴 추적 기반 동적 모자이크보다  
사전 정의된 위치 기반 마스킹 또는 실루엣 자산 사용을 우선 적용한다.

이유

- 구현 난이도 감소
- 렌더링 속도 향상
- 일관성 확보

---

## 13. Subtitle System

자막은 PayStreet 영상에서 매우 중요한 정보 전달 수단이다.

### Subtitle Requirements

- 모바일 화면에서 읽기 쉬워야 한다.
- 연봉 숫자와 직무명을 강조해야 한다.
- 대사 길이에 맞춰 자연스럽게 분절해야 한다.
- 자막이 화면을 과도하게 가리지 않아야 한다.

### Subtitle Styles

#### Style A: Bottom Bold Caption

- 하단 배치
- 굵은 폰트
- 핵심 단어 강조

#### Style B: Split Highlight Caption

- 주요 키워드 분리 강조
- 숫자, 직무, 지역만 별도 카드 처리

### Highlight Targets

다음을 자동 강조 대상으로 정의한다.

- `salary`
- `job_title`
- `years_of_experience`
- `region`
- `company_type`

---

## 14. Timeline Generation

타임라인은 음성 길이와 장면 규칙을 기반으로 자동 생성하며, 이는 `ARCH.md`의 `Video Composer` 내부 책임에 해당한다.

### Inputs

- interviewer audio duration
- interviewee audio duration
- scene order
- subtitle segments
- intro/outro padding

### Rules

- Intro: 1.5 ~ 2.5 sec
- Question Scene: audio duration + 0.3 sec
- Answer Scene: audio duration + 0.5 sec
- Highlight Scene: 1.5 ~ 3 sec
- Outro: 1.5 ~ 2.5 sec

### Example

```text
Intro: 2.0 sec
Q1: 2.3 sec
A1: 3.8 sec
Q2: 2.1 sec
A2: 4.2 sec
Highlight: 2.0 sec
Outro: 2.0 sec
```

---

## 15. Render Engine

렌더링 엔진은 최종 영상을 조립하고 출력하는 책임을 가진다.

### Responsibilities

- scene 합성
- layer 순서 보장
- subtitle 삽입
- mosaic 적용
- 오디오 믹싱
- mp4 출력

### Recommended Tools

- FFmpeg
- OpenCV
- Python orchestration layer

### Output Requirements

```text
format: mp4
codec: H.264
resolution: 1080x1920
aspect_ratio: 9:16
fps: 30
target_duration: 20 ~ 40 sec
```

---

## 16. Template Config Structure

템플릿은 코드 하드코딩보다 설정 파일 기반으로 관리한다.

### Example

```yaml
template_id: street_interview_v1
type: interview
resolution: 1080x1920
fps: 30

subtitle:
  style: bottom_bold_caption
  position: bottom
  highlight_salary: true
  highlight_job_title: true

mosaic:
  policy: silhouette_only

branding:
  logo: assets/logos/paystreet_white.png
  watermark_enabled: true

scenes:
  - type: intro
    layout: intro_title_layout
  - type: question
    layout: split_interview_layout
  - type: answer
    layout: split_interview_layout
  - type: highlight
    layout: salary_card_layout
  - type: outro
    layout: outro_cta_layout
```

---

## 17. Template Selection Strategy

템플릿 선택은 규칙 기반으로 시작하며, 이는 상위 파이프라인에서 전달된 콘텐츠 메타데이터를 사용한다.

### Selection Inputs

- `content_type`
- `tone`
- `topic_category`
- `duration_estimate`
- `platform`

### Example Rules

- 연봉 인터뷰 -> `street_interview_v1`
- 민감한 현실 토크 -> `anonymous_salary_talk_v1`
- 비교형 주제 -> `salary_facts_mix_v1`

향후에는 A/B 테스트 결과를 기반으로 템플릿 성능 최적화 가능하다.

---

## 18. Branding System

Video Template System은 PayStreet 브랜드 일관성을 유지해야 한다.

### Branding Elements

- 로고
- 인트로 타이틀 스타일
- 아웃트로 CTA
- 자막 스타일
- 색상 팔레트
- 숫자 강조 카드 스타일

### Branding Rules

- 모든 영상에 PayStreet 로고를 포함한다.
- 연봉 숫자 강조 UI는 동일 스타일을 유지한다.
- 템플릿마다 세부 차이는 허용하되 브랜드 아이덴티티는 유지한다.

---

## 19. File / Directory Structure

```text
paystreet/
  assets/
    backgrounds/
    characters/
    silhouettes/
    overlays/
    logos/
    icons/

  templates/
    street_interview_v1.yaml
    anonymous_salary_talk_v1.yaml
    salary_facts_mix_v1.yaml

  app/
    video/
      scene_planner.py
      template_selector.py
      timeline_builder.py
      layer_resolver.py
      subtitle_mapper.py
      render_engine.py

    models/
      template.py
      scene.py
      layer.py
      render_job.py
```

---

## 20. MVP Scope

MVP에서는 다음만 지원한다.

- 템플릿 1개: `street_interview_v1`
- 장면 타입 4개: `intro`, `question`, `answer`, `outro`
- 인터뷰어 1종
- 인터뷰이 실루엣 3종
- 자막 스타일 1종
- 연봉 강조 카드 1종
- 20~40초 영상 출력

### MVP Out of Scope

- 자유 편집
- 다중 카메라 연출
- 동적 얼굴 추적 모자이크
- 사용자 맞춤 템플릿 편집기
- 생성형 비디오 모델 통합

---

## 21. Risks

### Risk 1. Too Generic Visuals

모든 영상이 비슷해 보여 시청자가 질릴 수 있다.

대응

- 배경, 실루엣, 카드 스타일 변형 지원
- 템플릿 2~3종 확장

### Risk 2. Rendering Cost

영상 렌더링 속도가 느릴 수 있다.

대응

- 템플릿 단순화
- 정적 자산 재사용
- 병렬 렌더링 구조 도입

### Risk 3. Low Realism

실제 인터뷰처럼 보이지 않을 수 있다.

대응

- 오디오 톤 개선
- 현장감 있는 배경 선택
- 자막, 컷 편집 고도화

---

## 22. Future Evolution

### Phase 2

- 템플릿 3종 확장
- 비교형 카드 장면 추가
- 플랫폼별 변형 템플릿 지원

### Phase 3

- A/B 테스트 기반 템플릿 성능 최적화
- 자동 템플릿 추천 시스템

### Phase 4

- 사용자 선택형 템플릿 SaaS
- 브랜딩 커스터마이징
- 멀티채널 운영용 배치 생성

---

## 23. Conclusion

PayStreet의 핵심은 AI로 영상을 통째로 만드는 것이 아니라  
반복 가능한 인터뷰형 숏폼 영상을 안정적으로 조립하는 Template System이다.

이 시스템은 다음을 동시에 만족해야 한다.

- 비용 효율성
- 대량 생산성
- 브랜딩 일관성
- 정보 전달력
- 현실감 있는 연출

따라서 Video Template System은 `ARCH.md`의 `Video Composer`를 구체화한 렌더링 계층이자  
콘텐츠 품질을 결정하는 핵심 엔진이다.
