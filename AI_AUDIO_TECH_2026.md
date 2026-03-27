# 최신 AI 오디오 기술 정보 (2026-03 기준)

검색 소스: Reddit (r/AudioProduction, r/VocalIsolation, r/IsolatedVocals), Gearspace, AudioSEX, VI-Control, GitHub Discussions, MVSEP

---

## 음원 분리 모델 티어

| 티어 | 모델 | SDR | 용도 |
|------|------|-----|------|
| Tier 1 (SOTA) | BS-RoFormer (`ep_317_sdr_12.9755`) | 12.98 | 보컬/반주 분리 (본 프로젝트 기본 모델) |
| Tier 1 | MelBand RoFormer (`ep_3005_sdr_11.4360`) | 11.44 | 앙상블 보조, 보컬/드럼/기타 분리에서 BS-RoFormer 능가 사례 |
| Tier 1 | BS-RoFormer SW | — | 6스템 분리 (vocals/drums/bass/guitar/piano/other) |
| Tier 2 | SCNet XL (IHF) | 9.0 | 앙상블 보조, HTDemucs 대비 48% CPU 시간 |
| Tier 2 | Demucs v4 (htdemucs_ft) | — | 4스템 분리, 드럼/베이스 리얼리즘 최고 |
| 복원 | Apollo Universal_Model | — | 저비트레이트(128kbps) 소스 음질 복원 |

## 최고 품질 앙상블 조합 (MVSEP 기준)

- **보컬/반주:** BS-RoFormer + MelBand RoFormer + SCNet XL IHF
- **본 프로젝트:** BS-RoFormer + MelBand RoFormer 앙상블 (`run_separation.sh ensemble`)

## 라이브/폰 녹음 전처리 권장 순서

1. **디노이즈 (선택):** Resemble Enhance (오픈소스, 15-25dB 노이즈 감소) 또는 DeepFilterNet
2. **음원 분리:** BS-RoFormer (UVR5 aggression 15-20으로 설정)
3. **스템별 후처리:** 분리된 개별 스템에 라이트 노이즈 리덕션 적용
4. **믹싱:** 개별 볼륨 조절 후 합산
5. **마스터링:** loudnorm 2-pass

## 새로운 패러다임: 언어 쿼리 분리

- **AudioSep:** 자연어로 원하는 소스 지정 (예: "female backing vocalist") → 해당 소리만 추출
- 기존 모델이 처리 못하는 세밀한 분리에 유용

## 검색 대상 커뮤니티

다음 세션에서 최신 정보 갱신 시 아래를 검색할 것:
- Reddit: r/AudioProduction, r/WeAreTheMusicMakers, r/VocalIsolation, r/IsolatedVocals
- 전문가 포럼: Gearspace, AudioSEX, VI-Control
- GitHub: UVR5, audio-separator, ZFTurbo/Music-Source-Separation-Training
- 서비스: MVSEP (mvsep.com) 알고리즘 페이지
