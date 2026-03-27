# 04_caption — 자막 하드서브 작업 노트

**목적:** 마스터링된 영상(`03_export/final_versionB_v1.3_lra3.6.mp4`)에 일본어/한국어 병기 자막을 하드서브(Hardsub)하여 최종 업로드본 생성.

**최종 결과물:** `03_export/final_versionB_v1.3_hardsub.mp4` (3840×2160, 4K)

---

## 파일 구성

| 파일 | 설명 |
|------|------|
| `sync_lyrics.py` | Whisper 생성 일본어 SRT → 한국어 치환 (퍼지 매칭) |
| `gen_subtitle.py` | 2줄 자막 ASS 생성 (일본어 38pt + 한국어 52pt) |
| `subtitle_final.ass` | 최종 사용 자막 파일 |
| `*.ko_cleaned.ass/srt` | 정제된 자막 (BOM 제거, 순수 UTF-8) |
| `*.ko.srt` | 한국어 SRT 원본 |
| `p.png` | 자막 오버레이 이미지 (6.5 MB, 3840×2160) |
| `small_out/` | 보조 SRT 및 가사 파일 |

---

## 주요 명령어

```bash
# 1. 일본어 SRT → 한국어 SRT 치환
python3 04_caption/sync_lyrics.py <input.srt> [output.srt]

# 2. 2줄 자막 ASS 생성 (ko_cleaned.ass → subtitle_final.ass)
python3 04_caption/gen_subtitle.py

# 3. 자막 이미지 오버레이 방식 하드서브
ffmpeg -i 03_export/final_versionB_v1.3_lra3.6.mp4 \
       -i 04_caption/p.png \
       -filter_complex "overlay=0:0" \
       -c:v libx264 -crf 18 -c:a copy \
       03_export/final_versionB_v1.3_hardsub.mp4 -y
```

---

## 파이프라인

```
Whisper SRT (일본어)
    │
    ▼ sync_lyrics.py (퍼지 매칭, LYRICS_MAP 37쌍)
*.ko.srt (한국어)
    │
    ▼ 정제 (BOM 제거, UTF-8 정규화)
*.ko_cleaned.srt
    │
    ▼ ASS 변환 + 폰트 지정 (Hiragino Kaku Gothic ProN)
*.ko_cleaned.ass
    │
    ▼ gen_subtitle.py (일본어+한국어 2줄, 크기 차등)
subtitle_final.ass
    │
    ▼ 커스텀 Python 렌더링 엔진 (타임코드 → 투명 PNG)
p.png (자막 오버레이 이미지)
    │
    ▼ ffmpeg overlay
03_export/final_versionB_v1.3_hardsub.mp4 ✅
```

---

## 알려진 제약 및 해결책

**문제 1 — 일본어 한자('残' 등) 깨짐**
- 원인: SRT UTF-8 BOM 혼선 + Arial 계열 폰트 미지원
- 해결: BOM 제거 후 순수 UTF-8 처리 + **Hiragino Kaku Gothic ProN** 폰트 강제 지정

**문제 2 — ffmpeg minimal 빌드 (`ass`/`subtitles` 필터 미지원)**
- 원인: 현재 설치된 ffmpeg가 최소 빌드
- 해결: 커스텀 Python 렌더링으로 자막을 투명 PNG 이미지로 변환 후 `overlay` 필터 사용
- 향후: `brew install ffmpeg` (full 빌드) 시 `subtitles` 필터로 직접 하드서브 가능

---

## ASS 자막 설정 (subtitle_final.ass)

- PlayRes: 3840×2160 (4K)
- 폰트: Hiragino Kaku Gothic ProN
- 일본어: 38pt (인라인 크기 오버라이드)
- 한국어: 52pt (인라인 크기 오버라이드)
- Outline: 2.5 / Shadow: 1
