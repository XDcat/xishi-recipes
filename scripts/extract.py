#!/usr/bin/env python3
"""
Step 1: 下载 B站视频 + 音频，提取字幕（有则用，无则准备 Whisper）
"""
import subprocess
import json
import sys
import os
import re
from pathlib import Path

def slugify(text: str) -> str:
    """生成安全的文件名"""
    text = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text).strip('-')
    return text[:60]

def extract(url: str, output_dir: str = "output") -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"📥 获取视频信息: {url}")

    # 获取视频元数据
    info_result = subprocess.run(
        ["yt-dlp", "--dump-json", "--skip-download", url],
        capture_output=True, text=True
    )
    if info_result.returncode != 0:
        raise RuntimeError(f"获取视频信息失败: {info_result.stderr}")

    info = json.loads(info_result.stdout)
    title = info.get("title", "unknown")
    description = info.get("description", "")
    duration = info.get("duration", 0)
    thumbnail = info.get("thumbnail", "")
    slug = slugify(title)

    recipe_dir = output_dir / slug
    recipe_dir.mkdir(parents=True, exist_ok=True)

    print(f"📺 标题: {title}")
    print(f"⏱️  时长: {int(duration//60)}分{int(duration%60)}秒")
    print(f"📁 输出目录: {recipe_dir}")

    # 保存元数据
    meta = {
        "url": url,
        "title": title,
        "description": description,
        "duration": duration,
        "thumbnail": thumbnail,
        "slug": slug,
        "recipe_dir": str(recipe_dir),
    }
    with open(recipe_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 下载音频（用于 Whisper）
    audio_path = recipe_dir / "audio.mp3"
    if not audio_path.exists():
        print("🎵 下载音频...")
        result = subprocess.run([
            "yt-dlp",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", str(audio_path.with_suffix("")),
            url
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️  音频下载失败: {result.stderr}")
        else:
            print(f"✅ 音频已保存: {audio_path}")
    else:
        print(f"✅ 音频已存在: {audio_path}")

    # 下载视频（用于截帧，选最佳画质但不超过 1080p）
    video_path = recipe_dir / "video.mp4"
    if not video_path.exists():
        print("🎬 下载视频...")
        result = subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", str(video_path),
            url
        ], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️  视频下载失败: {result.stderr}")
        else:
            print(f"✅ 视频已保存: {video_path}")
    else:
        print(f"✅ 视频已存在: {video_path}")

    # 尝试获取 B站字幕
    subtitle_path = recipe_dir / "subtitle.srt"
    print("📝 尝试获取字幕...")
    result = subprocess.run([
        "yt-dlp",
        "--write-subs", "--write-auto-subs",
        "--sub-langs", "zh-Hans,zh-CN,zh,ai-zh",
        "--sub-format", "srt/vtt/best",
        "--skip-download",
        "-o", str(recipe_dir / "subtitle"),
        url
    ], capture_output=True, text=True)

    # 检查是否有字幕文件
    srt_files = list(recipe_dir.glob("subtitle*.srt")) + list(recipe_dir.glob("subtitle*.vtt"))
    meta["has_subtitle"] = len(srt_files) > 0
    if srt_files:
        print(f"✅ 字幕已获取: {srt_files[0]}")
        meta["subtitle_path"] = str(srt_files[0])
    else:
        print("⚠️  无可用字幕，将使用 Whisper 转录")
        meta["subtitle_path"] = None

    # 更新 meta
    with open(recipe_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 提取完成！目录: {recipe_dir}")
    return meta


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.bilibili.com/video/BV15QPCzGEMy/"
    result = extract(url)
    print(json.dumps(result, ensure_ascii=False, indent=2))
