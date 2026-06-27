# Nyx_Web_Visualization

这是《基于体绘制与相空间刷选的 Nyx 宇宙密度演化可视分析》的 Web 交互展示子项目。它将原 MATLAB / Python 项目中生成的 Nyx 密度数据、统计结果和报告图像整理为一个可用于课程展示和答辩演示的 HTML 单页系统。

## 文件结构

```text
Nyx_Web_Visualization/
├─ web/
│  ├─ index.html
│  ├─ style.css
│  ├─ app.js
│  ├─ README_WEB.md
│  └─ assets/
│     ├─ data/
│     │  ├─ metadata.json
│     │  ├─ density_stats.json
│     │  ├─ histograms.json
│     │  ├─ time_density_heatmap.json
│     │  ├─ hessian_fraction.json
│     │  ├─ time_similarity_stage.json
│     │  └─ volumes/
│     │     ├─ vol_0000.bin
│     │     ├─ vol_0001.bin
│     │     └─ ...
│     └─ images/
│        ├─ iteration_roadmap.png
│        ├─ overall_workflow.png
│        ├─ nyx_keyword_wordcloud.png
│        └─ ...
└─ scripts/
   ├─ preprocess_for_web.py
   ├─ generate_web_preview_images.py
   └─ build_web_data.py
```

根目录 `scripts/` 也提供了同名兼容入口，便于从原项目根目录直接运行。

## 快速运行

在原项目根目录运行：

```bash
python scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
cd Nyx_Web_Visualization/web
python -m http.server 8000
```

浏览器打开：

```text
http://localhost:8000
```

## 主要功能

- 时间步滑条和播放按钮：展示 Nyx 密度场随时间演化。
- 密度百分位刷选：默认 `99% - 100%`，即 top 1% 高密度体素。
- 空间视图：支持 MIP、Mask、Masked MIP、Slice 和简化 Volume Composite。
- 方向切换：支持 X/Y/Z 三个投影方向。
- 传递函数切换：支持 Balanced、Void、Filament 和 Node。
- 直方图联动：拖拽 histogram 可以改变密度刷选范围。
- time-density heatmap：点击热力图可跳转到对应时间步。
- 指标曲线：展示 mean、std、P99、P99/mean 和 P99-P01。
- 项目概览：展示实验迭代路线图、关键词词云和方法亮点图。

## 数据策略

网页端不直接加载原始完整体数据，而是通过 `preprocess_for_web.py` 生成降采样后的 normalized log-density 体：

- 默认大小：`64×64×64`
- 数据类型：`float32`
- 加载方式：按当前时间步懒加载
- 缓存方式：浏览器内存缓存已访问时间步

这样可以避免一次性加载 `128×128×128×100` 的完整体数据导致浏览器卡顿。

## 注意事项

1. 如果没有 `.dat` 原始数据，预处理脚本无法生成体数据，但页面结构仍可打开。
2. 如果 `data/processed/density_stats.csv` 存在，脚本会优先读取已有统计结果。
3. 如果缺少 Hessian 或时间阶段 CSV，脚本会自动降级生成基础阶段信息。
4. 本项目用于数据可视化课程展示，不作为正式天体物理科学结论。
