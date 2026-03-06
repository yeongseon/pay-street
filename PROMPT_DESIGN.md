# PayStreet Prompt Design

## 1. Goal

Script Generator는 데이터 기반 인터뷰 대본을 일관된 형식으로 생성해야 한다.

핵심 조건

- 실제 인터뷰처럼 보이되 실제 인터뷰라고 주장하지 않음
- 연봉은 범위 기반으로 표현
- 과장하거나 단정하지 않음
- 20~40초 숏폼 길이에 맞는 대사량 유지

---

## 2. Output Format

기본 출력 형식

```json
{
  "hook": "4년차 백엔드 개발자 연봉 얼마예요?",
  "dialogue": [
    {"speaker": "interviewer", "line": "무슨 일 하세요?"},
    {"speaker": "interviewee", "line": "판교에서 백엔드 개발자로 일하고 있습니다."},
    {"speaker": "interviewer", "line": "몇 년 차세요?"},
    {"speaker": "interviewee", "line": "4년차입니다."},
    {"speaker": "interviewer", "line": "연봉은 어느 정도 되세요?"},
    {"speaker": "interviewee", "line": "세전 기준 약 6천5백에서 7천5백 정도입니다."}
  ],
  "outro": "여러분 연봉은 어떤가요?"
}
```

---

## 3. Prompt Rules

- 입력 데이터 밖의 사실을 추가하지 않는다.
- `salary_range`는 범위 표현으로 유지한다.
- 화자는 `interviewer`, `interviewee` 2명만 사용한다.
- 대사는 짧고 구어체로 작성한다.
- 숫자는 모바일 자막에서 읽기 쉽게 단순화한다.
- 지역, 직무, 연차는 가능한 한 초반에 드러낸다.

---

## 4. Forbidden Patterns

- 실제 인터뷰를 했다고 암시하는 표현
- 근거 없는 기업명 언급
- 확정적 수치 단정
- 과도한 자극 문구
- 혐오/차별적 표현

예

- `실제로 인터뷰해보니`
- `무조건 이 연봉입니다`
- `다른 직무보다 훨씬 별로예요`

---

## 5. Tone Presets

### `neutral`

- 정보 전달 중심
- 과장 최소화

### `shorts_hook`

- 첫 문장 훅 강화
- 본문은 여전히 데이터 기반 유지

### `career_reality`

- 직무 현실 강조
- 감정 표현은 절제

---

## 6. Prompt Template

```text
You are generating a simulated interview script based only on structured salary data.
This is not a real interview.

Use the following data:
- job_title: {job_title}
- experience_years: {experience_years}
- region: {region}
- company_size: {company_size}
- salary_range: {salary_range}
- tone: {tone}

Requirements:
- Return only valid JSON
- Keep it under 40 seconds when spoken
- Use interviewer/interviewee format
- Do not invent facts beyond the given data
- Express salary as a range, not a single exact value
```

