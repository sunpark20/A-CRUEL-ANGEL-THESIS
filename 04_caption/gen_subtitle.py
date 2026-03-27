#!/usr/bin/env python3
"""
기존 ko_cleaned.ass에서 타이밍을 유지하면서
일본어(작게) + 한국어(보통) 2줄 자막 ASS 파일을 생성.
"""

import re
import glob

# 기존 ASS 파일 읽기
ass_files = glob.glob("/Users/sunguk/0.code/caption/*.ko_cleaned.ass")
if not ass_files:
    raise FileNotFoundError("ko_cleaned.ass not found")

with open(ass_files[0], 'r', encoding='utf-8') as f:
    content = f.read()

# Dialogue 항목 파싱
dialogue_pattern = re.compile(
    r'Dialogue:\s*(\d+),(\d:\d{2}:\d{2}\.\d{2}),(\d:\d{2}:\d{2}\.\d{2}),([^,]*),([^,]*),(\d+),(\d+),(\d+),([^,]*),(.*)'
)

dialogues = []
for m in dialogue_pattern.finditer(content):
    layer, start, end, style, name, ml, mr, mv, effect, text = m.groups()
    dialogues.append({
        'layer': layer,
        'start': start,
        'end': end,
        'style': style,
        'name': name,
        'ml': ml, 'mr': mr, 'mv': mv,
        'effect': effect,
        'text': text,
    })

print(f"파싱된 Dialogue 수: {len(dialogues)}")

# 새 ASS 파일 생성 (PlayRes 3840x2160, 4K 직접 좌표)
JA_SIZE = 38   # 일본어: 작게
KO_SIZE = 52   # 한국어: 보통
OUTLINE = 2.5
SHADOW = 1

header = f"""[Script Info]
; Bilingual subtitle - Japanese (small) + Korean (normal)
ScriptType: v4.00+
PlayResX: 3840
PlayResY: 2160
ScaledBorderAndShadow: yes
YCbCr Matrix: None

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Hiragino Kaku Gothic ProN,{KO_SIZE},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{OUTLINE},{SHADOW},2,40,40,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

lines = []
for d in dialogues:
    text = d['text']

    # \N으로 구분된 일본어/한국어 분리
    if '\\N' in text:
        parts = text.split('\\N')
        ja_part = parts[0].strip()
        ko_part = parts[1].strip()

        # 불필요한 따옴표 제거
        ja_part = ja_part.strip("'\"")
        ko_part = ko_part.strip("'\"")

        # 인라인 크기 오버라이드: 일본어 작게, 한국어 보통
        new_text = f"{{\\fs{JA_SIZE}}}{ja_part}\\N{{\\fs{KO_SIZE}}}{ko_part}"
    else:
        # 단일 줄 (일본어만 또는 한국어만)
        new_text = f"{{\\fs{JA_SIZE}}}{text.strip(chr(39)).strip(chr(34))}"

    line = f"Dialogue: {d['layer']},{d['start']},{d['end']},Default,,0,0,0,,{new_text}"
    lines.append(line)

output_path = "/Users/sunguk/0.code/caption/subtitle_final.ass"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(header)
    for line in lines:
        f.write(line + '\n')

print(f"생성 완료: {output_path}")
print(f"Dialogue 항목: {len(lines)}개")

# 결과 미리보기
for line in lines[:5]:
    # Text 부분만 추출
    text_part = line.split(',', 9)[-1]
    print(f"  {text_part}")
