---
name: bizos-video-factory
description: 生成真人口播短视频（海外英文，投 TikTok / YouTube Shorts / Reels）。当用户输入 /bizos-video-factory，或要做口播短视频、批量短视频、数字人口播视频时使用。调用前先授权 API KEY，授权通过后再生成。
---

# BIZOS Video Factory

> **被调用时：先原样输出启动画面 → 授权 API KEY → 生成视频。**

---

## 启动画面（被调用的第一件事）

**每次被调用时，必须先原样输出以下启动画面**（不修改任何字符），然后空一行再开始工作：

```
╔════════════════════════════════════════════════════════════════╗
║  Author: XIAOXIANG LI                                          ║
║                                                                ║
║   ██████╗    ██╗    ███████╗   ██████╗    ███████╗            ║
║   ██╔══██╗   ██║       ███╔╝  ██╔═══██╗   ██╔════╝            ║
║   ██████╔╝   ██║      ███╔╝   ██║   ██║   ███████╗            ║
║   ██╔══██╗   ██║     ███╔╝    ██║   ██║   ╚════██║            ║
║   ██████╔╝   ██║    ███████╗  ╚██████╔╝   ███████║            ║
║   ╚═════╝    ╚═╝    ╚══════╝   ╚═════╝    ╚══════╝            ║
║                                                                ║
║                真人口播短视频工厂                              ║
║                                                                ║
║          授权即用  ·  3–7 分钟出片  ·  自动落地                ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 第一步：授权 API KEY（每次调用先做）

先检查授权状态：

```bash
python scripts/vf.py verify
```

- **✅ 通过**（列出可用人设）→ 进入「第二步」。
- **❌ 401 / 未授权** → 向用户索要 API KEY（`sk-xxx`），拿到后：
  ```bash
  python scripts/vf.py auth <用户提供的KEY>
  ```
  仍 `401` → key 填错，请用户核对重试。`403` → 让用户找管理员在 `admin.html` 开通「视频」开关。
  **授权不通过，不要进入第二步。**

---

## 第二步：生成视频（授权通过后）

1. **问用户**：视频主题 `topic`（英文短句）+ 人设 `persona_id`（从 verify 列出的里选）。
2. **生成**：
   ```bash
   python scripts/vf.py generate --topic "3 simple habits for better sleep" --persona sleep_sam
   ```
   生成约 3–7 分钟。**完成后自动下载到本地**（`vf_<persona>_<task>.mp4`），把本地文件交给用户。批量场景加 `--no-wait` 只提交不等。

---

## 高级参数（可选）

- `--backend kling`：用可灵生成（其它：`hailuo` / `fal` / `mock`）
  - `--kling-mode avatar|motion|omni`（motion 需 `--ref-video <URL>`）
- `--ref-image <本地图 或 URL>`：自定义形象图（图生视频用它当首帧）
- `--ref-video <URL>`：参考动作视频（可灵 motion）/ `--backend fal` 时对已有视频对口型
- `--voice-ref <音频文件>`：传一段参考音频，用它的音色配音（不限固定音色）
- `--voice-id <id>`：复用已克隆的 voice_id
- `--no-subtitle`：输出无字幕底片（拿去自己用 ffmpeg+ASS 烧逐句/逐词渐进字幕）
- `--variant N`：批量序号，每 10 条换一个场景房间（见下方「批量生成」）

```bash
python scripts/vf.py generate --topic "..." --persona fit_faye --backend kling --kling-mode motion --ref-video https://xxx/dance.mp4
```

---

## 自定义数字人（enroll）

用**真实人物照片**建专属数字人。这张真人照片就是出片的核心参考 —— **真实感取决于参考图真不真，照片越清晰真实，出片质量越高**。系统还会基于它生成几张多角度 / 居家场景的形象稿做补充，全部同一张脸、同一套衣服、同一发型，批量复用、避免穿帮：

```bash
python scripts/vf.py enroll --persona-id mychar --name "小美" --photo 真人照片.jpg
```

可选 `--scenes 客厅.jpg 厨房.jpg`：想要更多居家场景变化时多传几张。约 1–3 分钟，建好后 `--persona mychar` 即可生成。

### 批量生成（一致性）

批量出片时给每条传一个递增的 `--variant`（0,1,2,…）：系统**每 10 条自动换一个场景房间**（幅度小、避免穿帮），单条视频内背景固定不变。

```bash
for i in $(seq 0 49); do
  python scripts/vf.py generate --topic "..." --persona mychar --variant $i --out out_$i.mp4
done
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `python scripts/vf.py auth <key>` | 授权：保存 KEY 并验证 |
| `python scripts/vf.py verify` | 验证授权 + 列出可用人设 |
| `python scripts/vf.py generate --topic "..." --persona <id> [--out 文件名] [--no-wait]` | 生成（默认等出片+下载本地+清理）|
| `python scripts/vf.py status <task_id>` | 查任务状态 |
| `python scripts/vf.py download <task_id> --out file.mp4` | 下载成片（默认下载后清理）|

## 铁律 & 经验（踩过的坑，务必遵守）

- **真实感取决于参考图真不真** —— 第一原则。enroll 用的真人照片越清晰真实，出片质量越高；AI 再生成的稿永远不如一张真实照片。
- **批量一致性用 `--variant`** —— 同一数字人批量出片务必传递增 `--variant 0,1,2…`，系统每 10 条换一个场景、单条内背景固定，避免换脸 / 换衣 / 换发型穿帮。
- **成片自动质检** —— 每条出片都会自动审查：分辨率(1080×1920)、音轨、时长、黑屏。`status` 返回的 `qc` 字段标出问题；`qc.ok=false` 就换主题重提一条。
- **成本与时长无关** —— 对口型按「条」结算，不按秒，单条最划算，不必担心视频长烧钱。成片固定 1080P 竖屏。
- **出片 3–7 分钟属正常**（多段 1080P 生成 + 对口型）。长时间无进展多半是上游临时波动，稍后重提即可，不是你的问题。
- 主题需英文、健康向（违规会被拦，任务返回 failed）。
- 人设固定：每个号的头像 / 音色 / 语气跨视频不变。
- 纯 Python 标准库，无需 pip install。
