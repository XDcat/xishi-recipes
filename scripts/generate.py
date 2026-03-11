#!/usr/bin/env python3
"""
Step 4: 用 Claude API（OpenAI 兼容接口）生成结构化菜谱 Markdown。
输入：转录文本 + 视频描述 + 帧截图列表 → 输出：专业菜谱 recipe.md
"""
import sys
import json
import os
from pathlib import Path
from openai import OpenAI


def build_prompt(meta: dict, transcript: str, frame_names: list) -> str:
    """构建生成菜谱的 prompt。"""

    title = meta.get("title", "未知菜名")
    description = meta.get("description", "")
    uploader = meta.get("uploader", "")

    # 构建帧说明
    if frame_names:
        frames_info = "\n".join([f"- `{f}`" for f in frame_names])
        frames_instruction = f"""
## 可用截图

以下是从视频中截取的关键帧图片文件名，请在菜谱步骤中合理插入对应的图片。
使用 Markdown 图片语法 `![描述](./frames/文件名)` 插入。
不需要每个步骤都插图，选最有价值的（展示关键操作、成品效果等）。

{frames_info}
"""
    else:
        frames_instruction = "\n（无截图，跳过图片插入）\n"

    prompt = f"""你是一位专业的中餐菜谱编辑。请根据以下烹饪视频的转录文本，生成一份专业、清晰、实用的菜谱。

## 视频信息

- 标题：{title}
- UP主：{uploader}
- 视频描述：{description[:500] if description else '无'}

## 转录文本

{transcript}
{frames_instruction}
## 输出要求

请输出标准 Markdown 格式的菜谱，严格按以下结构：

```
---
title: 菜名
tags: [标签1, 标签2]
difficulty: ⭐⭐☆☆☆（1-5星）
servings: X人份
prep_time: X分钟
cook_time: X分钟
source: {meta.get('url', '')}
---

# 菜名

> 一句话简介（突出这道菜的特色和亮点）

## 🛒 食材

**主料：**
- 食材名 — 用量

**辅料/调料：**
- 调料名 — 用量

## 👨‍🍳 步骤

### 1. 步骤标题

步骤描述，要具体、可操作。

![步骤图](./frames/frame_xx.jpg)

### 2. 下一步...

（继续...）

## 💡 烹饪技巧

- 关键技巧 1
- 关键技巧 2

## 📝 小贴士

- 注意事项、常见错误、变体建议等
```

## 重要注意事项

1. 食材用量要从转录文本中推断，如果没提到具体用量，给出合理估计并标注"适量"
2. 步骤要详细，把视频中演示的技巧和细节写清楚
3. 如果视频中展示了多个版本/做法，请分别写出
4. 语言风格：专业但亲切，像一位有经验的厨师在耐心教学
5. 不要编造视频中没有提到的内容
6. frontmatter 中 tags 使用中文标签

只输出 Markdown 内容，不要有其他说明。
"""
    return prompt


def generate(meta_path: str) -> None:
    meta = json.loads(Path(meta_path).read_text())
    out_dir = Path(meta["out_dir"])

    # 读取转录文本
    transcript_path = out_dir / "transcript.txt"
    if not transcript_path.exists():
        print("❌ 未找到 transcript.txt，请先运行 transcribe.py")
        sys.exit(1)
    transcript = transcript_path.read_text(encoding="utf-8")

    # 读取实际截帧列表
    frames_dir = out_dir / "frames"
    frame_names = []
    if frames_dir.exists():
        frame_names = sorted([f.name for f in frames_dir.glob("frame_*.jpg")])
    print(f"📸 找到 {len(frame_names)} 张截帧")

    prompt = build_prompt(meta, transcript, frame_names)

    print("🤖 调用 Claude 生成菜谱...")
    client = OpenAI(
        base_url=os.environ.get(
            "OPENAI_BASE_URL",
            "https://wanqing-api.corp.kuaishou.com/api/agent/v1/apps"
        ),
        api_key=os.environ.get(
            "OPENAI_API_KEY",
            "7b72pjubmoh7hqsvvqw1z9ett4xdf81dyr7n"
        ),
    )
    MODEL = os.environ.get("RECIPE_MODEL", "app-0h5zc0-1773132513333160269")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        recipe_md = response.choices[0].message.content
    except Exception as e:
        print(f"❌ Claude API 调用失败：{e}")
        sys.exit(1)

    # 保存菜谱
    recipe_path = out_dir / "recipe.md"
    recipe_path.write_text(recipe_md, encoding="utf-8")
    print(f"✅ 菜谱已保存：{recipe_path}")

    # 更新 meta
    meta["recipe_path"] = str(recipe_path)
    meta.setdefault("steps_completed", [])
    if "generate" not in meta["steps_completed"]:
        meta["steps_completed"].append("generate")
    Path(meta_path).write_text(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python generate.py <meta.json路径>")
        sys.exit(1)
    generate(sys.argv[1])
