项目名称
========
基于体绘制与相空间刷选的 Nyx 宇宙密度演化可视分析

项目简介
========
本项目对应赛题 II：科学可视化挑战赛，围绕 Nyx 宇宙学模拟密度数据开展可视分析。项目完成了原始三维体数据读取、密度统计、直方图与 time-density heatmap、体绘制、高密度区域筛选、结构指标计算、相空间刷选和 Web 交互展示。

本项目用于课程设计和可视化作品展示。文中关于空洞、丝状结构和高密度节点的说明来自给定数据与可视化实验结果，不作为正式天体物理科学结论。

整理后的文件结构
================
```text
Nyx_Visualization_Project/
  data/
    raw/                  原始 Nyx .dat 数据
    processed/            统计指标、阈值、阶段划分等 CSV/MAT 结果

  code/
    main.m                MATLAB 主入口
    step1_*.m             数据读取与中心切片检查
    step2_*.m             全时间步密度统计
    step3_*.m             直方图与 time-density heatmap
    step4_*.m             体绘制关键帧
    step5_*.m             Top 1% 高密度筛选
    step6_*.m             结构指标分析
    step7_*.m             MATLAB 交互式仪表盘
    step8_*.m             density-gradient 相空间分析
    step9_*.m             Hessian 宇宙网结构分类
    step10_*.m            时间步相似性与阶段划分
    utils/                通用函数

  Nyx_Web_Visualization/
    scripts/              Web 数据预处理脚本
    web/                  Web 单页交互展示系统

  results/
    01_data_check/
    02_histograms/
    03_statistics/
    04_volume_render/
    05_high_density/
    06_structure_metrics/
    07_dashboard/
    08_density_gradient_phase_space/
    09_hessian_cosmic_web/
    10_time_similarity/
    frames/
    report_figures/

  report/
    技术报告.docx
    长摘要.docx
    Answer Sheet.docx

  video/
    演示视频2.mp4

  start_nyx_web_demo.bat
  start_nyx_web_demo.py
  README.txt
```

数据说明
========
原始数据位于 `data/raw/`，文件名通常为 `0000.dat` 到 `0099.dat`。每个 `.dat` 文件表示一个时间步，格式为 little-endian float32 二进制数组。程序会根据文件大小自动推断 `n×n×n` 网格规模，并按照 z 轴最快、y 轴其次、x 轴最慢的存储顺序恢复为 x-y-z 三维密度体。

`data/processed/` 保存分析过程产生的统计结果，例如：

- `density_stats.csv`：全时间步 mean、std、P99、P99/mean、P99-P01 等指标。
- `high_density_threshold.csv`：每个时间步的 P99 / P99.9 高密度阈值。
- `structure_metrics.csv`：空洞比例、致密比例、熵、Gini、tail amplification 等结构指标。
- `hessian_cosmic_web_fraction.csv`：Hessian 结构分类比例。
- `time_similarity_stage.csv`：时间步相似性与阶段划分结果。

MATLAB 分析运行方法
===================
推荐环境：

- Windows
- MATLAB
- 可选：Image Processing Toolbox，用于 P99 mask 连通域分析

运行步骤：

1. 将 Nyx `.dat` 文件放入 `data/raw/`。
2. 打开 MATLAB，并将当前目录切换到项目根目录。
3. 执行：

```matlab
run('code/main.m')
```

`main.m` 会自动添加 `code/` 和 `code/utils/` 到 MATLAB 路径，并依次运行基础分析和进阶分析模块。若某个进阶模块失败，基础结果仍会保留。

Web 交互展示运行方法
====================
推荐直接双击项目根目录下的：

```text
start_nyx_web_demo.bat
```

或在命令行运行：

```bash
python start_nyx_web_demo.py
```

启动器会检查 Web 数据是否存在。如果缺少 `metadata.json` 或 `vol_0000.bin`，会自动调用：

```bash
python Nyx_Web_Visualization/scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
```

然后启动本地 HTTP 服务并打开浏览器。Web 页面不建议直接双击 `index.html` 打开，应通过本地服务器访问。

主要结果目录
============
- `results/01_data_check/`：中心切片、文件大小一致性检查。
- `results/02_histograms/`：代表时间步直方图、直方图对比、time-density heatmap。
- `results/03_statistics/`：均值、标准差、百分位、偏度峰度等统计曲线。
- `results/04_volume_render/`：体绘制关键帧、传递函数对比图。
- `results/05_high_density/`：Top 1% 高密度 MIP、等值面和多阈值结果。
- `results/06_structure_metrics/`：结构指标曲线和首末时间步差异投影。
- `results/07_dashboard/`：MATLAB 交互仪表盘截图。
- `results/08_density_gradient_phase_space/`：density-gradient 相空间分析。
- `results/09_hessian_cosmic_web/`：Hessian 宇宙网分类结果。
- `results/10_time_similarity/`：时间步相似矩阵与阶段划分。
- `results/report_figures/`：报告中使用的汇总图片。
- `results/frames/`：用于生成演示视频的帧图。

报告与视频
==========
- 技术报告：`report/技术报告.docx`
- 长摘要：`report/长摘要.docx`
- 答案表：`report/Answer Sheet.docx`
- 演示视频：`video/演示视频2.mp4`
