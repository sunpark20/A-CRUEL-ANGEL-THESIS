# CLAUDE.md — A Cruel Angel's Thesis 오디오+영상 제작

## 프로젝트 개요

한로로 '잔혹한 천사의 테제' 야외 라이브 커버 오디오 개선 + 자막 하드서브 → 유튜브 재업로드.

- **Version A (Enhanced Live):** 완료 (2026-03-16)
- **Version B (Studio Clean):** 오디오 완료, 자막 하드서브 완료 (2026-03-27)

## 참조 문서

| 문서 | 내용 |
|------|------|
| [`PROCESS.md`](PROCESS.md) | 전체 파이프라인 (Phase 1~5) 기술 상세 |
| [`04_caption/NOTES.md`](04_caption/NOTES.md) | 자막 하드서브 작업 노트 (스크립트, 제약, ASS 설정) |

## 작업 규칙

1. **품질 기준:** -14 LUFS, -1 dBTP, 보컬 MR 대비 +3dB 이상, AI 아티팩트 없음
2. **파일 규칙:** 48kHz/24-bit WAV, 소문자+언더스코어, 단계 prefix (`00_`~`04_`)
3. **소스 제약:** 원본 Opus 128kbps lossy — 손실 정보 복원 불가 인지
4. **ffmpeg:** `amix`는 `normalize=0`, 마스터링은 2-pass loudnorm (`linear=true`), 중간물 `pcm_s32le`
5. **자막:** 폰트는 Hiragino Kaku Gothic ProN 강제 지정, SRT는 BOM 제거 후 순수 UTF-8
