# A Cruel Angel's Thesis — 작업 완료 보고서

## 프로젝트 요약

한로로 '잔혹한 천사의 테제' 야외 라이브 커버 영상의 오디오를 개선하여 유튜브 재업로드용 영상 제작.

**작업일:** 2026-03-16
**상태:** Version A 완료 / Version B 미진행 (보류)

---

## 최종 산출물

```
03_export/final_versionA.mp4   (274MB)
├── 영상: AV1 3840×2160 (원본 영상 그대로)
└── 오디오: AAC LC 257kbps, 48kHz, Stereo
```

---

## 원본 vs 최종 오디오 비교

| 항목 | 원본 (로로원본.mp4) | 최종 (final_versionA.mp4) |
|---|---|---|
| 코덱 | Opus | AAC LC |
| 비트레이트 | ~128 kbps | ~257 kbps |
| 통합 라우드니스 | -14.37 LUFS | -15.38 LUFS |
| True Peak | **+0.19 dBTP (클리핑)** | **-1.03 dBTP (정상)** |
| Loudness Range | 4.30 LU | 4.20 LU |

**실질적 개선점:** 원본의 True Peak 클리핑(+0.19 dBTP) 해소 → 피크에서 왜곡 없는 깨끗한 재생.

**한계:** 원본 소스가 유튜브 Opus 128kbps lossy이므로, 이미 손실된 정보의 복원은 불가. 체감 품질 차이는 미미함.

---

## 작업 파이프라인 (4단계)

### Phase 1 — 소스 준비 ✅
- YT Chita로 유튜브 원본 추출 → 48kHz/32-bit WAV 변환
- 파일: `00_source/source_original.wav` (69MB, 3분 7초)

### Phase 2 — UVR5 스템 분리 ✅
- 1차: MDX-Net Kim_Vocal_2 → `vocal_raw.wav` + `instrumental_and_noise.wav`
- 2차: VR Architecture UVR-DeNoise → `clean_mr.wav` + `crowd_noise.wav`
- QA: MR 누출 허용 수준 확인, 위상 테스트 통과

### Phase 3 — GarageBand 믹싱 ✅
- 보컬 가공: Channel EQ (HP 80Hz, High Shelf +2dB) + Compressor + Noise Gate + De-esser
- Version A (Enhanced Live): 보컬 + MR 믹싱, 피크 -3dBFS 이하 확인
- 렌더: `02_mix/mix_versionA.wav`

### Phase 4 — ffmpeg 마스터링 & 영상 합산 ✅
- ffmpeg 2-pass loudnorm → `final_versionA.wav` (-15.4 LUFS, -1.00 dBTP)
- 원본 영상 + 마스터링 오디오 합산 → `final_versionA.mp4`

---

## 파일 구조 (최종)

```
A-Cruel-Angels-Thesis/
├── 00_source/
│   ├── 로로원본.mp4                    # 유튜브 원본 영상
│   ├── source_original.wav            # 추출 오디오 (48kHz/32-bit)
│   └── source_original.webm           # 유튜브 원본 오디오
├── 01_stems/
│   ├── vocal_raw.wav                  # 1차 분리: 보컬
│   ├── instrumental_and_noise.wav     # 1차 분리: 악기+소음
│   ├── clean_mr.wav                   # 2차 분리: 악기(클린)
│   └── crowd_noise.wav               # 2차 분리: 관객 소음
├── 02_mix/
│   └── mix_versionA.wav              # GarageBand 믹스 렌더
├── 03_export/
│   ├── final_versionA.wav            # 마스터링 완료 오디오
│   └── final_versionA.mp4            # 최종 영상 (영상+오디오 합산)
├── PRD.md                             # 기획 문서
├── TRD.md                             # 기술 문서
└── TODO.md                            # 이 파일
```

---

## 미진행 / 보류

- [ ] **Version B (Studio Clean)** — 소음 완전 제거 + 리버브 추가 버전. 필요 시 진행.
- [ ] 헤드폰 + 스마트폰 스피커 청취 QA
- [ ] YouTube 업로드 후 자동 normalization 확인

---

## 세션 로그

| 시간대 | 작업 |
|--------|------|
| Phase 1 | 소스 추출, 디렉토리 구조 생성, WAV 변환 |
| Phase 2 | UVR5 2회 분리 (보컬/MR/소음), QA 통과 |
| 도구 조사 | Dolby.io (서비스 종료), Adobe Podcast (부적합) → 파이프라인 재설계 |
| Phase 3 | GarageBand 보컬 가공 + Version A 믹싱 |
| Phase 4 | ffmpeg loudnorm 마스터링 + 영상 합산 |
| 최종 검증 | 원본 vs 최종 오디오 수치 비교 — 클리핑 해소 확인, 체감 차이 미미 |
