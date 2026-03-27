#!/usr/bin/env bash
# =============================================================================
# UVR5 음원 분리 워크플로우 자동화
# BS-Roformer + MelBand Roformer 앙상블 via audio-separator CLI
# Apple Silicon MPS/CoreML 가속 자동 사용
# =============================================================================
set -euo pipefail

# --- 경로 설정 ---
PROJECT_DIR="/Users/sunguk/0.code/A-Cruel-Angels-Thesis"
SOURCE="$PROJECT_DIR/00_source/source_original.wav"
STEMS_DIR="$PROJECT_DIR/01_stems"
VENV="$PROJECT_DIR/.venv/bin"
MODEL_DIR="/Applications/Ultimate Vocal Remover.app/Contents/Resources/models/MDX_Net_Models"
SEP="$VENV/audio-separator"

# --- 모델 이름 ---
BS_ROFORMER="model_bs_roformer_ep_317_sdr_12.9755.ckpt"
MELBAND_ROFORMER="model_mel_band_roformer_ep_3005_sdr_11.4360.ckpt"

# 출력 형식
OUTPUT_FORMAT="WAV"
SAMPLE_RATE=48000

# =============================================================================
# 함수 정의
# =============================================================================

print_header() {
    echo ""
    echo "============================================"
    echo "  $1"
    echo "============================================"
    echo ""
}

check_prerequisites() {
    print_header "사전 확인"

    if [ ! -f "$SOURCE" ]; then
        echo "ERROR: 소스 파일을 찾을 수 없습니다: $SOURCE"
        exit 1
    fi

    if [ ! -f "$SEP" ]; then
        echo "ERROR: audio-separator가 설치되지 않았습니다."
        echo "  uv venv .venv --python 3.11 && uv pip install audio-separator 'numpy<2' 'setuptools<81'"
        exit 1
    fi

    echo "소스 파일: $SOURCE"
    echo "출력 디렉토리: $STEMS_DIR"
    echo "모델 디렉토리: $MODEL_DIR"
    echo ""

    # 소스 파일 정보
    ffprobe -i "$SOURCE" -show_entries format=duration,bit_rate -of csv=p=0 2>/dev/null || true
    echo ""
}

# -----------------------------------------------------------------------------
# Step 1: BS-Roformer 단일 모델 분리
# -----------------------------------------------------------------------------
run_bs_roformer() {
    local input_file="$1"
    local output_dir="$2"
    local prefix="${3:-1}"

    print_header "Step 1: BS-Roformer 보컬/반주 분리"
    echo "모델: $BS_ROFORMER (SDR 12.98)"
    echo "입력: $input_file"
    echo "출력: $output_dir"
    echo ""

    mkdir -p "$output_dir"

    "$SEP" \
        -m "$BS_ROFORMER" \
        --model_file_dir "$MODEL_DIR" \
        --output_dir "$output_dir" \
        --output_format "$OUTPUT_FORMAT" \
        --sample_rate "$SAMPLE_RATE" \
        --custom_output_names "{\"Vocals\": \"${prefix}_source_original_(Vocals)\", \"Instrumental\": \"${prefix}_source_original_(Instrumental)\"}" \
        "$input_file"

    echo ""
    echo "분리 완료!"
    ls -lh "$output_dir"/${prefix}_source_original_*.wav 2>/dev/null || true
}

# -----------------------------------------------------------------------------
# Step 3: 앙상블 모드 (BS-Roformer + MelBand Roformer)
# -----------------------------------------------------------------------------
run_ensemble() {
    local input_file="$1"
    local output_dir="$2"
    local prefix="${3:-1}"
    local algorithm="${4:-uvr_max_spec}"

    print_header "Step 3: 앙상블 (BS-Roformer + MelBand Roformer)"
    echo "모델 1: $BS_ROFORMER (SDR 12.98)"
    echo "모델 2: $MELBAND_ROFORMER (SDR 11.44)"
    echo "알고리즘: $algorithm"
    echo "입력: $input_file"
    echo "출력: $output_dir"
    echo ""

    mkdir -p "$output_dir"

    "$SEP" \
        -m "$BS_ROFORMER" \
        --extra_models "$MELBAND_ROFORMER" \
        --model_file_dir "$MODEL_DIR" \
        --output_dir "$output_dir" \
        --output_format "$OUTPUT_FORMAT" \
        --sample_rate "$SAMPLE_RATE" \
        --ensemble_algorithm "$algorithm" \
        --custom_output_names "{\"Vocals\": \"${prefix}_source_original_(Vocals)\", \"Instrumental\": \"${prefix}_source_original_(Instrumental)\"}" \
        "$input_file"

    echo ""
    echo "앙상블 분리 완료!"
    ls -lh "$output_dir"/${prefix}_source_original_*.wav 2>/dev/null || true
}

# =============================================================================
# 메인 실행
# =============================================================================

usage() {
    echo "Usage: $0 <mode> [options]"
    echo ""
    echo "Modes:"
    echo "  single     BS-Roformer 단일 모델 분리 (기본, 빠름)"
    echo "  ensemble   BS-Roformer + MelBand Roformer 앙상블 (느림, 고품질)"
    echo ""
    echo "Options:"
    echo "  --input <path>      입력 파일 (기본: source_original.wav)"
    echo "  --output <dir>      출력 디렉토리 (기본: 01_stems)"
    echo "  --prefix <str>      출력 파일 접두사 (기본: 1)"
    echo "  --algorithm <alg>   앙상블 알고리즘 (기본: uvr_max_spec)"
    echo "                      옵션: avg_wave, avg_fft, uvr_max_spec, uvr_min_spec"
    echo ""
    echo "Examples:"
    echo "  $0 single                          # 기본 BS-Roformer 분리"
    echo "  $0 ensemble                        # 2모델 앙상블"
    echo "  $0 ensemble --algorithm avg_fft    # 안정적 앙상블"
    echo "  $0 single --input /path/to/apollo_restored.wav  # Apollo 복원 후 분리"
    echo ""
    echo "Apollo 음질 복원 (128kbps 저음질일 때):"
    echo "  → UVR5 GUI에서 수동 처리 필요"
    echo "  → CHOOSE PROCESS → Apollo → Universal_Model.ckpt"
    echo "  → 복원된 파일을 --input으로 전달"
}

# 기본값
MODE="${1:-}"
INPUT="$SOURCE"
OUTPUT="$STEMS_DIR"
PREFIX="1"
ALGORITHM="uvr_max_spec"

# 인자 파싱
shift 2>/dev/null || true
while [[ $# -gt 0 ]]; do
    case "$1" in
        --input)    INPUT="$2"; shift 2 ;;
        --output)   OUTPUT="$2"; shift 2 ;;
        --prefix)   PREFIX="$2"; shift 2 ;;
        --algorithm) ALGORITHM="$2"; shift 2 ;;
        *)          echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

case "$MODE" in
    single)
        check_prerequisites
        run_bs_roformer "$INPUT" "$OUTPUT" "$PREFIX"
        ;;
    ensemble)
        check_prerequisites
        run_ensemble "$INPUT" "$OUTPUT" "$PREFIX" "$ALGORITHM"
        ;;
    *)
        usage
        exit 1
        ;;
esac

print_header "완료"
echo "출력 파일:"
ls -lh "$OUTPUT"/${PREFIX}_source_original_*.wav 2>/dev/null || echo "(파일 없음)"
echo ""
echo "다음 단계: TODO.md Phase 3 (ffmpeg 믹싱) 참조"
