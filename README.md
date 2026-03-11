# 喜食AI 🍳

> 粘一个 B站做饭视频，自动生成图文并茂的专业菜谱。

**在线地址：** https://xdcat.github.io/xishi-recipes/

---

## 这是什么

给自己做的一个懒人工具——看到好吃的视频，不想手动记菜谱，让 AI 帮我整理。

输入 B站视频链接，自动：
1. 下载视频音频，提取字幕（有 CC 字幕用字幕，没有用 Whisper 转录）
2. 截取关键烹饪步骤截图
3. 用 Claude AI 生成结构化菜谱（食材 / 步骤 / 技巧 / 小贴士）
4. 发布到 VitePress 静态站点，GitHub Pages 部署

---

## 快速开始

### 环境要求

```bash
# 系统依赖
brew install yt-dlp ffmpeg

# Python 依赖
pip install -r requirements.txt
# 内含：openai-whisper anthropic torch

# 环境变量
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 用法

```bash
# 一键生成菜谱（下载 → 转录 → 截帧 → 生成 → 发布）
python recipe.py https://www.bilibili.com/video/BV15QPCzGEMy/

# 只生成不发布
python recipe.py <URL> --no-publish

# 跳过截帧（加快速度）
python recipe.py <URL> --skip-frames

# 自定义输出目录
python recipe.py <URL> --output ./my-output
```

### 单步运行（调试用）

```bash
# Step 1: 下载
python scripts/extract.py <URL>

# Step 2: 转录（需要先有 meta.json）
python scripts/transcribe.py output/<slug>/meta.json

# Step 3: 截帧
python scripts/frames.py output/<slug>/meta.json

# Step 4: 生成菜谱
python scripts/generate.py output/<slug>/meta.json

# Step 5: 发布到站点
python scripts/publish.py output/<slug>/meta.json
```

---

## 项目结构

```
xishi-recipes/
├── recipe.py           # 主入口 CLI
├── requirements.txt    # Python 依赖
├── plan.md             # 项目规划
├── scripts/
│   ├── extract.py      # Step 1: 下载视频/音频/字幕
│   ├── transcribe.py   # Step 2: 语音转文字
│   ├── frames.py       # Step 3: 截取关键帧
│   ├── generate.py     # Step 4: Claude 生成菜谱
│   └── publish.py      # Step 5: 发布到 VitePress
├── output/             # 临时文件（gitignore）
│   └── <slug>/
│       ├── meta.json
│       ├── audio.mp3
│       ├── video.mp4
│       ├── transcript.txt
│       ├── segments.json
│       ├── frames/
│       └── recipe.md
└── docs/               # VitePress 站点
    ├── .vitepress/
    ├── index.md        # 首页
    └── recipes/        # 菜谱页面
        └── <slug>/
            ├── index.md
            └── frames/
```

---

## 技术栈

- **下载：** [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **转录：** [OpenAI Whisper](https://github.com/openai/whisper)（本地，M系Mac MPS加速）
- **截帧：** [ffmpeg](https://ffmpeg.org/)
- **AI 生成：** [Claude](https://anthropic.com/)（claude-opus-4-5）
- **站点：** [VitePress](https://vitepress.dev/)
- **部署：** GitHub Pages

---

## License

MIT
