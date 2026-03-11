# 喜食AI — 项目规划

## 现状评估

### ✅ 已完成
- 完整的 5 步 Pipeline 骨架：`extract → transcribe → frames → generate → publish`
- `extract.py`：yt-dlp 下载音频/视频 + B站字幕尝试，保存 meta.json
- `transcribe.py`：优先用 B站字幕，无则 Whisper medium 转录
- `frames.py`：按 segment 时间戳或均匀截帧（最多 12 帧）
- `generate.py`：Claude API 生成结构化 Markdown 菜谱
- `publish.py`：复制到 VitePress docs，更新侧边栏 & 菜谱列表
- `recipe.py`：主入口 CLI，把 5 步串起来
- VitePress 站点基础搭建 + GitHub Actions 准备（package.json 里有 build 脚本）

### ❌ 已知问题 / 未完成

| 问题 | 优先级 | 说明 |
|------|--------|------|
| 未做任何错误测试 | 🔴 高 | 整个 pipeline 从未真正跑通过，未知问题多 |
| Whisper 依赖重 | 🟡 中 | torch + whisper 安装慢，首次体验差 |
| 截帧质量靠运气 | 🟡 中 | 均匀截帧不够智能，常截到无意义帧 |
| 图片路径硬编码 | 🟡 中 | 菜谱 MD 里帧路径是固定的 frame_01~12，与实际截帧结果可能不符 |
| publish.py 侧边栏更新脆弱 | 🟡 中 | 依赖字符串替换，多次执行容易出问题 |
| 无 GitHub Actions 配置 | 🟡 中 | 自动部署逻辑写在 recipe.py 里但没有 .yml |
| 无 OpenAI Whisper API 备选 | 🟢 低 | 本地 Whisper 失败时没有回退 |
| 无 Web UI | 🟢 低 | 目前纯 CLI |

---

## 目标

**核心目标：把 B站视频 URL → 高质量图文菜谱的流程跑通，并部署到 GitHub Pages。**

---

## 阶段规划

### Phase 1：跑通 Pipeline（当前优先）

1. **真实测试** 用案例视频 `BV15QPCzGEMy` 完整走一遍
2. **修复发现的 bug**
3. 验证生成的菜谱质量

**关键子任务：**
- [x] 检查环境依赖（yt-dlp / ffmpeg / whisper / openai）
- [x] 运行 extract.py 测试下载和字幕提取 ✅
- [x] 运行 transcribe.py 测试转录（B站字幕直接用）✅
- [x] 运行 frames.py 测试截帧 ✅
- [x] 运行 generate.py 测试 Claude 生成（切换至 wanqing OpenAI 兼容 API）✅
- [ ] 修复帧路径问题：generate 时应根据实际 frames 列表动态插入图片
- [x] 运行 publish.py 测试发布 ✅

🎯 **Phase 1 全流程已跑通（2026-03-11）** 案例视频：BV15QPCzGEMy 蛋炒饭

### Phase 2：质量提升

1. **智能截帧**：利用 Whisper segments 时间戳，让 Claude 在生成菜谱步骤时指定对应帧的时间点，再截图，而不是事先盲截
2. **更好的 Prompt**：
   - 让 Claude 输出 JSON 结构（而非直接 Markdown），再渲染，更可靠
   - 加入 few-shot 示例，提升菜谱质量
   - 支持视频描述区的食材清单辅助提取
3. **帧与步骤对齐**：每个烹饪步骤精准对应截图
4. **更好的错误处理**：网络失败重试、API 失败降级

### Phase 3：部署 & 体验

1. **GitHub Actions**：push 后自动 `vitepress build` + 部署到 GitHub Pages
2. **VitePress 主题优化**：首页菜谱卡片式展示（缩略图 + 标题 + 标签）
3. **菜谱 frontmatter 完善**：让 VitePress 能搜索/过滤
4. **（可选）Web 表单**：输入 URL 直接触发 pipeline

### Phase 4：扩展（远期）

- 支持更多来源（YouTube、抖音、小红书）
- 批量导入（一次处理收藏夹）
- 菜谱评分 & 用户反馈

---

## 技术架构

```
输入: B站视频 URL
    ↓
[extract] yt-dlp → 音频/视频/字幕 → meta.json
    ↓
[transcribe] B站字幕 or Whisper → transcript.txt + segments.json
    ↓
[frames] ffmpeg 按时间戳截帧 → frames/frame_XX.jpg
    ↓
[generate] Claude API (转录 + 视频描述) → recipe.md
    ↓
[publish] 复制到 VitePress docs → 更新侧边栏 → git push → GitHub Pages
```

---

## 当前最高优先级

🎯 **Phase 1 第一步：用 `BV15QPCzGEMy` 跑通全流程，边跑边修**
