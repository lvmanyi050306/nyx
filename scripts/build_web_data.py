#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""兼容入口：构建 Nyx Web 展示数据。"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "Nyx_Web_Visualization" / "scripts" / "build_web_data.py"
    runpy.run_path(str(target), run_name="__main__")
