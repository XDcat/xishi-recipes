#!/usr/bin/env python3
"""
Step 5: 发布菜谱到 VitePress 站点
- 复制 MD 和图片到 docs/recipes/
- 更新侧边栏配置
"""
import sys
import json
import shutil
import re
from pathlib import Path


def publish(meta_path: str, site_dir: str = "docs") -> dict:
    meta_path = Path(meta_path)
    site_dir = Path(site_dir)

    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    recipe_dir = Path(meta["recipe_dir"])
    slug = meta["slug"]
    recipe_md_path = recipe_dir / "recipe.md"

    if not recipe_md_path.exists():
        raise FileNotFoundError("菜谱 MD 不存在，请先运行 generate.py")

    # 创建菜谱目录
    target_dir = site_dir / "recipes" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    # 复制图片
    frames_src = recipe_dir / "frames"
    frames_dst = target_dir / "frames"
    if frames_src.exists():
        if frames_dst.exists():
            shutil.rmtree(frames_dst)
        shutil.copytree(frames_src, frames_dst)
        print(f"📸 图片已复制到 {frames_dst}")

    # 复制菜谱 MD
    target_md = target_dir / "index.md"
    shutil.copy2(recipe_md_path, target_md)
    print(f"📄 菜谱已复制到 {target_md}")

    # 读取菜谱标题
    content = recipe_md_path.read_text(encoding="utf-8")
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else meta["title"]

    # 更新侧边栏
    update_sidebar(site_dir, slug, title)

    # 更新菜谱列表页
    update_recipe_index(site_dir, slug, title, meta)

    print(f"\n✅ 发布完成！")
    print(f"📖 地址: /recipes/{slug}/")
    return meta


def update_sidebar(site_dir: Path, slug: str, title: str):
    config_path = site_dir / ".vitepress" / "config.ts"
    config = config_path.read_text(encoding="utf-8")

    entry = f"{{ text: '{title}', link: '/recipes/{slug}/' }}"

    if slug in config:
        print("📌 侧边栏已有该菜谱")
        return

    # 在 items 数组中插入
    config = config.replace(
        "// 自动生成的菜谱会插入这里",
        f"{entry},\n            // 自动生成的菜谱会插入这里"
    )
    config_path.write_text(config, encoding="utf-8")
    print(f"📌 侧边栏已更新: {title}")


def update_recipe_index(site_dir: Path, slug: str, title: str, meta: dict):
    index_path = site_dir / "recipes" / "index.md"
    content = index_path.read_text(encoding="utf-8")

    # 读取菜谱 frontmatter 获取标签
    recipe_content = (site_dir / "recipes" / slug / "index.md").read_text(encoding="utf-8")
    desc_match = re.search(r'description:\s*(.+)', recipe_content)
    desc = desc_match.group(1).strip() if desc_match else ""

    entry = f"\n### 🍳 [{title}](./{slug}/)\n\n{desc}\n"

    if slug in content:
        return

    content = content.replace(
        "> 🍳 菜谱正在陆续添加中，敬请期待...",
        entry + "\n---\n\n> 🍳 更多菜谱持续添加中..."
    )
    index_path.write_text(content, encoding="utf-8")
    print(f"📋 菜谱列表已更新")


if __name__ == "__main__":
    meta_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not meta_path:
        print("用法: python publish.py <meta.json路径>")
        sys.exit(1)
    publish(meta_path)
