# Video Factory — 瘦客户端

真人口播短视频工厂的**员工端瘦客户端**。海外英文，投 TikTok / YouTube Shorts / Reels。

> **执行层全部在服务器**。本仓库只是一个壳：验证你的 API key → 提交主题 → 取回成片。
> 这里**不包含**任何算法、选题/脚本/审查/对口型逻辑、源 key 或 pipeline 实现——那些都在服务器上，对外保密。

## 它能做什么

用一行命令（或在 Claude Code 里用自然语言）生成一条带数字人口播 + 字幕的竖屏（1080×1920）短视频：

```bash
python scripts/vf.py generate --topic "3 simple habits for better sleep" --persona sleep_sam --wait --out out.mp4
```

## 安装

```bash
git clone https://github.com/<your-org>/video-factory.git
cd video-factory
cp .env.example .env
# 编辑 .env，填入管理员给你的子 key
```

无需 `pip install`（纯 Python 3 标准库）。

### 作为 Claude Code Skill 用

把本仓库放到 Claude Code 的 skills 目录即可（例如 `~/.claude/skills/video-factory/`），
然后在 Claude Code 里直接说「做一条睡眠主题的短视频」，它会自动验证 key 并提交任务。详见 [SKILL.md](SKILL.md)。

## 配置

`.env`：

```
VF_API_KEY=sk-你的子key          # 管理员发放、且已开通「视频」权限
# VF_BASE_URL=https://h2-bottle.com/v1/video   # 可选，默认即此
```

## 用法

```bash
# 1. 验证 key（会列出可用人设）
python scripts/vf.py verify

# 2. 生成（--wait 阻塞到出片，--out 下载成片）
python scripts/vf.py generate --topic "..." --persona nutrition_nadia --wait --out out.mp4

# 或者异步：拿到 task_id 后自己轮询
python scripts/vf.py generate --topic "..." --persona sleep_sam
python scripts/vf.py status <task_id>
python scripts/vf.py download <task_id> --out out.mp4
```

## 拿不到权限？

| 现象 | 原因 | 解决 |
|------|------|------|
| `401` | key 没配 / 无效 | 检查 `.env` 的 `VF_API_KEY` |
| `403` | key 有效但没开视频权限 | 找管理员在后台给你的 key 打开「视频」开关 |

## 可用人设

运行 `python scripts/vf.py verify` 获取实时列表。每个号有固定头像 / 音色，跨视频不变。

## 安全边界

- 你的子 key 只能调用视频工厂的提交/查询接口，**拿不到任何源 key**（脚本/配音/视频生成的上游密钥全锁在服务器）。
- 服务器对每个 key 校验权限；只有被开通「视频」的 key 才能用。
- 内容在服务器侧过合规审查，违规任务会被拒。
