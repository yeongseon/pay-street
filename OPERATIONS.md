# PayStreet Operations

## 1. Overview

PayStreet 운영은 로컬 머신 기준의 batch pipeline 운영을 전제로 한다.

---

## 2. Daily Workflow

1. topic batch 생성
2. 우선순위 topic 선택
3. pipeline 실행
4. render 결과 검수
5. 업로드 후보 선정
6. 게시

---

## 3. Operator Checklist

- salary data 최신성 확인
- topic queue 상태 확인
- 실패 job 재시도
- output 영상 샘플 검수
- 설명 문구와 disclosure 확인

---

## 4. Failure Recovery

- script 실패 -> 재생성
- audio 실패 -> provider fallback
- render 실패 -> asset/timeline 로그 확인
- topic duplication -> skip

---

## 5. Local Run Modes

- single topic run
- batch topic run
- render-only rerun
- publish-ready export

