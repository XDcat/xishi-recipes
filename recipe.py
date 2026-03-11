#!/usr/bin/env python3
"""
喜食AI - 视频转菜谱 CLI
用法: python recipe.py <B站视频URL> [--output OUTPUT_DIR] [--site SITE_DIR] [--skip-frames]
"""
import sys
import argparse
import subprocess
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from extract import extract
from transcribe import transcribe
from frames import extract_frames
from generate import generate_recipe
from publish import publish


def main():
    parser = argparse.ArgumentParser(description="喜食AI - B站视频转菜谱")
    parser.add_argument("url", help="B站视频 URL")
    parser.add_argument("--output", default="output", help="临时文件输出目录（默认: output）")
    parser.add_argument("--site", default="docs", help="VitePress 站点目录（默认: docs）")
    parser.add_argument("--skip-frames", action="store_true", help="跳过截帧步骤")
    parser.add_argument("--no-publish", action="store_true", help="只生成，不发布到站点")
    args = parser.parse_args()

    print("=" * 60)
    print("🍳  喜食AI — 视频转菜谱")
    print("=" * 60)

    # Step 1: 下载视频
    print("\n[1/5] 📥 提取视频内容...")
    meta = extract(args.url, args.output)
    meta_path = Path(meta["recipe_dir"]) / "meta.json"

    # Step 2: 转录
    print("\n[2/5] 🎙️  文字转录...")
    meta = transcribe(str(meta_path))

    # Step 3: 截帧
    if not args.skip_frames:
        print("\n[3/5] 📸 截取关键帧...")
        meta = extract_frames(str(meta_path))
    else:
        print("\n[3/5] 📸 跳过截帧")

    # Step 4: 生成菜谱
    print("\n[4/5] 🤖 AI 生成菜谱...")
    meta = generate_recipe(str(meta_path))

    # Step 5: 发布
    if not args.no_publish:
        print("\n[5/5] 🚀 发布到站点...")
        publish(str(meta_path), args.site)

        # 自动 git push
        print("\n📤 推送到 GitHub...")
        try:
            subprocess.run(["git", "add", "-A"], cwd=Path(args.site).parent, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"recipe: {meta['title'][:50]}"],
                cwd=Path(args.site).parent, check=True
            )
            subprocess.run(["git", "push"], cwd=Path(args.site).parent, check=True)
            print("✅ 已推送，GitHub Actions 将自动部署")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git 操作失败: {e}")
    else:
        print("\n[5/5] 🚀 跳过发布（--no-publish）")
        print(f"📄 菜谱已生成: {meta.get('recipe_path')}")

    print("\n" + "=" * 60)
    print(f"✅ 完成！菜谱: {meta['title']}")
    if not args.no_publish:
        slug = meta["slug"]
        print(f"🌐 网址: https://xdcat.github.io/xishi-recipes/recipes/{slug}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
