#!/usr/bin/env python3
"""
Step 3: 截取关键帧
- 根据 Whisper segments 的时间戳，在步骤变化时截图
- 无 segments 则均匀截帧
"""
import sys
import json
import subprocess
from pathlib import Path


def extract_frames(meta_path: str, max_frames: int = 12) -> dict:
    meta_path = Path(meta_path)
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    recipe_dir = Path(meta["recipe_dir"])
    frames_dir = recipe_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    video_path = recipe_dir / "video.mp4"
    if not video_path.exists():
        print("⚠️  视频文件不存在，跳过截帧")
        meta["frames"] = []
        return meta

    duration = meta.get("duration", 0)

    # 尝试从 segments 中找关键时间点
    segments_path = recipe_dir / "segments.json"
    timestamps = []

    if segments_path.exists():
        with open(segments_path, encoding="utf-8") as f:
            segments = json.load(f)
        if segments:
            # 每隔 N 个 segment 取一帧，控制总数
            step = max(1, len(segments) // max_frames)
            timestamps = [seg["start"] for seg in segments[::step]][:max_frames]

    if not timestamps:
        # 均匀截帧：跳过片头片尾 10%
        start = duration * 0.1
        end = duration * 0.9
        interval = (end - start) / max_frames
        timestamps = [start + i * interval for i in range(max_frames)]

    print(f"📸 截取 {len(timestamps)} 帧...")
    frames = []

    for i, ts in enumerate(timestamps):
        frame_path = frames_dir / f"frame_{i+1:02d}.jpg"
        if frame_path.exists():
            frames.append({"index": i+1, "timestamp": ts, "path": str(frame_path)})
            continue

        result = subprocess.run([
            "ffmpeg", "-y",
            "-ss", str(ts),
            "-i", str(video_path),
            "-frames:v", "1",
            "-q:v", "2",
            "-vf", "scale=1280:-2",
            str(frame_path)
        ], capture_output=True, text=True)

        if result.returncode == 0:
            frames.append({"index": i+1, "timestamp": ts, "path": str(frame_path)})
            print(f"  ✅ 帧 {i+1}: {int(ts//60)}:{int(ts%60):02d}")
        else:
            print(f"  ⚠️  帧 {i+1} 失败: {result.stderr[:100]}")

    meta["frames"] = frames
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 截帧完成: {frames_dir}")
    return meta


if __name__ == "__main__":
    meta_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not meta_path:
        print("用法: python frames.py <meta.json路径>")
        sys.exit(1)
    extract_frames(meta_path)
