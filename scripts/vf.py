#!/usr/bin/env python3
"""Video Factory CLI.

  auth      授权:保存 API KEY 并验证
  verify    验证 key + 列出可用人设
  generate  生成视频(主题 + 人设)
  status    查任务状态
  download  下载成片
"""
import os
import sys
import time
import json
import argparse
import urllib.request
import urllib.error


def _env_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", ".env")


def _load_env():
    """从 repo 根目录的 .env 读取配置（员工只需填 .env，无需 export）。"""
    envp = _env_path()
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
        sys.exit("❌ 未授权。先运行：python scripts/vf.py auth <你的API_KEY>")
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


def save_key(key):
    """把 API KEY 写入 repo 根的 .env，然后立即验证。供首次授权用。"""
    key = (key or "").strip()
    if not key:
        sys.exit("❌ 请提供 API KEY：python scripts/vf.py auth <你的API_KEY>")
    envp = _env_path()
    lines, found = [], False
    if os.path.exists(envp):
        with open(envp, encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("VF_API_KEY="):
                    lines.append(f"VF_API_KEY={key}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"VF_API_KEY={key}\n")
    with open(envp, "w", encoding="utf-8") as f:
        f.writelines(lines)
    os.environ["VF_API_KEY"] = key  # 当前进程立即生效
    print(f"🔑 已保存 API KEY 到 {os.path.abspath(envp)}")
    print("正在验证授权…")
    verify()


def verify():
    """验证 key + 列出可用人设。验证不过会退出（非 0）。"""
    code, body = _req("GET", "/health")
    if code == 200 and isinstance(body, dict) and body.get("ok"):
        ps = body.get("personas", [])
        print("✅ 授权成功。可用人设 (persona_id)：")
        for p in ps:
            print(f"   - {p}")
        return ps
    if code == 401:
        sys.exit("❌ 401：未授权或 key 无效。运行 auth 重新授权：python scripts/vf.py auth <key>")
    if code == 403:
        sys.exit("❌ 403：key 有效但还没开通视频权限。请管理员在 admin.html 给你打开「视频」开关。")
    sys.exit(f"❌ 验证失败 HTTP {code}: {body}")


def generate(topic, persona, opts=None):
    payload = {"topic": topic, "persona_id": persona}
    payload.update({k: v for k, v in (opts or {}).items() if v is not None})
    code, body = _req("POST", "/generate", payload)
    if code == 401:
        sys.exit("❌ 401：未授权。先运行：python scripts/vf.py auth <key>")
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
    print(f"✅ 已下载成片到本地：{out}（{len(body)} bytes）")


def delete_remote(tid):
    """下载到本地后删服务器的成片+中间产物(结果不停留服务器)。"""
    code, body = _req("DELETE", f"/file/{tid}")
    if code == 200:
        n = body.get("deleted", "?") if isinstance(body, dict) else "?"
        print(f"🧹 已清理服务器(task {tid[:8]}，删 {n} 个文件)")
    else:
        print(f"⚠️ 服务器清理未成功 HTTP {code}（成片已在本地，不影响）")


def main():
    ap = argparse.ArgumentParser(description="BIZOS Video Factory")
    sub = ap.add_subparsers(dest="cmd")
    au = sub.add_parser("auth", help="首次授权：保存 API KEY 到 .env 并验证")
    au.add_argument("key", help="管理员发放的 API KEY（sk-xxx）")
    sub.add_parser("verify", help="验证 key 并列出可用人设")
    g = sub.add_parser("generate", help="提交一个生成任务")
    g.add_argument("--topic", required=True, help="视频主题（英文）")
    g.add_argument("--persona", default="nutrition_nadia", help="人设 id（用 verify 查看）")
    g.add_argument("--backend", default=None, help="输出模型: hailuo / fal / kling / mock（默认服务器设定）")
    g.add_argument("--kling-mode", default="avatar", help="可灵模式: avatar(对口型) / motion(动作控制) / omni(多模态)")
    g.add_argument("--ref-image", default=None, help="自定义形象图：本地图片路径 或 URL（海螺/可灵图生视频用它当首帧，解锁金发等自定义形象）")
    g.add_argument("--ref-video", default=None, help="参考动作视频 URL（可灵 motion 用）")
    g.add_argument("--orient", default="image", help="motion 朝向: image / video")
    g.add_argument("--duration", default="5", help="omni 时长(秒)")
    g.add_argument("--prompt", default=None, help="追加 / 覆盖生成 prompt")
    g.add_argument("--voice-ref", default=None, help="参考音色音频文件(本地路径，克隆该音色来配音)")
    g.add_argument("--voice-id", default=None, help="复用已克隆的 voice_id")
    g.add_argument("--voice-engine", default="elevenlabs", help="克隆引擎: elevenlabs / minimax")
    g.add_argument("--qc-retry", type=int, default=2, help="每段视频质检不过最多重生成次数(0=关质检)")
    g.add_argument("--out", default="", help="下载文件名(默认 vf_<persona>_<task>.mp4)")
    g.add_argument("--no-wait", action="store_true", help="异步:只提交、不等待、不下载(批量场景)")
    g.add_argument("--keep-remote", action="store_true", help="保留服务器成片(默认下载到本地后删，不停留服务器)")
    s = sub.add_parser("status", help="查任务状态")
    s.add_argument("task_id")
    d = sub.add_parser("download", help="下载成片(默认下载后删服务器)")
    d.add_argument("task_id")
    d.add_argument("--out", default="video.mp4")
    d.add_argument("--keep-remote", action="store_true", help="保留服务器成片")
    a = ap.parse_args()

    if a.cmd == "auth":
        save_key(a.key)
    elif a.cmd == "verify":
        verify()
    elif a.cmd == "generate":
        voice_ref_b64 = None
        if a.voice_ref:
            import base64
            with open(a.voice_ref, "rb") as vf:
                voice_ref_b64 = "data:audio/mpeg;base64," + base64.b64encode(vf.read()).decode()
        ref_image_url, ref_image_b64 = None, None
        if a.ref_image:
            if os.path.exists(a.ref_image):
                import base64
                with open(a.ref_image, "rb") as imf:
                    ref_image_b64 = "data:image/png;base64," + base64.b64encode(imf.read()).decode()
            else:
                ref_image_url = a.ref_image
        opts = {
            "aroll_backend": a.backend,
            "kling_mode": a.kling_mode,
            "reference_image_url": ref_image_url,
            "reference_image_b64": ref_image_b64,
            "reference_video_url": a.ref_video,
            "character_orientation": a.orient,
            "duration": a.duration,
            "extra_prompt": a.prompt,
            "voice_ref_b64": voice_ref_b64,
            "voice_id": a.voice_id,
            "voice_engine": a.voice_engine,
            "qc_retry": a.qc_retry,
        }
        tid = generate(a.topic, a.persona, opts)
        if a.no_wait:
            print(f"已提交(异步)。轮询: python scripts/vf.py status {tid}")
        else:
            wait(tid)
            out = a.out or f"vf_{a.persona}_{tid[:8]}.mp4"
            download(tid, out)
            if not a.keep_remote:
                delete_remote(tid)
    elif a.cmd == "status":
        print(json.dumps(status(a.task_id), ensure_ascii=False, indent=2))
    elif a.cmd == "download":
        download(a.task_id, a.out)
        if not a.keep_remote:
            delete_remote(a.task_id)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
