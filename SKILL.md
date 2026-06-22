---
name: video-factory
description: 生成真人口播短视频（海外英文，投 TikTok / YouTube Shorts / Reels）。当用户要做口播短视频、批量短视频、数字人口播视频，或提到"视频工厂""做条短视频"时使用。这是瘦客户端——所有执行在服务器，本 skill 只验证 key 并提交任务、取回成片。
---

# Video Factory（瘦客户端）

通过 h2-bottle 视频工厂生成真人口播短视频。**所有执行（选题 / 脚本 / 内容审查 / 配音 / 数字人 A-roll / 对口型 / 字幕 / 合成）都在服务器完成**，本 skill 不含任何算法、源 key 或 pipeline 实现，只负责：验证你的 API key → 提交主题 → 取回成片。

## 前置：配置 API Key（一次性）

1. 找管理员要一个**子 key**（形如 `sk-xxx`），并确认已在后台给你开通「视频」权限。
2. 复制 `.env.example` 为 `.env`，填入你的 key：
   ```
   VF_API_KEY=sk-你的子key
   ```

## 工作流（给 Claude Code 的执行步骤）

当用户要生成视频时，**严格按顺序**：

1. **先验证 key（必做，验证不过不要继续）**：
   ```bash
   python scripts/vf.py verify
   ```
   - 成功 → 会列出可用人设（persona_id），继续下一步。
   - `401` → key 没配/无效，提示用户检查 `.env`。
   - `403` → key 没开视频权限，提示用户找管理员在 admin.html 打开「视频」开关。

2. **确认主题和人设**：问用户视频主题（`topic`，英文短句）和选哪个人设（`persona_id`，从 verify 输出里选；每个号有固定头像/音色，跨视频不变）。

3. **提交并等待出片**：
   ```bash
   python scripts/vf.py generate --topic "3 simple habits for better sleep" --persona sleep_sam --wait --out out.mp4
   ```
   生成约 3–7 分钟。完成后把 `out.mp4` 和在线地址交给用户。

## 命令参考

| 命令 | 说明 |
|------|------|
| `python scripts/vf.py verify` | 验证 key + 列出可用人设 |
| `python scripts/vf.py generate --topic "..." --persona <id> [--wait --out file.mp4]` | 提交生成任务 |
| `python scripts/vf.py status <task_id>` | 查任务状态 |
| `python scripts/vf.py download <task_id> --out file.mp4` | 下载成片 |

## 注意

- **内容合规审查在服务器侧执行**：违规脚本会被服务器拦下（任务返回 failed）。
- 人设固定：每个号的头像/音色/语气跨视频永不变（真人感信任的核心）。
- 纯 Python 标准库，**无需 pip install**。
- 服务器地址可用环境变量 `VF_BASE_URL` 覆盖（默认 `https://h2-bottle.com/v1/video`）。
