#!/usr/bin/env python3
"""
Step 2: 语音转文字
- 优先用已有字幕（B站 CC）
- 无字幕则用 Whisper large-v3（MPS 加速）
"""
import sys
import json
import re
from pathlib import Path


def parse_srt(srt_path: str) -> str:
    """解析 SRT 字幕，返回纯文本"""
    content = Path(srt_path).read_text(encoding="utf-8")
    # 去掉序号和时间戳，只保留文本
    lines = []
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        if re.match(r"^\d+$", line):
            continue
        if re.match(r"^\d{2}:\d{2}:\d{2}", line):
            continue
        lines.append(line)
    return " ".join(lines)


def transcribe_whisper(audio_path: str, language: str = "zh") -> str:
    """用 Whisper large-v3 转录音频（M系Mac用MPS加速）"""
    try:
        import whisper
        import torch
    except ImportError:
        print("📦 安装 Whisper...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper", "-q"], check=True)
        import whisper
        import torch

    # M系Mac用MPS，否则CPU
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"🔧 使用设备: {device}")
    print(f"📦 加载 Whisper medium 模型...")

    # large-v3 太大容易超时，medium 对中文效果也很好
    model_name = "medium"
    model = whisper.load_model(model_name, device=device)

    print(f"🎙️  开始转录: {audio_path}")
    result = model.transcribe(
        audio_path,
        language=language,
        verbose=False,
        fp16=False,  # MPS 暂不支持 fp16
        initial_prompt="这是一个中文烹饪视频，包含食材介绍和烹饪步骤。"
    )

    # 带时间戳的文本，方便后续截帧对齐
    segments = result.get("segments", [])
    text = result["text"]

    return text, segments


def transcribe(meta_path: str) -> dict:
    meta_path = Path(meta_path)
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    recipe_dir = Path(meta["recipe_dir"])
    transcript_path = recipe_dir / "transcript.txt"
    segments_path = recipe_dir / "segments.json"

    # 已有转录就跳过
    if transcript_path.exists():
        print(f"✅ 转录已存在: {transcript_path}")
        meta["transcript_path"] = str(transcript_path)
        return meta

    if meta.get("has_subtitle") and meta.get("subtitle_path"):
        print("📝 使用 B站字幕...")
        text = parse_srt(meta["subtitle_path"])
        segments = []
    else:
        print("🎙️  使用 Whisper 转录...")
        audio_path = recipe_dir / "audio.mp3"
        text, segments = transcribe_whisper(str(audio_path))

    transcript_path.write_text(text, encoding="utf-8")
    with open(segments_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)

    print(f"✅ 转录完成（{len(text)} 字）: {transcript_path}")
    meta["transcript_path"] = str(transcript_path)
    meta["segments_path"] = str(segments_path)

    # 更新 meta
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return meta


if __name__ == "__main__":
    meta_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not meta_path:
        print("用法: python transcribe.py <meta.json路径>")
        sys.exit(1)
    result = transcribe(meta_path)
    print(f"\n转录预览:\n{Path(result['transcript_path']).read_text()[:500]}...")
