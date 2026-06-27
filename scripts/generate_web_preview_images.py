#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""兼容入口：刷新 Nyx Web 展示图片资产。"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "Nyx_Web_Visualization" / "scripts" / "generate_web_preview_images.py"
    runpy.run_path(str(target), run_name="__main__")
