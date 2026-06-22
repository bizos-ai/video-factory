#!/usr/bin/env python3
"""Video Factory — 瘦客户端 (thin client)。

执行层（选题 / 脚本 / 内容审查 / 配音 / 数字人 A-roll / 对口型 / 字幕 / 合成）
全部在服务器完成。本脚本不含任何算法、源 key 或 pipeline 实现，只做三件事：

  1. 用你的子 key 验证「是否有视频工厂访问权限」
  2. 提交一个生成任务（主题 + 人设）
  3. 轮询并取回成片

API key 经服务器的 token hub 校验；只有被管理员开通「视频」权限的子 key 才能用。
"""
import os
import sys
import time
import json
import argparse
import urllib.request
import urllib.error


def _load_env():
    """从 repo 根目录的 .env 读取配置（员工只需填 .env，无需 export）。"""
    here = os.path.dirname(os.path.abspath(__file__))
    envp = os.path.join(here, "..", ".env")
    if os.path.exists(envp):
        with open(envp, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


_load_env()

BASE = os.environ.get("VF_BASE_URL", "https://h2-bottle.com/v1/video").rstrip("/")


def _key():
    k = os.environ.get("VF_API_KEY", "").strip()
    if not k:
        sys.exit("❌ 未配置 VF_API_KEY。把管理员给你的子 key 填到 .env（见 .env.example）。")
    return k


def _req(method, path, body=None, timeout=30):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_key()}")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            ct = r.headers.get("Content-Type", "")
            return r.status, (json.loads(raw) if "json" in ct else raw)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw
    except urllib.error.URLError as e:
        sys.exit(f"❌ 连不上服务器 {BASE}：{e}")


def verify():
    """验证 key + 列出可用人设。验证不过会退出。"""
    code, body = _req("GET", "/health")
    if code == 200 and isinstance(body, dict) and body.get("ok"):
        ps = body.get("personas", [])
        print("✅ key 有效，已开通视频工厂。可用人设 (persona_id)：")
        for p in ps:
            print(f"   - {p}")
        return ps
    if code == 401:
        sys.exit("❌ 401：key 无效或未配置。检查 .env 里的 VF_API_KEY。")
    if code == 403:
        sys.exit("❌ 403：你的 key 还没开通视频权限。请管理员在 admin.html 给你打开「视频」开关。")
    sys.exit(f"❌ 验证失败 HTTP {code}: {body}")


def generate(topic, persona):
    code, body = _req("POST", "/generate", {"topic": topic, "persona_id": persona})
    if code == 401:
        sys.exit("❌ 401：key 无效。")
    if code == 403:
        sys.exit("❌ 403：没开通视频权限，找管理员。")
    if code != 200 or not isinstance(body, dict):
        sys.exit(f"❌ 提交失败 HTTP {code}: {body}")
    tid = body.get("task_id")
    print(f"✅ 已提交，task_id = {tid}")
    return tid


def status(tid):
    _, body = _req("GET", f"/status/{tid}")
    return body if isinstance(body, dict) else {"status": "unknown", "raw": str(body)}


def wait(tid, every=8, timeout=1800):
    print("⏳ 生成中（多段视频 + 对口型，约 3–7 分钟）…")
    t0 = time.time()
    last = ""
    while time.time() - t0 < timeout:
        b = status(tid)
        st = b.get("status", "")
        if st != last:
            print(f"   [{int(time.time() - t0)}s] {st}")
            last = st
        if st == "succeed":
            return b.get("video_url")
        if st == "failed":
            sys.exit(f"❌ 生成失败：{b.get('error')}")
        time.sleep(every)
    sys.exit("❌ 超时（任务可能仍在服务器跑，可稍后用 status <task_id> 查）。")


def download(tid, out):
    code, body = _req("GET", f"/file/{tid}", timeout=300)
    if code != 200:
        sys.exit(f"❌ 下载失败 HTTP {code}: {body}")
    with open(out, "wb") as f:
        f.write(body)
    print(f"✅ 已下载成片：{out}（{len(body)} bytes）")


def main():
    ap = argparse.ArgumentParser(description="Video Factory 瘦客户端")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("verify", help="验证 key 并列出可用人设")
    g = sub.add_parser("generate", help="提交一个生成任务")
    g.add_argument("--topic", required=True, help="视频主题（英文）")
    g.add_argument("--persona", default="nutrition_nadia", help="人设 id（用 verify 查看）")
    g.add_argument("--wait", action="store_true", help="阻塞等到出片")
    g.add_argument("--out", default="", help="出片后下载到此文件（需配合 --wait）")
    s = sub.add_parser("status", help="查任务状态")
    s.add_argument("task_id")
    d = sub.add_parser("download", help="下载成片")
    d.add_argument("task_id")
    d.add_argument("--out", default="video.mp4")
    a = ap.parse_args()

    if a.cmd == "verify":
        verify()
    elif a.cmd == "generate":
        tid = generate(a.topic, a.persona)
        if a.wait:
            url = wait(tid)
            if url:
                print(f"🎬 完成。在线地址（需带 key 访问）：{BASE}{url.replace('/v1/video', '')}")
            if a.out:
                download(tid, a.out)
        else:
            print(f"轮询：python scripts/vf.py status {tid}")
    elif a.cmd == "status":
        print(json.dumps(status(a.task_id), ensure_ascii=False, indent=2))
    elif a.cmd == "download":
        download(a.task_id, a.out)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
