#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""兼容入口：转发到 Nyx_Web_Visualization/scripts/preprocess_for_web.py。"""

from pathlib import Path
import runpy


if __name__ == "__main__":
    target = Path(__file__).resolve().parents[1] / "Nyx_Web_Visualization" / "scripts" / "preprocess_for_web.py"
    runpy.run_path(str(target), run_name="__main__")
