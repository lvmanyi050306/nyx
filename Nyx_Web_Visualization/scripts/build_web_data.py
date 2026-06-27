#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Web 数据构建入口。

该脚本只是 `preprocess_for_web.py` 的轻量包装，便于按项目结构调用。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from preprocess_for_web import main


if __name__ == "__main__":
    main()
