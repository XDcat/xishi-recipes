#!/usr/bin/env python3
"""
Step 1: 下载 B站视频、音频和字幕，保存 meta.json。
"""
import sys
import json
import re
import subprocess
from pathlib import Path


OUTPUT_DIR = Path(__file__).parent.parent / "output"


def slugify(text: str) -> str:
    """把视频标题转成合法目录名。"""
    text = re.sub(r'[^\w\u4e00-\u9fff\-]', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    return text[:80]


def extract(url: str) -> dict:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # 先获取视频信息
    print("📡 获取视频信息...")
    result = subprocess.run(
        ["yt-dlp", "--dump-json", "--no-playlist", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ 获取视频信息失败：{result.stderr[:300]}")
        sys.exit(1)

    info = json.loads(result.stdout)
    title = info.get("title", "unknown")
    video_id = info.get("id", "unknown")
    slug = slugify(title)
    out_dir = OUTPUT_DIR / slug
    out_dir.mkdir(exist_ok=True)

    print(f"📺 视频：{title}")
    print(f"📁 输出目录：{out_dir}")

    # 下载音频（用于 Whisper 转录备用）
    audio_path = out_dir / "audio.%(ext)s"
    print("🎵 下载音频...")
    r = subprocess.run(
        ["yt-dlp", "-x", "--audio-format", "mp3",
         "-o", str(audio_path), url],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"⚠️  音频下载失败（继续）：{r.stderr[:200]}")
    audio_file = out_dir / "audio.mp3"

    # 下载视频（用于截帧）
    video_path = out_dir / "video.%(ext)s"
    print("🎬 下载视频...")
    r = subprocess.run(
        ["yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
         "-o", str(video_path), url],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"⚠️  视频下载失败（继续）：{r.stderr[:200]}")
    # 找实际下载的视频文件
    video_files = list(out_dir.glob("video.*"))
    video_file = video_files[0] if video_files else None

    # 尝试下载字幕
    print("📝 尝试下载 B站字幕...")
    subtitle_path = None
    r = subprocess.run(
        ["yt-dlp", "--write-auto-sub", "--skip-download",
         "--sub-langs", "zh-Hans,zh,zh-CN",
         "-o", str(out_dir / "%(title)s"), url],
        capture_output=True, text=True
    )
    sub_files = list(out_dir.glob("*.vtt")) + list(out_dir.glob("*.srt"))
    if sub_files:
        subtitle_path = str(sub_files[0])
        print(f"✅ 字幕：{sub_files[0].name}")
    else:
        print("ℹ️  未找到字幕，将使用 Whisper 转录")

    meta = {
        "url": url,
        "video_id": video_id,
        "title": title,
        "slug": slug,
        "out_dir": str(out_dir),
        "audio_path": str(audio_file) if audio_file.exists() else None,
        "video_path": str(video_file) if video_file and video_file.exists() else None,
        "subtitle_path": subtitle_path,
        "description": info.get("description", ""),
        "duration": info.get("duration"),
        "uploader": info.get("uploader", ""),
        "steps_completed": ["extract"],
    }

    meta_path = out_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"✅ meta.json 已保存：{meta_path}")
    return meta


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python extract.py <B站视频URL>")
        sys.exit(1)
    extract(sys.argv[1])
