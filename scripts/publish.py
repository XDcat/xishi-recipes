#!/usr/bin/env python3
"""
Step 5: 把生成的菜谱发布到 VitePress docs 站点。
复制 recipe.md + frames/ 到 docs/recipes/<slug>/，
然后重新扫描 docs/recipes/ 目录，更新 VitePress 侧边栏配置。
"""
import sys
import json
import re
import shutil
from pathlib import Path


DOCS_DIR = Path(__file__).parent.parent / "docs"
RECIPES_DIR = DOCS_DIR / "recipes"
CONFIG_PATH = DOCS_DIR / ".vitepress" / "config.ts"


def slugify_title(md_path: Path) -> str:
    """从 recipe.md frontmatter 读取 title，生成侧边栏显示名。"""
    try:
        content = md_path.read_text(encoding="utf-8")
        m = re.search(r'^title:\s*(.+)$', content, re.MULTILINE)
        if m:
            return m.group(1).strip().strip('"\'')
    except Exception:
        pass
    return md_path.parent.name


def update_sidebar(sidebar_items: list) -> None:
    """更新 config.ts 中 recipes 侧边栏部分。"""
    if not CONFIG_PATH.exists():
        print("⚠️  config.ts 不存在，跳过侧边栏更新")
        return

    # 构建新的 sidebar items 字符串
    items_lines = []
    for item in sidebar_items:
        items_lines.append(
            f"          {{ text: '{item['text']}', link: '{item['link']}' }},"
        )
    items_str = "\n".join(items_lines)

    new_sidebar_block = f"""{{
        text: '所有菜谱',
        items: [
{items_str}
        ]
      }}"""

    config_text = CONFIG_PATH.read_text(encoding="utf-8")

    # 用正则替换 sidebar recipes 部分（整个 { text: '所有菜谱', ... } 块）
    pattern = r'\{[^{}]*text:\s*[\'"]所有菜谱[\'"].*?\}'
    if re.search(pattern, config_text, re.DOTALL):
        new_config = re.sub(pattern, new_sidebar_block, config_text, flags=re.DOTALL)
    else:
        # 如果没有找到，尝试替换整个 sidebar 的 recipes 数组
        print("⚠️  未找到侧边栏 recipes 块，追加到文件末尾前")
        new_config = config_text

    CONFIG_PATH.write_text(new_config, encoding="utf-8")
    print(f"✅ 侧边栏已更新（{len(sidebar_items)} 个菜谱）")


def publish(meta_path: str) -> None:
    meta = json.loads(Path(meta_path).read_text())
    out_dir = Path(meta["out_dir"])
    slug = meta["slug"]

    recipe_src = out_dir / "recipe.md"
    if not recipe_src.exists():
        print("❌ 未找到 recipe.md，请先运行 generate.py")
        sys.exit(1)

    # 目标目录
    dest_dir = RECIPES_DIR / slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 复制 recipe.md → index.md
    dest_recipe = dest_dir / "index.md"
    shutil.copy2(recipe_src, dest_recipe)
    print(f"📄 复制菜谱：{dest_recipe}")

    # 复制 frames/
    frames_src = out_dir / "frames"
    if frames_src.exists():
        dest_frames = dest_dir / "frames"
        if dest_frames.exists():
            shutil.rmtree(dest_frames)
        shutil.copytree(frames_src, dest_frames)
        frame_count = len(list(dest_frames.glob("*.jpg")))
        print(f"🖼️  复制截帧：{frame_count} 张")

    # 扫描所有已发布菜谱，重建侧边栏
    sidebar_items = []
    for recipe_dir in sorted(RECIPES_DIR.iterdir()):
        if not recipe_dir.is_dir():
            continue
        index_md = recipe_dir / "index.md"
        if not index_md.exists():
            continue
        title = slugify_title(index_md)
        sidebar_items.append({
            "text": title,
            "link": f"/recipes/{recipe_dir.name}/",
        })

    update_sidebar(sidebar_items)

    # 更新菜谱列表页
    update_recipe_list(sidebar_items)

    # 更新 meta
    meta["published_path"] = str(dest_recipe)
    meta.setdefault("steps_completed", [])
    if "publish" not in meta["steps_completed"]:
        meta["steps_completed"].append("publish")
    Path(meta_path).write_text(json.dumps(meta, ensure_ascii=False, indent=2))

    print(f"🎉 发布完成：docs/recipes/{slug}/")


def update_recipe_list(sidebar_items: list) -> None:
    """更新 docs/recipes/index.md 菜谱列表页。"""
    index_path = RECIPES_DIR / "index.md"
    lines = ["# 所有菜谱\n"]
    for item in sidebar_items:
        lines.append(f"- [{item['text']}]({item['link']})")
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"📋 菜谱列表已更新（{len(sidebar_items)} 个）")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python publish.py <meta.json路径>")
        sys.exit(1)
    publish(sys.argv[1])
