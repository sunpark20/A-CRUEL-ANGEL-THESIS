# 오디오 리팩토링 TRD: 한로로 '잔혹한 천사의 테제' 라이브 커버

---

## 1. 시스템 및 구동 환경 (System Environment)

| 항목 | 명세 |
|------|------|
| 운영체제 | macOS (Apple Silicon M1 칩셋) |
| 권장 여유 RAM | 2GB 이상 (UVR5 AI 모델 구동 + WAV I/O) |
| 권장 여유 스토리지 | 10GB 이상 SSD (무손실 분리 파일 + 백업) |

### 핵심 소프트웨어 스택

| 역할 | 툴 | 비고 |
|------|----|------|
| 오디오 추출 | YT Chita | 유튜브 원본 고음질 추출 |
| 음원 분리 | UVR5 (arm64 네이티브 빌드) | Apple Silicon 최적화 |
| 믹싱 및 마스터링 | GarageBand | macOS 내장 DAW |

---

## 2. 디렉토리 및 파일 명명 규칙 (Directory & Naming Convention)

```
A-Cruel-Angels-Thesis/
├── 00_source/
│   └── source_original.wav          # YT Chita 추출 → 변환 원본
├── 01_stems/
│   ├── vocal_raw.wav                # Phase 2 1차 분리 보컬
│   ├── instrumental_and_noise.wav   # Phase 2 1차 분리 나머지
│   ├── clean_mr.wav                 # Phase 2 2차 분리 악기
│   └── crowd_noise.wav             # Phase 2 2차 분리 소음
├── 02_mix/
│   ├── mix_ver_a_enhanced_live.wav  # GarageBand 렌더 Ver.A
│   └── mix_ver_b_studio_clean.wav  # GarageBand 렌더 Ver.B
└── 03_export/
    ├── final_ver_a_enhanced_live.wav  # 마스터링 완료 최종본
    └── final_ver_b_studio_clean.wav   # 마스터링 완료 최종본
```

**파일 명명 규칙:**
- 소문자 + 언더스코어(`_`) 사용, 공백 금지
- 단계 번호 prefix로 작업 단계를 명확히 구분
- 버전명은 `ver_a_` / `ver_b_` prefix로 구분

---

## 3. 기술 워크플로우 및 파이프라인 (Technical Workflow & Pipeline)

### Phase 1: 원본 소스 확보 (Source Acquisition)

**도구:** YT Chita

**동작 명세:** 대상 유튜브 URL에서 비디오 압축을 거치지 않은 가장 높은 비트레이트의 오디오 스트림(주로 m4a 또는 webm/opus 포맷)을 직접 다운로드.

**포맷 변환:** 다운로드 파일 → `48kHz, 24-bit WAV` 변환 후 `00_source/source_original.wav`로 저장.

**QA 체크리스트 — Phase 1 완료 조건:**
- [ ] 파일이 `00_source/` 에 저장되었는가?
- [ ] ffprobe 또는 GarageBand에서 `48kHz / 24-bit` 확인
- [ ] 전체 재생으로 소스 무결성 확인 (잘림, 오디오 끊김 없음)
- [ ] 명확한 파열음(ㅍ, ㅌ 등) 또는 타악기 타격음을 앵커 포인트로 삼아 영상 클립과 오디오 클립의 시작점 동기화 확인

---

### Phase 2: AI 스템 분리 (Stem Separation via UVR5)

M1 맥북의 GPU 및 Neural Engine을 활용하여 로컬에서 트랙을 분리합니다.

#### 1차 분리 (보컬 / 악기+소음)

| 항목 | 값 |
|------|-----|
| Processing Method | MDX-Net |
| Model | **Kim_Vocal_2** |
| Fallback 모델 | **Kimberley_Jensen** 또는 **HTDemucs ft (vocals)** |
| GPU Conversion | 활성화 (M1 GPU 가속) |
| 입력 | `source_original.wav` |
| 출력 | `vocal_raw.wav`, `instrumental_and_noise.wav` |

> **Fallback 기준:** Kim_Vocal_2 결과물에 심각한 아티팩트(금속음, 보컬 누락)가 있을 경우 Kimberley_Jensen → HTDemucs ft 순으로 시도.

#### 2차 분리 (악기 / 소음 및 환호성)

| 항목 | 값 |
|------|-----|
| Processing Method | VR Architecture |
| Model | **UVR-DeNoise** 또는 **Crowd_HQ** |
| Fallback 모델 | **MDX23C** (다목적 노이즈 분리) |
| 입력 | `instrumental_and_noise.wav` |
| 출력 | `clean_mr.wav`, `crowd_noise.wav` |

**QA 체크리스트 — Phase 2 완료 조건:**
- [ ] `vocal_raw.wav` 재생 시 MR 누출(bleeding)이 허용 가능한 수준인가?
- [ ] `clean_mr.wav` 재생 시 관객 소음이 유의미하게 감소했는가?
- [ ] 위상 확인: GarageBand에서 `source_original.wav` + 분리 트랙 합산 시 음소거 현상 없음

---

### Phase 3: DAW 믹싱 및 렌더링 (Mixing & Rendering via GarageBand)

**프로젝트 세팅:** Sample Rate `48kHz`, Audio Resolution `24-bit`

#### 보컬 가공 체인 (vocal_raw.wav에 적용)

| 순서 | 효과 | 파라미터 | 목적 |
|------|------|----------|------|
| 1 | Channel EQ | Low-cut 80Hz, 고음역 10~12kHz +2dB 부스트 | 스마트폰 마이크 보정 |
| 2 | Compressor | Threshold -15dB, Ratio 3:1, Attack 10ms, Release 100ms | 보컬 다이나믹 안정화 |
| 3 | Noise Gate | Threshold -40dB | 무음 구간 잔여 노이즈 차단 |
| 4 | De-esser (EQ 활용) | 5~8kHz 대역 narrow Q로 -3dB 컷 | 치찰음 완화 |

#### 트랙 구성 및 파라미터

| 트랙명 | Version A (Enhanced Live) | Version B (Studio Clean) |
|--------|--------------------------|--------------------------|
| vocal_raw | Volume: 0dB (기준점), 위 보컬 가공 체인 적용 | Volume: 0dB, 위 보컬 가공 체인 적용 + Reverb: Space Designer (Studio Room 프리셋, 약하게) |
| clean_mr | Volume: -3dB ~ -5dB | Volume: -2dB ~ -4dB |
| crowd_noise | Volume: -15dB ~ -20dB (오토메이션 적용, 배경 앰비언스) | **Mute** (완전 음소거) |

**QA 체크리스트 — Phase 3 완료 조건:**
- [ ] GarageBand 내 보컬 트랙이 MR 대비 시각적으로 +3dB 이상 높게 위치
- [ ] 믹스 피크가 **-3dBFS 이하**인지 확인 (마스터링 헤드룸 확보)
- [ ] 헤드폰 + 스마트폰 스피커 양쪽에서 청취 확인
- [ ] A/B 청취 비교: 보컬 가공 체인 적용 전/후

---

## 4. YouTube 마스터링 타겟 및 최종 익스포트 명세 (Mastering Target & Export Spec)

### 마스터링 타겟 (YouTube 업로드 기준)

| 항목 | 타겟값 |
|------|--------|
| Integrated Loudness | **-14 LUFS** |
| True Peak | **-1 dBTP 이하** |
| Loudness Range (LRA) | 8 ~ 12 LU 권장 |

> 측정 도구: Youlean Loudness Meter (무료) 또는 ffmpeg `loudnorm` 필터

**GarageBand 바운스 → ffmpeg 포스트 프로세싱 워크플로우:**

1. **GarageBand 바운스 목표**: 피크 **-3 ~ -6dBFS** 로 내보내기 (loudnorm 처리를 위한 헤드룸 확보)
2. **ffmpeg loudnorm 적용** (터미널):
```bash
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=summary output.wav
```
> GarageBand 내 LUFS 정밀 제어가 제한적이므로, 바운스 후 위 명령어로 YouTube 타겟(-14 LUFS, -1 dBTP)을 정확히 맞추는 것이 더 실용적.

### 최종 익스포트 파일 명세

| 항목 | 값 |
|------|-----|
| 포맷 | WAV (최종 아카이브) + AAC 256kbps (영상 합산용) |
| Sample Rate | 48kHz |
| Bit Depth | 24-bit (WAV), 256kbps (AAC) |
| 채널 | Stereo (2ch) |
| 출력 경로 | `03_export/final_ver_a_enhanced_live.wav` / `final_ver_b_studio_clean.wav` |

**QA 체크리스트 — 최종 익스포트 완료 조건:**
- [ ] Youlean Loudness Meter에서 `-14 LUFS ±1` 범위 확인
- [ ] True Peak `-1 dBTP` 이하 확인
- [ ] 영상 합산 후 시작/끝 오디오 싱크 확인
- [ ] YouTube 업로드 후 자동 normalization 적용 여부 확인

---

## 5. 제약 사항 및 리스크 (Constraints & Risks)

| 리스크 | 내용 | 대응 |
|--------|------|------|
| 위상 캔슬레이션 | 분리 트랙 합산 시 특정 주파수 상쇄 | GarageBand에서 원본과 위상 비교; 필요 시 트랙 위상 반전 |
| 고음역대 손실 | 스마트폰 마이크 한계상 16kHz 이상 데이터 부족 가능 | GarageBand EQ에서 보컬 10kHz~12kHz 대역 +2dB 부스트로 선명도 보완 |
| UVR5 모델 실패 | Kim_Vocal_2 결과 불량 | Kimberley_Jensen → HTDemucs ft 순 Fallback |
| UVR5 메모리 오버플로우 | M1에서 MDX-Net (Kim_Vocal_2) 처리 중 RAM 부족 시 중단 | UVR5 설정에서 **Segment Size를 256으로 낮춰** 처리 |
| GarageBand 위상 반전 버튼 부재 | Logic Pro와 달리 GarageBand에는 Ø(위상 반전) 버튼이 없음 | 위상 캔슬레이션 감지 시, 트랙을 좌우로 미세 이동하여 수동 정렬로 대응 |
