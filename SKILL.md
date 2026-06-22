---
name: bizos-video-factory
description: 生成真人口播短视频（海外英文，投 TikTok / YouTube Shorts / Reels）。当用户输入 /bizos-video-factory，或要做口播短视频、批量短视频、数字人口播视频时使用。这是瘦客户端——所有执行在服务器；调用时先做 API KEY 授权，授权通过后再进入视频制作流程。
---

# BIZOS Video Factory（瘦客户端）

通过 h2-bottle 视频工厂生成真人口播短视频。**所有执行（选题 / 脚本 / 内容审查 / 配音 / 数字人 A-roll / 对口型 / 字幕 / 合成）都在服务器完成**，本 skill 不含任何算法、源 key 或 pipeline 实现。

> **被调用时严格分两步：先授权 API KEY，授权通过后才进入视频制作。**

---

## 第一步：授权 API KEY（每次调用先做）

先检查当前授权状态：

```bash
python scripts/vf.py verify
```

根据结果：

- **✅ 验证通过**（200，列出可用人设）→ 已授权，直接进入「第二步：视频制作」。
- **❌ 未授权 / 401**（还没填 key 或 key 无效）→ **向用户索要 API KEY**：
  > 「请提供你的视频工厂 API KEY（管理员发放的 `sk-xxx`）：」
  
  拿到 key 后保存并验证（一步到位）：
  ```bash
  python scripts/vf.py auth <用户提供的KEY>
  ```
  - 成功 → 进入「第二步」。
  - 仍 `401` → key 填错了，请用户核对后重新 `auth`。
  - `403` → key 有效但**没开通视频权限**，让用户找管理员在 `admin.html` 给这个 key 打开「视频」开关，开通后再来。
  
  **授权不通过，不要进入第二步。**

---

## 第二步：视频制作流程（授权通过后）

1. **问用户两件事**：
   - 视频主题 `topic`（英文短句，如 `3 simple habits for better sleep`）
   - 选哪个人设 `persona_id`（从 verify 列出的里选；每个号有固定头像/音色，跨视频不变）
2. **提交并等待出片**：
   ```bash
   python scripts/vf.py generate --topic "..." --persona <persona_id> --wait --out out.mp4
   ```
   生成约 3–7 分钟。完成后把 `out.mp4` 和在线地址交给用户。

---

## 命令参考

| 命令 | 说明 |
|------|------|
| `python scripts/vf.py auth <key>` | 首次授权：保存 KEY 到 .env 并验证 |
| `python scripts/vf.py verify` | 验证授权 + 列出可用人设 |
| `python scripts/vf.py generate --topic "..." --persona <id> [--wait --out file.mp4]` | 提交生成任务 |
| `python scripts/vf.py status <task_id>` | 查任务状态 |
| `python scripts/vf.py download <task_id> --out file.mp4` | 下载成片 |

## 注意

- **内容合规审查在服务器侧执行**：违规脚本会被服务器拦下（任务返回 failed）。
- 人设固定：每个号的头像/音色/语气跨视频永不变（真人感信任的核心）。
- 纯 Python 标准库，**无需 pip install**。
- 服务器地址可用环境变量 `VF_BASE_URL` 覆盖（默认 `https://h2-bottle.com/v1/video`）。
