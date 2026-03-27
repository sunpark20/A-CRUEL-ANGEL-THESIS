# CLAUDE.md — A Cruel Angel's Thesis 오디오 리팩토링

## 프로젝트 개요

한로로 '잔혹한 천사의 테제' 야외 라이브 커버 오디오 개선 → 유튜브 재업로드.

- **Version A (Enhanced Live):** 완료 (2026-03-16)
- **Version B (Studio Clean):** v2 재작업 중 (2026-03-18~)

## 참조 문서

| 문서 | 내용 |
|------|------|
| [`PRD.md`](PRD.md) | 기획 — 목표, 성공 기준, 2버전 명세 |
| [`TRD.md`](TRD.md) | 기술 — 디렉토리 구조, 모델 설정, 보컬 가공 체인, 마스터링 명세 |
| [`TODO.md`](TODO.md) | v2 작업 체크리스트 (현재 진행) |
| [`TODO_versionA.md`](TODO_versionA.md) | v1 완료 보고서 |
| [`AI_AUDIO_TECH_2026.md`](AI_AUDIO_TECH_2026.md) | 최신 AI 오디오 기술 정보 (2026-03 기준, 모델 티어, 앙상블, 전처리 순서) |

## 작업 규칙

1. **최신 기술 확인:** 작업 전 [`AI_AUDIO_TECH_2026.md`](AI_AUDIO_TECH_2026.md) 참조. 필요 시 전문가 커뮤니티 재검색하여 갱신.
2. **품질 기준:** -14 LUFS, -1 dBTP, 보컬 MR 대비 +3dB 이상, AI 아티팩트 없음
3. **파일 규칙:** 48kHz/24-bit WAV, 소문자+언더스코어, 단계 prefix (`00_`~`03_`)
4. **소스 제약:** 원본 Opus 128kbps lossy — 손실 정보 복원 불가 인지
5. **ffmpeg:** `amix`는 `normalize=0`, 마스터링은 2-pass loudnorm (`linear=true`), 중간물 `pcm_s32le`
