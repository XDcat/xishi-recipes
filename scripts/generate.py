#!/usr/bin/env python3
"""
Step 4: 用 Claude API 生成结构化菜谱 Markdown（OpenAI 兼容接口）
"""
import sys
import json
import os
import re
from pathlib import Path
from openai import OpenAI

RECIPE_PROMPT = """你是一个专业的菜谱编辑，擅长将烹饪视频内容转化为清晰、实用、图文并茂的菜谱文档。

以下是一个做饭视频的信息：

**标题：** {title}
**视频描述：** {description}
**视频转录文本：**
{transcript}

请根据以上内容，生成一个高质量的菜谱 Markdown 文档。

**格式要求（严格遵守）：**

```markdown
---
title: 菜谱名称
description: 一句话描述
difficulty: 简单/中等/困难
time: XX分钟
servings: X人份
tags: [标签1, 标签2]
source: 视频标题
source_url: 视频URL
---

# 菜谱名称

> 一句吸引人的介绍语

## ⚡ 快速指南

| 项目 | 详情 |
|------|------|
| 烹饪时间 | XX分钟 |
| 准备时间 | XX分钟 |
| 难度 | ⭐⭐☆☆☆ |
| 份量 | X人份 |

### 食材清单

**主料：**
- 食材1：XX克/个/适量

**调料：**
- 调料1：XX克/ml/适量

## 📋 详细步骤

### 第一步：步骤标题

步骤详细描述...

![步骤1](./frames/frame_01.jpg)

### 第二步：步骤标题

步骤详细描述...

...

## 💡 小贴士

- 关键技巧1
- 注意事项2

## 🔗 原视频

- 来源：{title}
- 链接：{url}
```

**注意：**
1. 菜谱名称要简洁吸引人，不要照抄视频标题
2. 步骤要详细、准确，保留视频中的关键技巧
3. 食材用量要尽可能精确（视频中提到的）
4. 图片占位符 frame_01.jpg 到 frame_12.jpg，在步骤中合理分配
5. 只输出 Markdown 内容，不要有任何额外说明
"""


def generate_recipe(meta_path: str) -> dict:
    meta_path = Path(meta_path)
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    recipe_dir = Path(meta["recipe_dir"])
    recipe_md_path = recipe_dir / "recipe.md"

    if recipe_md_path.exists():
        print(f"✅ 菜谱已存在: {recipe_md_path}")
        meta["recipe_path"] = str(recipe_md_path)
        return meta

    # 读取转录文本
    transcript_path = meta.get("transcript_path")
    if not transcript_path or not Path(transcript_path).exists():
        raise FileNotFoundError("转录文本不存在，请先运行 transcribe.py")

    transcript = Path(transcript_path).read_text(encoding="utf-8")

    # 截断过长的转录文本（Claude 上下文限制）
    if len(transcript) > 8000:
        transcript = transcript[:8000] + "\n...(截断)"

    prompt = RECIPE_PROMPT.format(
        title=meta["title"],
        description=meta.get("description", "")[:500],
        transcript=transcript,
        url=meta["url"],
    )

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

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    recipe_md = response.choices[0].message.content

    # 清理可能的 markdown 代码块包装
    recipe_md = re.sub(r'^```markdown\n', '', recipe_md)
    recipe_md = re.sub(r'\n```$', '', recipe_md)

    recipe_md_path.write_text(recipe_md, encoding="utf-8")
    print(f"✅ 菜谱已生成: {recipe_md_path}")

    meta["recipe_path"] = str(recipe_md_path)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return meta


if __name__ == "__main__":
    meta_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not meta_path:
        print("用法: python generate.py <meta.json路径>")
        sys.exit(1)
    result = generate_recipe(meta_path)
    print(f"\n菜谱预览:\n{Path(result['recipe_path']).read_text()[:800]}...")
