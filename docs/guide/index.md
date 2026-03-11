# 使用方法

## 快速开始

```bash
# 克隆项目
git clone https://github.com/XDcat/xishi-recipes.git
cd xishi-recipes

# 安装 Python 依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 安装 Node.js 依赖（VitePress 站点）
npm install
```

## 生成菜谱

```bash
# 激活虚拟环境
source .venv/bin/activate

# 一键生成（B站视频 URL）
python recipe.py "https://www.bilibili.com/video/BVxxxxxxx/"
```

## 命令选项

| 选项 | 说明 |
|------|------|
| `--force` | 强制重跑所有步骤（忽略缓存） |
| `--no-publish` | 只生成菜谱，不发布到站点 |
| `--skip-frames` | 跳过截帧步骤 |
| `--output DIR` | 自定义输出目录 |

## 流水线步骤

1. **Extract** — 下载视频、音频、字幕
2. **Transcribe** — 优先用 B站字幕，否则 Whisper 本地转录
3. **Frames** — 从视频中截取关键帧（最多 12 张）
4. **Generate** — AI 生成结构化菜谱 Markdown
5. **Publish** — 复制到 VitePress 站点，更新侧边栏

## 本地预览

```bash
npm run docs:dev
```

浏览器访问 `http://localhost:5173/xishi-recipes/`

## 部署

推送到 `main` 分支会自动触发 GitHub Actions 部署到 GitHub Pages。
