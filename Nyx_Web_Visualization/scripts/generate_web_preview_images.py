#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""复制 Web 展示所需的报告图片。

正常情况下，`preprocess_for_web.py` 会自动复制这些图片；本脚本用于只刷新图片资产。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preprocess_for_web import copy_report_images, find_project_root


def main() -> None:
    project_root = find_project_root()
    web_root = project_root / "Nyx_Web_Visualization" / "web"
    copy_report_images(project_root, web_root)
    print("已刷新 Web 图片资产：", web_root / "assets" / "images")


if __name__ == "__main__":
    main()
