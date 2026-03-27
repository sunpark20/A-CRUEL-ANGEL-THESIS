# 잔혹한 천사의 테제 — 오디오 리마스터링 작업 과정

**최종 결과물:** `03_export/final_versionB_v1.3_hardsub.mp4` (자막 포함 업로드본)
**소스:** 유튜브 야외 라이브 폰 녹화 (Opus 128kbps lossy)

---

## 용어 설명

| 용어 | 설명 |
|------|------|
| **LUFS** | 통합 라우드니스 단위. 숫자가 클수록(0에 가까울수록) 크게 들림. YouTube 기준은 **-14 LUFS**. -14보다 크면 YouTube가 자동으로 낮춤. -14 이하면 그대로 둠. |
| **LRA** | 다이나믹 레인지. 소리의 강약 폭. 낮을수록 더 압축된(꽉 찬) 소리. 클래식 8~12, 일반 팝 5~8, **K-pop/상업 음악 3~5**. |
| **dBTP** | True Peak. 실제 파형의 최고점. **-1 dBTP 이하**로 유지해야 클리핑(소리 찢어짐) 없음. |
| **Compressor** | 큰 소리는 줄이고 작은 소리는 살려서 전체 볼륨을 균일하게 만드는 도구. LRA를 낮춰 더 꽉 찬 소리를 만듦. |
| **Limiter** | 설정한 레벨을 절대 넘지 못하게 막는 하드 천장. 클리핑 방지. |
| **Loudnorm** | ffmpeg의 라우드니스 정규화 필터. LUFS/dBTP 목표값에 맞게 전체 레벨 조정. **2-pass** 방식 사용 (1차 측정 → 2차 적용). |
| **AI 스템 분리** | AI 모델로 혼합 오디오에서 보컬/반주를 각각 분리. 분리된 개별 파일을 **스템(stem)** 이라 부름. |
| **앙상블** | 여러 AI 모델의 분리 결과를 합산해 더 나은 결과를 얻는 방법. |

---

## 전체 파이프라인

```
00_source/source_original.wav
        │
        ▼
[ Phase 1: AI 스템 분리 ]
  run_separation.sh ensemble
  → 01_stems/ensemble/ (Vocals + Instrumental)
        │
        ▼
[ Phase 2: ffmpeg 믹싱 ]
  Vocal +6dB / Inst -1dB
  → 02_mix/mix_versionB_v1.3.wav
        │
        ▼
[ Phase 3: 마스터링 ]
  Compressor → Limiter → Loudnorm (-14 LUFS)
  → 03_export/final_versionB_v1.3_lra3.6.wav
        │
        ▼
[ Phase 4: 영상 합산 ]
  00_source/로로원본.mp4 + final_versionB_v1.3_lra3.6.wav
  → 03_export/final_versionB_v1.3_lra3.6.mp4
        │
        ▼
[ Phase 5: 자막 하드서브 ]
  04_caption/subtitle_final.ass → 이미지 오버레이
  → 03_export/final_versionB_v1.3_hardsub.mp4  ✅ 최종 업로드본
```

---

## Phase 1: AI 스템 분리

**사용 모델:** BS-RoFormer (SDR 12.98) + MelBand RoFormer (SDR 11.44) 앙상블
**알고리즘:** `uvr_max_spec` (주파수별 최댓값 선택, 보컬 선명도 우수)

```bash
cd /Users/sunguk/0.code/A-Cruel-Angels-Thesis
bash run_separation.sh ensemble --output 01_stems/ensemble
```

**출력:**
- `01_stems/ensemble/1_source_original_(Vocals).wav` — 보컬 스템
- `01_stems/ensemble/1_source_original_(Instrumental).wav` — 반주 스템
- 포맷: 48kHz / 32-bit WAV

> ⏱ M5 Pro 기준 약 4분 소요

---

## Phase 2: ffmpeg 믹싱

보컬/반주 볼륨 비율 조정 후 합산.

**최종 채택값:** Vocal **+6dB** / Inst **-1dB** (상대 차이 7dB)

```bash
ffmpeg -i "01_stems/ensemble/1_source_original_(Vocals).wav" \
       -i "01_stems/ensemble/1_source_original_(Instrumental).wav" \
       -filter_complex "
         [0:a]volume=6dB[vocal];
         [1:a]volume=-1dB[inst];
         [vocal][inst]amix=inputs=2:duration=longest:normalize=0[out]
       " \
       -map "[out]" -c:a pcm_s32le 02_mix/mix_versionB_v1.3.wav -y
```

> `normalize=0` 필수 — amix 자동 정규화 비활성화

---

## Phase 3: 마스터링 (2-pass Loudnorm)

컴프레서 → 리미터 → Loudnorm 순서로 적용.

### Pass 1: 측정

```bash
ffmpeg -i 02_mix/mix_versionB_v1.3.wav \
  -af "acompressor=threshold=-18dB:ratio=4:attack=5:release=100:makeup=2dB,
       alimiter=level_in=1:level_out=0.891:limit=0.891:attack=5:release=50:asc=true,
       loudnorm=I=-14:TP=-1:LRA=8:print_format=json" \
  -f null - 2>&1 | grep -A 12 "{"
```

측정값 예시 (매번 다를 수 있음):
```
input_i: -15.94  input_tp: -5.13  input_lra: 3.60  input_thresh: -26.00  target_offset: 0.57
```

### Pass 2: 적용

```bash
ffmpeg -i 02_mix/mix_versionB_v1.3.wav \
  -af "acompressor=threshold=-18dB:ratio=4:attack=5:release=100:makeup=2dB,
       alimiter=level_in=1:level_out=0.891:limit=0.891:attack=5:release=50:asc=true,
       loudnorm=I=-14:TP=-1:LRA=8:measured_I=<Pass1값>:measured_TP=<Pass1값>:measured_LRA=<Pass1값>:measured_thresh=<Pass1값>:offset=<Pass1값>:linear=true" \
  -ar 48000 -c:a pcm_s32le 03_export/final_versionB_v1.3_lra3.6.wav -y
```

**결과:** -14.00 LUFS / -1.26 dBTP / LRA 3.6 ✅

---

## Phase 4: 영상 합산

```bash
ffmpeg -i "00_source/로로원본.mp4" \
       -i 03_export/final_versionB_v1.3_lra3.6.wav \
       -c:v copy -c:a aac -b:a 256k \
       -map 0:v:0 -map 1:a:0 \
       03_export/final_versionB_v1.3_lra3.6.mp4 -y
```

---

## Phase 5: 자막 하드서브

입력: `03_export/final_versionB_v1.3_lra3.6.mp4`
스크립트: `04_caption/sync_lyrics.py`, `04_caption/gen_subtitle.py`
자막: `04_caption/subtitle_final.ass` (Hiragino Kaku Gothic ProN, 일본어 38pt + 한국어 52pt)

```bash
# 자막 이미지 오버레이 방식 하드서브 (ffmpeg minimal 빌드 환경)
ffmpeg -i 03_export/final_versionB_v1.3_lra3.6.mp4 \
       -i 04_caption/p.png \
       -filter_complex "overlay=0:0" \
       -c:v libx264 -crf 18 -c:a copy \
       03_export/final_versionB_v1.3_hardsub.mp4 -y
```

> ⚠️ 현재 시스템의 ffmpeg는 minimal 빌드로 `ass`/`subtitles` 필터 미지원.
> `p.png`는 Python 렌더링 엔진으로 생성한 자막 오버레이 이미지(3840×2160).
> ffmpeg full 빌드(`brew install ffmpeg`) 설치 시 `subtitles` 필터로 직접 하드서브 가능.

**결과:** `03_export/final_versionB_v1.3_hardsub.mp4` (3840×2160 4K) ✅

---

## 최종 파일 구조

```
A-Cruel-Angels-Thesis/
├── 00_source/
│   ├── source_original.wav       # 원본 소스 (48kHz/32-bit)
│   ├── source_original.webm      # 유튜브 원본 오디오
│   └── 로로원본.mp4              # 원본 영상
├── 01_stems/
│   ├── ensemble/                 # ✅ 최종 사용 스템
│   │   ├── 1_source_original_(Vocals).wav
│   │   └── 1_source_original_(Instrumental).wav
│   ├── bs/                       # BS-RoFormer 단일 모델 백업
│   └── lod/                      # Demucs 4스템 백업
├── 02_mix/
│   └── mix_versionB_v1.3.wav    # ✅ 최종 믹스 (Vocal +6 / Inst -1)
├── 03_export/
│   ├── final_versionB_v1.3_lra3.6.mp4  # 마스터링 완료본 (자막 없음)
│   └── final_versionB_v1.3_hardsub.mp4 # ✅ 최종 업로드본 (4K + 자막)
├── 04_caption/
│   ├── sync_lyrics.py            # SRT 한국어 치환 스크립트
│   ├── gen_subtitle.py           # 2줄 ASS 자막 생성 스크립트
│   ├── subtitle_final.ass        # 최종 자막 파일
│   ├── p.png                     # 자막 오버레이 이미지
│   ├── small_out/                # 보조 SRT/가사
│   └── NOTES.md                  # 자막 작업 상세 노트
└── run_separation.sh             # 스템 분리 스크립트
```

---

## 컴프레서 설정 참고

| 파라미터 | 값 | 의미 |
|---------|-----|------|
| threshold | -18dB | 이 레벨 이상이면 압축 시작 |
| ratio | 4:1 | 넘친 소리를 1/4로 줄임 |
| attack | 5ms | 압축 시작 반응 속도 |
| release | 100ms | 압축 해제 속도 |
| makeup | +2dB | 압축 후 전체 게인 보상 |

## LUFS vs LRA 관계

- **LUFS만 높이면** → YouTube가 낮춰버림 (효과 없음)
- **LRA를 낮추면** → YouTube에서도 더 꽉 찬 소리 유지
- **최적 전략:** LUFS -14 고정 + LRA 3~5로 압축 = 유튜브 최강 볼륨
