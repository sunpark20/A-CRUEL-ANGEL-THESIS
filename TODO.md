# A Cruel Angel's Thesis — v2 재작업 체크리스트

## 목표
UVR5 스템 분리(BS-Roformer 보컬/반주 + Demucs 4스템) 후 개별 볼륨 조절하여 믹싱.
GarageBand 프로젝트 파일이 없으므로 ffmpeg 믹싱으로 대체.

**작업 시작일:** 2026-03-18
**기존 작업 기록:** `TODO_versionA.md` 참조

---

## Phase 2: UVR5 스템 분리

### 2-A. Demucs 4스템 분리 (완료 — UVR5 GUI)

- [x] UVR5 GUI에서 **Demucs v4: htdemucs_ft** 선택 (CHOOSE PROCESS → Demucs, All Stems 모드)
- [x] 입력: `00_source/source_original.wav`
- [x] 출력 → `01_stems/lod/` (4개 스템):
  - `01_stems/lod/1_source_original_(Vocals).wav`
  - `01_stems/lod/1_source_original_(Drums).wav`
  - `01_stems/lod/1_source_original_(Bass).wav`
  - `01_stems/lod/1_source_original_(Other).wav`
- [x] 분리 결과 청취 QA

### 2-B. BS-Roformer 보컬/반주 분리 (`run_separation.sh`)

- [x] `run_separation.sh single` 실행 (BS-Roformer `model_bs_roformer_ep_317_sdr_12.9755`)
  - audio-separator 0.42.1 CLI, MPS/CoreML 가속, 26청크, 총 3시간 3분
- [x] 출력 → `01_stems/` (2개 스템, 각 69MB, 48kHz/32-bit stereo):
  - `01_stems/1_source_original_(Vocals).wav` — 48kHz/32-bit (pcm_s32le)
  - `01_stems/1_source_original_(Instrumental).wav` — 44.1kHz/16-bit (pcm_s16le)
  - ⚠️ **스펙 혼재:** BS-Roformer Vocals만 48kHz/32-bit, Instrumental은 Demucs 출력(44.1kHz/16-bit)으로 덮어씌워진 상태
  - ⚠️ `01_stems/` 루트에 Demucs 4스템(Bass, Drums, Other)도 함께 존재 (44.1kHz/16-bit)
- [x] BS-Roformer 원본 백업: `01_stems/bs/` (Vocals + Instrumental, 둘 다 48kHz/32-bit)
- [ ] 분리 결과 청취 QA — Demucs 보컬 대비 블리드 개선 확인

### 2-C. (선택) 앙상블 분리

- [ ] `bash run_separation.sh ensemble` 실행
  - BS-Roformer (`model_bs_roformer_ep_317_sdr_12.9755`) + MelBand Roformer (`model_mel_band_roformer_ep_3005_sdr_11.4360`)
  - 두 모델 각각 분리 후 결과를 가중 평균(앙상블)하여 아티팩트 감소
  - ⏱ 예상 소요: ~7-8시간 (M1 Air 기준, 모델 2개 순차 실행)
- [ ] 완료 후 후처리: 출력을 `01_stems/ensemble/`로 이동하여 정리
- [ ] 결과가 2-B보다 나은지 비교 청취

### 2-D. (선택) Apollo 음질 복원

- [ ] UVR5 GUI에서 수동 처리 (CHOOSE PROCESS → Apollo → `Universal_Model.ckpt`)
- [ ] 복원 후 다시 분리: `run_separation.sh single --input <apollo_restored.wav>`

## Phase 3: ffmpeg 믹싱

### 3-A. BS-Roformer 2스템 믹싱 (기본)

- [ ] 2스템을 ffmpeg로 합치기 (보컬 볼륨만 조절)
  - `1_source_original_(Vocals).wav` → **+5dB** (조정 가능)
  - `1_source_original_(Instrumental).wav` → **0dB** (조정 가능)
- [ ] 출력: `02_mix/mix_versionB.wav`
- [ ] 믹스 청취 QA — 보컬 볼륨 적절한지 확인

### 3-B. Demucs 4스템 믹싱 (대안)

- [x] 4스템을 ffmpeg로 합치기 (개별 볼륨 밸런스) — 2026-03-26 완료
  - `lod/1_source_original_(Vocals).wav` → **+5dB**
  - `lod/1_source_original_(Drums).wav` → **0dB**
  - `lod/1_source_original_(Bass).wav` → **0dB**
  - `lod/1_source_original_(Other).wav` → **-4dB**
- [x] 출력: `02_mix/mix_versionB_4stem.wav` (44.1kHz/32-bit, pcm_s32le, 63MB)
  - ⚠️ 44.1kHz — lod/ 소스가 44.1kHz/16-bit이므로 48kHz 미달, 마스터링 시 리샘플 필요
- [ ] 3-A vs 3-B 비교 청취 후 최종 선택

### ffmpeg 믹싱 커맨드 (참고)

```bash
# --- 3-A: BS-Roformer 2스템 ---
ffmpeg -i "01_stems/1_source_original_(Vocals).wav" \
       -i "01_stems/1_source_original_(Instrumental).wav" \
       -filter_complex "
         [0:a]volume=5dB[vocal];
         [1:a]volume=0dB[inst];
         [vocal][inst]amix=inputs=2:duration=longest:normalize=0[out]
       " \
       -map "[out]" -c:a pcm_s32le 02_mix/mix_versionB.wav

# --- 3-B: Demucs 4스템 ---
ffmpeg -i "01_stems/lod/1_source_original_(Vocals).wav" \
       -i "01_stems/lod/1_source_original_(Drums).wav" \
       -i "01_stems/lod/1_source_original_(Bass).wav" \
       -i "01_stems/lod/1_source_original_(Other).wav" \
       -filter_complex "
         [0:a]volume=5dB[vocal];
         [1:a]volume=0dB[drums];
         [2:a]volume=0dB[bass];
         [3:a]volume=-4dB[other];
         [vocal][drums][bass][other]amix=inputs=4:duration=longest:normalize=0[out]
       " \
       -map "[out]" -c:a pcm_s32le 02_mix/mix_versionB_4stem.wav
```

## Phase 4: 마스터링 + 영상 합산

- [ ] ffmpeg loudnorm 2-pass → `03_export/final_versionB.wav`
  - 목표: -14 LUFS ±1, True Peak -1 dBTP 이하
- [ ] 영상 합산 → `03_export/final_versionB.mp4`
  - `00_source/로로원본.mp4` 영상 + `final_versionB.wav` 오디오

### ffmpeg 마스터링 커맨드 (참고)

```bash
# Pass 1: 측정
ffmpeg -i 02_mix/mix_versionB.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -

# Pass 2: 적용 (측정값으로 measured_* 파라미터 채우기)
ffmpeg -i 02_mix/mix_versionB.wav \
       -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=<값>:measured_TP=<값>:measured_LRA=<값>:measured_thresh=<값>:offset=<값>:linear=true" \
       -ar 48000 -c:a pcm_s32le 03_export/final_versionB.wav

# 영상 합산
ffmpeg -i "00_source/로로원본.mp4" -i 03_export/final_versionB.wav \
       -c:v copy -c:a aac -b:a 256k -map 0:v:0 -map 1:a:0 \
       03_export/final_versionB.mp4
```

## 검증

- [ ] `ffmpeg -i 03_export/final_versionB.wav -af loudnorm=print_format=json -f null -` 로 loudness 측정
  - 통합 라우드니스: -14 LUFS ±1
  - True Peak: -1 dBTP 이하
- [ ] 원본 versionA와 A/B 비교 청취 — 보컬 볼륨 차이 확인
- [ ] 최종 mp4 재생 테스트

---

## 파일 구조

```
A-Cruel-Angels-Thesis/
├── 00_source/                          # 원본 소스 (v2에서도 공용 입력)
│   ├── 로로원본.mp4                    # 유튜브 원본 영상
│   ├── source_original.wav            # 추출 오디오 (48kHz/32-bit)
│   └── source_original.webm           # 유튜브 원본 오디오
├── 01_stems/                           # 스템 출력 (혼재 주의)
│   ├── 1_source_original_(Vocals).wav       # BS-Roformer: 보컬 (48kHz/32-bit)
│   ├── 1_source_original_(Instrumental).wav # ⚠️ Demucs 덮어쓰기 (44.1kHz/16-bit)
│   ├── 1_source_original_(Drums).wav        # Demucs: 드럼 (44.1kHz/16-bit)
│   ├── 1_source_original_(Bass).wav         # Demucs: 베이스 (44.1kHz/16-bit)
│   ├── 1_source_original_(Other).wav        # Demucs: 기타 악기 (44.1kHz/16-bit)
│   ├── bs/                                  # BS-Roformer 원본 백업
│   │   ├── 1_source_original_(Vocals).wav   # 48kHz/32-bit (pcm_s32le)
│   │   └── 1_source_original_(Instrumental).wav # 48kHz/32-bit (pcm_s32le)
│   └── lod/                                 # Demucs 4스템 결과 보존
│       ├── 1_source_original_(Vocals).wav   # 44.1kHz/16-bit
│       ├── 1_source_original_(Drums).wav    # 44.1kHz/16-bit
│       ├── 1_source_original_(Bass).wav     # 44.1kHz/16-bit
│       ├── 1_source_original_(Instrumental).wav # 44.1kHz/16-bit
│       └── 1_source_original_(Other).wav    # 44.1kHz/16-bit
├── 02_mix/                             # v2 작업 출력 경로
│   └── mix_versionB_4stem.wav        # ✅ 4스템 믹스 (44.1kHz/32-bit, 2026-03-26)
├── 03_export/                          # v2 작업 출력 경로
│   ├── final_versionB.wav            # 마스터링 완료 오디오 (재작업)
│   └── final_versionB.mp4            # 최종 영상 (재작업)
├── versionA/                           # 기존 versionA 산출물 보존
│   ├── 01_stems/
│   │   ├── vocal_raw.wav
│   │   ├── instrumental_and_noise.wav
│   │   ├── clean_mr.wav
│   │   └── crowd_noise.wav
│   ├── 02_mix/
│   │   └── mix_versionA.wav
│   └── 03_export/
│       ├── final_versionA.wav
│       └── final_versionA.mp4
├── .venv/                              # Python 가상환경 (audio-separator)
├── run_separation.sh                   # BS-Roformer 분리 자동화 스크립트
├── PRD.md
├── TRD.md
├── TODO.md                            # 이 파일 (v2)
└── TODO_versionA.md                   # 기존 작업 기록 아카이브
```

---

## 추천 모델 참조

| 모델 | 유형 | SDR | 용도 |
|---|---|---|---|
| `model_bs_roformer_ep_317_sdr_12.9755` | BS-Roformer | 12.98 | 보컬/반주 분리 (기본) |
| `model_mel_band_roformer_ep_3005_sdr_11.4360` | MelBand Roformer | 11.44 | 앙상블 보조 |
| `htdemucs_ft` | Demucs v4 | — | 4스템 분리 (vocals/drums/bass/other) |
| `Universal_Model.ckpt` | Apollo | — | 음질 복원 (저비트레이트 소스용) |
