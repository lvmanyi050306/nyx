#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Nyx Web Demo 一键启动器。

比 .bat 更稳定：负责检查 Web 数据、必要时预处理、寻找可用端口、
启动本地 HTTP 服务器并自动打开浏览器。
"""

from __future__ import annotations

import http.server
import socket
import socketserver
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def find_free_port(start: int = 8000, end: int = 8010) -> int:
    """寻找一个可用端口。"""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
            except OSError:
                continue
            return port
    raise RuntimeError(f"端口 {start}-{end} 都被占用。")


def run_preprocess(root: Path) -> None:
    """运行 Web 数据预处理。"""
    script = root / "Nyx_Web_Visualization" / "scripts" / "preprocess_for_web.py"
    if not script.exists():
        raise FileNotFoundError(f"未找到预处理脚本：{script}")
    cmd = [
        sys.executable,
        str(script),
        "--input",
        "data/raw",
        "--output",
        "Nyx_Web_Visualization/web/assets/data",
        "--size",
        "64",
    ]
    print("[INFO] 开始生成 Web 数据，这一步可能需要 1 分钟左右。")
    print("[CMD] " + " ".join(cmd))
    subprocess.run(cmd, cwd=str(root), check=True)


def main() -> int:
    """启动入口。"""
    root = Path(__file__).resolve().parent
    web_dir = root / "Nyx_Web_Visualization" / "web"
    data_dir = web_dir / "assets" / "data"
    metadata = data_dir / "metadata.json"
    first_volume = data_dir / "volumes" / "vol_0000.bin"
    log_file = root / "Nyx_Web_Visualization" / "web_demo_startup.log"

    print("=" * 68)
    print("Nyx Density Explorer Web Demo")
    print("=" * 68)
    print(f"Project Root : {root}")
    print(f"Web Folder   : {web_dir}")
    print(f"Python       : {sys.executable}")
    print("=" * 68)

    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.write_text(
        f"Nyx Web Demo startup\nRoot: {root}\nPython: {sys.executable}\n",
        encoding="utf-8",
    )

    if not (web_dir / "index.html").exists():
        raise FileNotFoundError(f"未找到 Web 页面：{web_dir / 'index.html'}")

    if not metadata.exists() or not first_volume.exists():
        print("[WARN] 未检测到完整 Web 数据。")
        run_preprocess(root)
    else:
        print("[INFO] Web 数据已存在，跳过预处理。")

    port = find_free_port(8000, 8010)
    url = f"http://localhost:{port}"
    print(f"[INFO] 启动本地服务器：{url}")
    print("[INFO] 浏览器即将打开。如果没有自动打开，请手动复制上面的地址。")
    print("[INFO] 停止服务器：在此窗口按 Ctrl+C。")
    print("=" * 68)

    # 等服务器进入监听后再打开浏览器，避免浏览器太快访问失败。
    def delayed_open() -> None:
        time.sleep(1.0)
        webbrowser.open(url)

    import threading

    threading.Thread(target=delayed_open, daemon=True).start()

    handler = http.server.SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", port), handler) as httpd:
        # 只服务 Web 目录，不暴露项目根目录。
        import os

        os.chdir(web_dir)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[INFO] 服务器已停止。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("\n[ERROR] 启动失败：", exc)
        print("请把这段错误信息发给我，我可以继续定位。")
        input("按 Enter 退出...")
        raise
