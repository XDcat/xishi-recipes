#!/usr/bin/env python3
"""
Step 3: 用 ffmpeg 按时间戳截取关键帧。
优先使用 Whisper/字幕 segments 时间戳，每隔 N 秒取一帧；
没有 segments 则均匀截取最多 12 帧。
"""
import sys
import json
import subprocess
from pathlib import Path


MAX_FRAMES = 12


def seconds_to_ts(sec: float) -> str:
    """秒数转 HH:MM:SS.mmm 格式。"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def capture_frame(video_path: str, timestamp: str, out_path: str) -> bool:
    """用 ffmpeg 截取单帧。"""
    r = subprocess.run(
        ["ffmpeg", "-y", "-ss", timestamp, "-i", video_path,
         "-vframes", "1", "-q:v", "2", out_path],
        capture_output=True, text=True
    )
    return r.returncode == 0 and Path(out_path).exists()


def frames(meta_path: str) -> None:
    meta = json.loads(Path(meta_path).read_text())
    out_dir = Path(meta["out_dir"])
    video_path = meta.get("video_path")

    if not video_path or not Path(video_path).exists():
        print("❌ 没有视频文件，跳过截帧")
        meta["frames_dir"] = None
        meta["frame_paths"] = []
        if "frames" not in meta.get("steps_completed", []):
            meta.setdefault("steps_completed", []).append("frames")
        Path(meta_path).write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        return

    frames_dir = out_dir / "frames"
    frames_dir.mkdir(exist_ok=True)

    duration = meta.get("duration", 0) or 0
    segments_path = meta.get("segments_path")

    timestamps = []

    if segments_path and Path(segments_path).exists():
        segments = json.loads(Path(segments_path).read_text())
        print(f"🕐 使用字幕 segments 时间戳（共 {len(segments)} 段）...")

        # 兼容两种 segments 格式：新格式有 start_sec，旧 Whisper 格式有 start（秒数浮点）
        def get_secs(seg: dict, key: str) -> float:
            sec_key = key + "_sec"
            if sec_key in seg:
                return seg[sec_key]
            v = seg.get(key, 0)
            # 如果是纯数字（Whisper float），直接用
            if isinstance(v, (int, float)):
                return float(v)
            # 否则是时间字符串，转换
            return time_to_seconds(v) if v else 0.0

        # 按间隔采样：每 (duration / MAX_FRAMES) 秒选一个 segment 的中点
        if duration > 0 and len(segments) > 0:
            interval = max(duration / MAX_FRAMES, 10)
            last_ts = -interval
            for seg in segments:
                mid = (get_secs(seg, "start") + get_secs(seg, "end")) / 2
                if mid - last_ts >= interval:
                    timestamps.append(mid)
                    last_ts = mid
                    if len(timestamps) >= MAX_FRAMES:
                        break
        else:
            # 直接取前 MAX_FRAMES 个 segment 中点
            for seg in segments[:MAX_FRAMES]:
                mid = (get_secs(seg, "start") + get_secs(seg, "end")) / 2
                timestamps.append(mid)
    else:
        # 均匀截帧
        print("📐 均匀截帧...")
        if duration > 0:
            count = min(MAX_FRAMES, max(1, int(duration / 30)))
            interval = duration / (count + 1)
            timestamps = [interval * (i + 1) for i in range(count)]
        else:
            timestamps = [i * 10 for i in range(MAX_FRAMES)]

    # 过滤掉超出时长的时间戳
    if duration > 0:
        timestamps = [t for t in timestamps if t < duration - 1]

    print(f"📸 截取 {len(timestamps)} 帧...")
    frame_paths = []
    for i, ts in enumerate(timestamps, 1):
        ts_str = seconds_to_ts(ts)
        out_path = str(frames_dir / f"frame_{i:02d}.jpg")
        if capture_frame(video_path, ts_str, out_path):
            frame_paths.append(out_path)
            print(f"  ✅ frame_{i:02d}.jpg @ {ts_str}")
        else:
            print(f"  ⚠️  frame_{i:02d}.jpg 截帧失败 @ {ts_str}")

    print(f"✅ 截帧完成，共 {len(frame_paths)} 张")

    meta["frames_dir"] = str(frames_dir)
    meta["frame_paths"] = frame_paths
    meta.setdefault("steps_completed", [])
    if "frames" not in meta["steps_completed"]:
        meta["steps_completed"].append("frames")
    Path(meta_path).write_text(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python frames.py <meta.json路径>")
        sys.exit(1)
    frames(sys.argv[1])
