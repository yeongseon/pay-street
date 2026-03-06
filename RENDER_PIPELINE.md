# PayStreet Render Pipeline

## 1. Overview

이 문서는 `VIDEO_TEMPLATE_SYSTEM.md`를 구현 관점으로 구체화한 렌더링 파이프라인 문서다.

---

## 2. Input Assets

- script json
- interviewer audio
- interviewee audio
- subtitle srt/json
- template yaml
- background asset
- silhouette/character asset
- branding asset

---

## 3. Render Steps

1. 작업 디렉토리 생성
2. template 로드
3. scene plan 생성
4. audio duration 계산
5. timeline 생성
6. subtitle segment 매핑
7. background/overlay/layer path 해석
8. intermediate composition 생성
9. final ffmpeg render 실행
10. mp4 export

---

## 4. Intermediate Files

- `scene_plan.json`
- `timeline.json`
- `subtitles.srt`
- `mixed_audio.wav`
- `render_manifest.json`

---

## 5. FFmpeg Responsibilities

- audio concat/mix
- subtitle burn-in
- overlay composition
- scale/pad/crop
- final H.264 export

---

## 6. Failure Handling

- missing asset -> fail fast
- invalid subtitle timing -> fallback regeneration
- ffmpeg non-zero exit -> mark render failed
- output duration outside 20~40 sec -> reject output

---

## 7. Output Contract

- `.mp4`
- H.264
- 1080x1920
- 30fps
- 20~40 sec

