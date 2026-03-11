#!/usr/bin/env python3
"""
喜食AI 主入口 — B站视频 → 专业菜谱

用法：
  python recipe.py <B站视频URL> [选项]

选项：
  --no-publish    只生成不发布到站点
  --skip-frames   跳过截帧步骤（加快速度）
  --force         强制重跑所有步骤（忽略已完成的缓存）
  --output DIR    自定义输出目录（默认 ./output）
"""
import sys
import json
import argparse
from pathlib import Path

# 确保 scripts 目录在 path 里
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from extract import extract
from transcribe import transcribe
from frames import frames
from generate import generate
from publish import publish


def find_meta(output_base: Path, url: str) -> Path | None:
    """在 output 目录下查找已存在的 meta.json（通过 url 匹配）。"""
    if not output_base.exists():
        return None
    for meta_file in output_base.glob("*/meta.json"):
        try:
            meta = json.loads(meta_file.read_text())
            if meta.get("url") == url:
                return meta_file
        except Exception:
            pass
    return None


def run_step(name: str, fn, *args, completed_steps: list, force: bool) -> None:
    """运行单个步骤，支持断点续跑。"""
    if not force and name in completed_steps:
        print(f"⏭️  跳过 {name}（已完成，使用 --force 重新运行）")
        return
    print(f"\n{'='*50}")
    print(f"▶  步骤：{name.upper()}")
    print(f"{'='*50}")
    fn(*args)


def main():
    parser = argparse.ArgumentParser(
        description="B站视频 → 专业菜谱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("url", help="B站视频 URL")
    parser.add_argument("--no-publish", action="store_true", help="只生成不发布")
    parser.add_argument("--skip-frames", action="store_true", help="跳过截帧步骤")
    parser.add_argument("--force", action="store_true", help="强制重跑所有步骤")
    parser.add_argument("--output", default=None, help="自定义输出目录")
    args = parser.parse_args()

    # 自定义输出目录
    if args.output:
        import os
        os.environ["RECIPE_OUTPUT_DIR"] = args.output

    print("🍳 喜食AI — B站视频菜谱生成器")
    print(f"📺 视频：{args.url}\n")

    # 查找已有 meta（断点续跑）
    output_base = Path(__file__).parent / "output"
    if args.output:
        output_base = Path(args.output)

    meta_path = None
    if not args.force:
        meta_path = find_meta(output_base, args.url)
        if meta_path:
            meta = json.loads(meta_path.read_text())
            completed = meta.get("steps_completed", [])
            print(f"📌 找到已有进度：{completed}")

    # Step 1: Extract
    if meta_path is None:
        # 首次运行
        meta = extract(args.url)
        out_dir = Path(meta["out_dir"])
        meta_path = out_dir / "meta.json"
    else:
        meta = json.loads(meta_path.read_text())
        completed = meta.get("steps_completed", [])
        run_step("extract", extract, args.url, completed_steps=completed, force=args.force)
        # extract 会重新写 meta，重新读
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else meta

    # 重新找 meta_path（extract 可能改了 slug）
    output_base = Path(__file__).parent / "output"
    meta_path = find_meta(output_base, args.url)
    if not meta_path:
        print("❌ extract 后找不到 meta.json")
        sys.exit(1)

    meta = json.loads(meta_path.read_text())
    completed = meta.get("steps_completed", [])

    # Step 2: Transcribe
    run_step("transcribe", transcribe, str(meta_path),
             completed_steps=completed, force=args.force)
    meta = json.loads(meta_path.read_text())
    completed = meta.get("steps_completed", [])

    # Step 3: Frames
    if not args.skip_frames:
        run_step("frames", frames, str(meta_path),
                 completed_steps=completed, force=args.force)
        meta = json.loads(meta_path.read_text())
        completed = meta.get("steps_completed", [])
    else:
        print("⏭️  跳过截帧（--skip-frames）")

    # Step 4: Generate
    run_step("generate", generate, str(meta_path),
             completed_steps=completed, force=args.force)
    meta = json.loads(meta_path.read_text())
    completed = meta.get("steps_completed", [])

    # Step 5: Publish
    if not args.no_publish:
        run_step("publish", publish, str(meta_path),
                 completed_steps=completed, force=args.force)

    print("\n✅ 全部完成！")
    if not args.no_publish:
        slug = meta.get("slug", "")
        print(f"📖 查看菜谱：docs/recipes/{slug}/index.md")
        print("🌐 本地预览：npm run docs:dev（在项目根目录）")


if __name__ == "__main__":
    main()
