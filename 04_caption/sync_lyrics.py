#!/usr/bin/env python3
"""
Whisper가 생성한 일본어 SRT 파일의 가사를 한국어로 치환하는 스크립트.
타이밍은 Whisper가 감지한 것을 그대로 유지하고, 텍스트만 교체합니다.
"""

import re
import sys
from difflib import SequenceMatcher

# 일본어 원문 → 한국어 번역 매핑 (순서대로)
LYRICS_MAP = [
    ("残酷な天使のように少年よ神話になれ", "잔혹한 천사처럼 소년이여 신화가 되어라"),
    ("蒼い風がいま胸のドアを叩いても", "푸른 바람이 지금 가슴의 문을 두드려도"),
    ("私だけをただ見つめて微笑んでるあなた", "나만을 그저 바라보고 미소 짓는 당신"),
    ("そっとふれるものもとめることに夢中で", "살며시 닿은 것을 추구하는 것에 열중하여"),
    ("運命さえまだ知らないいたいけな瞳", "운명조차 아직 모르는 가련한 눈동자"),
    ("だけどいつか気付くでしょうその背中には", "그래도 언젠가 깨닫게 되겠지 그 등에는"),
    ("遥か未来めざすための羽根があること", "아득한 미래로 향하기 위한 날개가 있다는 것을"),
    ("残酷な天使のテーゼ窓辺からやがて飛び立つ", "잔혹한 천사의 테제 창가에서 이윽고 날아올라"),
    ("ほとばしる熱いパトスで思い出を裏切るなら", "용솟음치는 파토스로 추억을 배반한다면"),
    ("この宇宙を抱いて輝く少年よ神話になれ", "이 우주를 품고 빛나는 소년이여 신화가 되어라"),
    ("ずっと眠ってる私の愛の揺りかご", "계속 잠자고 있는 내 사랑의 요람"),
    ("あなただけが夢の使者に呼ばれる朝がくる", "당신만이 꿈의 사자에게 부름을 받는 아침이 온다"),
    ("細い首筋を月あかりが映してる", "가느다란 목덜미를 달빛이 비추고 있어"),
    ("世界中の時を止めて閉じこめたいけど", "온 세상의 시간을 멈춰서 가두고 싶지만"),
    ("もしもふたり逢えたことに意味があるなら", "만약 우리 둘이 만난 것에 의미가 있다면"),
    ("私はそう自由を知るためのバイブル", "나는 그래 자유를 알기 위한 바이블"),
    ("残酷な天使のテーゼ悲しみがそしてはじまる", "잔혹한 천사의 테제 슬픔이 그리고 시작된다"),
    ("抱きしめた命のかたちその夢に目覚めたとき", "끌어안은 생명의 형태 그 꿈에 눈뜨는 순간"),
    ("誰よりも光を放つ少年よ神話になれ", "그 누구보다도 빛을 발하는 소년이여 신화가 되어라"),
    ("人は愛をつむぎながら歴史をつくる", "사람은 사랑을 엮으면서 역사를 만든다"),
    ("女神なんてなれないまま私は生きる", "여신 따위는 될 수 없는 채로 나는 살아간다"),
    ("残酷な天使のテーゼ窓辺からやがて飛び立つ", "잔혹한 천사의 테제 창가로부터 이윽고 날아올라"),
    ("ほとばしる熱いパトスで思い出を裏切るなら", "용솟음치는 파토스로 추억을 배반한다면"),
    ("この宇宙を抱いて輝く少年よ神話になれ", "이 우주를 품고 빛나는 소년이여 신화가 되어라"),
]


def normalize_ja(text):
    """일본어 텍스트에서 공백, 구두점 등을 제거하여 비교용 문자열 생성"""
    text = re.sub(r'[\s　、。,.!?！？♪\u200b]', '', text)
    # 그 외 특수문자 제거
    text = re.sub(r'[「」『』（）\(\)\[\]【】]', '', text)
    return text


def similarity(a, b):
    """두 문자열의 유사도를 0~1로 반환"""
    return SequenceMatcher(None, a, b).ratio()


def parse_srt(filepath):
    """SRT 파일을 파싱하여 (index, start, end, text) 리스트 반환"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content.strip())
    entries = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        idx = lines[0].strip()
        timestamp = lines[1].strip()
        text = '\n'.join(lines[2:]).strip()
        entries.append({
            'index': idx,
            'timestamp': timestamp,
            'text': text,
        })
    return entries


def map_lyrics(entries):
    """SRT 항목들의 일본어 텍스트를 한국어로 매핑"""
    used = [False] * len(LYRICS_MAP)
    result = []

    for entry in entries:
        original = entry['text']
        normalized = normalize_ja(original)

        if not normalized:
            result.append(entry)
            continue

        best_score = 0
        best_idx = -1

        for i, (ja, ko) in enumerate(LYRICS_MAP):
            if used[i]:
                continue
            norm_ja = normalize_ja(ja)
            score = similarity(normalized, norm_ja)
            if score > best_score:
                best_score = score
                best_idx = i

        if best_score > 0.3 and best_idx >= 0:
            used[best_idx] = True
            entry['text'] = LYRICS_MAP[best_idx][1]

        result.append(entry)

    return result


def write_srt(entries, filepath):
    """SRT 항목들을 파일로 출력"""
    with open(filepath, 'w', encoding='utf-8') as f:
        for i, entry in enumerate(entries):
            f.write(f"{i + 1}\n")
            f.write(f"{entry['timestamp']}\n")
            f.write(f"{entry['text']}\n")
            f.write('\n')


def main():
    input_srt = sys.argv[1] if len(sys.argv) > 1 else None
    output_srt = sys.argv[2] if len(sys.argv) > 2 else 'korean_subtitle.srt'

    if not input_srt:
        print("Usage: python3 sync_lyrics.py <input.srt> [output.srt]")
        sys.exit(1)

    entries = parse_srt(input_srt)
    print(f"SRT 항목 수: {len(entries)}")

    mapped = map_lyrics(entries)

    # 매핑 결과 출력
    for entry in mapped:
        print(f"  [{entry['timestamp'][:12]}] {entry['text']}")

    write_srt(mapped, output_srt)
    print(f"\n한국어 자막 저장: {output_srt}")


if __name__ == '__main__':
    main()
