# BIZOS Video Factory

内部工具。

## 安装

```bash
git clone https://github.com/bizos-ai/video-factory.git ~/.claude/skills/bizos-video-factory
```

无需 `pip install`（纯 Python 3 标准库）。

## 用法

```bash
# 1. 授权（首次，管理员发的 sk-xxx）
python scripts/vf.py auth sk-你的key

# 2. 生成（默认等出片 + 自动下载到本地）
python scripts/vf.py generate --topic "3 simple habits for better sleep" --persona sleep_sam

# 其它
python scripts/vf.py verify                       # 验证 + 列可用人设
python scripts/vf.py status <task_id>
python scripts/vf.py download <task_id> --out out.mp4
```

## 命令 / 参数

| 命令 | 说明 |
|------|------|
| `auth <key>` | 授权：保存 KEY 并验证 |
| `verify` | 验证 + 列出可用人设 |
| `generate --topic "..." --persona <id> [选项]` | 生成 |
| `status <task_id>` | 查状态 |
| `download <task_id> --out file.mp4` | 下载 |

generate 选项：

| 参数 | 说明 |
|------|------|
| `--out <文件名>` | 下载文件名（默认 `vf_<persona>_<task>.mp4`）|
| `--no-wait` | 只提交不等不下载（批量）|
| `--keep-remote` | 保留远端副本（默认下载后清理）|
| `--backend hailuo\|fal\|kling\|mock` | 后端 |
| `--kling-mode avatar\|motion\|omni` | 可灵模式 |
| `--ref-image <本地图/URL>` | 自定义形象图 |
| `--ref-video <URL>` | 参考视频 |
| `--voice-ref <音频>` / `--voice-id <id>` | 自定义音色 |

## 授权失败

| 现象 | 解决 |
|------|------|
| `401` | 重新 `auth <key>` |
| `403` | 找管理员在 `admin.html` 开通「视频」开关 |
