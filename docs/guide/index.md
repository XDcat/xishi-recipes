# 使用方法

喜食AI 是一个把 B站烹饪视频自动转换成图文菜谱的工具。输入一个视频链接，输出结构完整、步骤清晰的 Markdown 菜谱并发布到本站。

## 环境准备

### 系统要求

- macOS（已针对 Apple Silicon MPS 加速优化）
- Python 3.10+
- Node.js 18+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)（`brew install yt-dlp`）
- [ffmpeg](https://ffmpeg.org/)（`brew install ffmpeg`）

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/XDcat/xishi-recipes.git
cd xishi-recipes

# 2. 创建 Python 虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 安装 Node.js 依赖（用于 VitePress 站点）
npm install
```

## 生成菜谱

```bash
# 激活虚拟环境（每次新开终端都要执行）
source .venv/bin/activate

# 基本用法：传入 B站视频 URL
python recipe.py "https://www.bilibili.com/video/BV1xxxxxxxxx/"
```

运行后会自动完成 5 个步骤：

1. **📡 Extract** — 下载视频、音频、字幕
2. **📝 Transcribe** — 优先使用 B站自带字幕；没有字幕则用本地 Whisper 转录
3. **📸 Frames** — 按内容节奏截取关键帧（最多 12 张）
4. **🤖 Generate** — AI 分析转录文本，生成结构化菜谱
5. **🌐 Publish** — 复制到 VitePress 站点，自动更新侧边栏

## 命令参数

```
python recipe.py <视频URL> [选项]

选项：
  --force          强制重跑所有步骤（忽略已有缓存）
  --no-publish     只生成菜谱，不发布到站点
  --skip-frames    跳过截帧步骤（加快速度）
  --output DIR     自定义输出目录（默认 ./output）
```

### 常用场景

```bash
# 首次运行某个视频（完整流程）
python recipe.py "https://www.bilibili.com/video/BVxxxxxx/"

# 重新生成菜谱内容（保留已有截帧）
python recipe.py "https://www.bilibili.com/video/BVxxxxxx/" --force

# 只生成、不发布（本地调试）
python recipe.py "https://www.bilibili.com/video/BVxxxxxx/" --no-publish

# 快速模式：跳过截帧
python recipe.py "https://www.bilibili.com/video/BVxxxxxx/" --skip-frames
```

## 断点续跑

每一步完成后都会在 `output/<视频>/meta.json` 里记录进度。
如果中途失败，重新运行同一条命令会自动从上次断点继续，不会重复已完成的步骤。

```bash
# 查看某个视频的进度
cat output/<视频目录>/meta.json | python3 -m json.tool | grep steps_completed
```

## 单步运行

也可以单独运行某个步骤（适合调试）：

```bash
source .venv/bin/activate

# Step 1: 下载视频
python scripts/extract.py "https://www.bilibili.com/video/BVxxxxxx/"

# Step 2: 转录（传入 meta.json 路径）
python scripts/transcribe.py output/<视频目录>/meta.json

# Step 3: 截帧
python scripts/frames.py output/<视频目录>/meta.json

# Step 4: 生成菜谱
python scripts/generate.py output/<视频目录>/meta.json

# Step 5: 发布到站点
python scripts/publish.py output/<视频目录>/meta.json
```

## 本地预览站点

```bash
npm run docs:dev
```

浏览器访问 `http://localhost:5173/xishi-recipes/` 即可预览。

## 发布到 GitHub Pages

推送到 `main` 分支后，GitHub Actions 会自动构建并部署到 GitHub Pages。

```bash
git add -A
git commit -m "recipe: 新增菜谱"
git push
```

约 1-2 分钟后访问：[https://xdcat.github.io/xishi-recipes/](https://xdcat.github.io/xishi-recipes/)

## 输出文件结构

```
output/
└── <视频标题>/
    ├── meta.json       # 视频元数据 + 流程进度
    ├── audio.mp3       # 音频（用于 Whisper 转录）
    ├── video.mp4       # 视频（用于截帧）
    ├── transcript.txt  # 纯文本转录
    ├── segments.json   # 带时间戳的分段（用于截帧定位）
    ├── frames/         # 截取的关键帧
    │   ├── frame_01.jpg
    │   └── ...
    └── recipe.md       # 生成的菜谱 Markdown

docs/recipes/
└── <slug>/
    ├── index.md        # 发布的菜谱页面
    └── frames/         # 对应截帧
```

## 常见问题

**Q: 转录很慢怎么办？**  
A: 如果 B站有字幕，会直接用字幕，秒级完成。没有字幕才用 Whisper，在 Apple Silicon 上大约 1-2 分钟。

**Q: 视频下载失败？**  
A: yt-dlp 可能需要登录 B站才能下载部分视频。运行 `yt-dlp --cookies-from-browser chrome <URL>` 或参考 [yt-dlp 文档](https://github.com/yt-dlp/yt-dlp#authentication-with-cookies)。

**Q: 生成的菜谱食材用量不准确？**  
A: AI 根据转录文本推断用量，视频里没提到的会标注"适量"。可以手动编辑 `docs/recipes/<slug>/index.md`。
