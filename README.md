# BIZOS Video Factory — 瘦客户端

真人口播短视频工厂的**员工端瘦客户端**（Claude Code Skill）。海外英文，投 TikTok / YouTube Shorts / Reels。

> **执行层全部在服务器**。本仓库只是一个壳：授权你的 API key → 提交主题 → 取回成片。
> 这里**不包含**任何算法、选题/脚本/审查/对口型逻辑、源 key 或 pipeline 实现——那些都在服务器上，对外保密。

## 在 Claude Code 里用（推荐）

把本仓库放到 Claude Code 的 skills 目录（例如 `~/.claude/skills/bizos-video-factory/`），然后：

```
/bizos-video-factory
```

调用后流程固定两步：

1. **授权 API KEY** —— skill 先验证授权；没授权会让你贴上管理员发的 `sk-xxx`，自动保存并验证。
2. **视频制作** —— 授权通过后，告诉它主题和人设，约 3–7 分钟出片。

## 安装

```bash
git clone https://github.com/bizos-ai/video-factory.git ~/.claude/skills/bizos-video-factory
```

无需 `pip install`（纯 Python 3 标准库），也无需手动建 `.env`——首次 `auth` 会自动写入。

## 命令行直接用

```bash
cd ~/.claude/skills/bizos-video-factory

# 1. 首次授权（保存 KEY 并验证，会列出可用人设）
python scripts/vf.py auth sk-你的子key

# 2. 生成（--wait 阻塞到出片，--out 下载成片）
python scripts/vf.py generate --topic "3 simple habits for better sleep" --persona sleep_sam --wait --out out.mp4

# 其它
python scripts/vf.py verify                       # 重新验证授权 + 看人设
python scripts/vf.py status <task_id>
python scripts/vf.py download <task_id> --out out.mp4
```

## 授权失败怎么办

| 现象 | 原因 | 解决 |
|------|------|------|
| `401` | 没授权 / key 填错 | 重新 `python scripts/vf.py auth <key>` |
| `403` | key 有效但没开视频权限 | 找管理员在 `admin.html` 给你的 key 打开「视频」开关 |

## 可用人设

授权后 `python scripts/vf.py verify` 会列出实时人设。每个号有固定头像 / 音色，跨视频不变。

## 安全边界

- 你的子 key 只能调用视频工厂的提交/查询接口，**拿不到任何源 key**（脚本/配音/视频生成的上游密钥全锁在服务器）。
- 服务器对每个 key 校验权限；只有被开通「视频」的 key 才能用。
- 内容在服务器侧过合规审查，违规任务会被拒。
