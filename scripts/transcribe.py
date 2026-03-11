#!/usr/bin/env python3
"""
Step 2: 语音转文字。
优先使用 B站自带字幕；没有字幕则用本地 Whisper 转录。
输出：transcript.txt（纯文本）+ segments.json（带时间戳）
"""
import sys
import json
import re
from pathlib import Path


def parse_vtt(vtt_path: str) -> tuple[str, list]:
    """解析 VTT 字幕文件，返回 (纯文本, segments列表)。"""
    text_lines = []
    segments = []
    time_re = re.compile(r'(\d+:\d+:\d+\.\d+)\s+-->\s+(\d+:\d+:\d+\.\d+)')

    with open(vtt_path, encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\n+', content)
    for block in blocks:
        lines = block.strip().splitlines()
        if not lines:
            continue
        time_match = None
        text_parts = []
        for line in lines:
            m = time_re.match(line)
            if m:
                time_match = m
            elif line and not line.startswith('WEBVTT') and not re.match(r'^\d+$', line):
                # 去掉 HTML 标签
                clean = re.sub(r'<[^>]+>', '', line).strip()
                if clean:
                    text_parts.append(clean)
        if time_match and text_parts:
            text = ' '.join(text_parts)
            segments.append({
                "start": time_match.group(1),
                "end": time_match.group(2),
                "text": text,
            })
            text_lines.append(text)

    return '\n'.join(text_lines), segments


def time_to_seconds(t: str) -> float:
    """把 HH:MM:SS.mmm 转成秒数。"""
    parts = t.split(':')
    h, m, s = int(parts[0]), int(parts[1]), float(parts[2])
    return h * 3600 + m * 60 + s


def transcribe(meta_path: str) -> None:
    meta = json.loads(Path(meta_path).read_text())
    out_dir = Path(meta["out_dir"])
    transcript_path = out_dir / "transcript.txt"
    segments_path = out_dir / "segments.json"

    # 如果有字幕，直接解析
    if meta.get("subtitle_path") and Path(meta["subtitle_path"]).exists():
        print(f"📝 解析 B站字幕：{meta['subtitle_path']}")
        text, segments = parse_vtt(meta["subtitle_path"])

        # 把 segments 的时间转成秒数，方便截帧使用
        segs_with_secs = []
        for seg in segments:
            segs_with_secs.append({
                **seg,
                "start_sec": time_to_seconds(seg["start"]),
                "end_sec": time_to_seconds(seg["end"]),
            })

        transcript_path.write_text(text, encoding='utf-8')
        segments_path.write_text(json.dumps(segs_with_secs, ensure_ascii=False, indent=2))
        print(f"✅ 字幕转录完成，共 {len(segments)} 段")

    elif meta.get("audio_path") and Path(meta["audio_path"]).exists():
        print("🤖 使用 Whisper 本地转录（首次运行需下载模型，约 1-2 分钟）...")
        try:
            import whisper
        except ImportError:
            print("❌ 未安装 whisper：pip install openai-whisper")
            sys.exit(1)

        model = whisper.load_model("medium")
        print("🎙️  转录中...")
        result = model.transcribe(meta["audio_path"], language="zh")

        text = result["text"]
        segments = [
            {
                "start": f"00:{int(s['start']//60):02d}:{s['start']%60:06.3f}",
                "end": f"00:{int(s['end']//60):02d}:{s['end']%60:06.3f}",
                "start_sec": s["start"],
                "end_sec": s["end"],
                "text": s["text"],
            }
            for s in result.get("segments", [])
        ]

        transcript_path.write_text(text, encoding='utf-8')
        segments_path.write_text(json.dumps(segments, ensure_ascii=False, indent=2))
        print(f"✅ Whisper 转录完成，共 {len(segments)} 段")

    else:
        print("❌ 没有字幕文件也没有音频文件，无法转录")
        sys.exit(1)

    # 更新 meta
    meta["transcript_path"] = str(transcript_path)
    meta["segments_path"] = str(segments_path)
    if "steps_completed" not in meta:
        meta["steps_completed"] = []
    if "transcribe" not in meta["steps_completed"]:
        meta["steps_completed"].append("transcribe")
    Path(meta_path).write_text(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python transcribe.py <meta.json路径>")
        sys.exit(1)
    transcribe(sys.argv[1])
