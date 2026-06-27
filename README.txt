项目名称
========
基于体绘制与相空间刷选的 Nyx 宇宙密度演化可视分析

项目性质
========
本项目为“数据可视化”课程大作业，数据来源于 ChinaVis 2026 赛题 II 科学可视化挑战赛中的 Nyx 宇宙学模拟密度数据。项目目标是围绕 Nyx 三维密度场完成数据读取、统计分析、体绘制、高密度区域筛选、结构指标计算和交互式相空间刷选分析。本文档与代码用于课程作业展示，不作为正式天体物理科学结论。

数据说明
========
原始数据放在 data/raw/ 目录下，文件名通常为：

0000.dat、0001.dat、0002.dat、...、0099.dat

每个 .dat 文件表示一个时间步。数据格式为 little-endian float32，每个文件内部是连续的一维数值序列，可自动推断为 n×n×n 的三维体数据，例如 128×128×128。原始线性存储顺序为 z 轴最快、y 轴其次、x 轴最慢，程序读取后会重排为 MATLAB 中更直观的 x-y-z 三维数组。

文件夹结构
==========
Nyx_Visualization_Project/
  data/
    raw/                  原始 .dat 文件
    processed/            CSV、MAT 统计结果
  code/
    main.m                一键运行主入口
    read_nyx_dat.m        Nyx 二进制数据读取
    infer_grid_size.m     自动推断立方体网格尺寸
    step1_check_data.m
    step2_statistics_all_frames.m
    step3_histogram_analysis.m
    step4_volume_render_keyframes.m
    step5_high_density_selection.m
    step6_structure_metrics.m
    step7_interactive_dashboard.m
    utils/                通用工具函数
  results/
    01_data_check/
    02_histograms/
    03_statistics/
    04_volume_render/
    05_high_density/
    06_structure_metrics/
    07_dashboard/
    frames/
  report/
    大作业技术报告草稿.md
    Answer_Sheet_简版.md
  report_assets/
  README.txt

运行环境
========
推荐环境：

- Windows
- MATLAB
- 可选：MATLAB Image Processing Toolbox，用于 P99 mask 连通域分析
- Python，可用于后续报告整理或辅助处理
- FFmpeg，可用于将帧图合成为视频

如果 Image Processing Toolbox 不可用，程序会跳过 bwconncomp 连通域分析，不影响主流程运行。

运行方法
========
1. 将 Nyx .dat 文件放入 data/raw/。
2. 打开 MATLAB。
3. 将当前目录切换到 Nyx_Visualization_Project 项目根目录。
4. 运行：

   run('code/main.m')

main.m 会自动添加 code/ 与 code/utils/ 到 MATLAB 路径，并依次运行：

- step1_check_data
- step2_statistics_all_frames
- step3_histogram_analysis
- step4_volume_render_keyframes
- step5_high_density_selection
- step6_structure_metrics

交互式仪表盘不会在 main.m 中默认阻塞启动。如需打开，请在 main.m 完成后运行：

   step7_interactive_dashboard(pwd)

主要输出
========
data/processed/density_stats.csv
  全时间步密度统计量，包括 mean、std、min、max、P01、P05、P50、P95、P99、P99.7、P99.9，以及 log-density 的均值、标准差、偏度、峰度。

data/processed/high_density_threshold.csv
  每个时间步的 P99 和 P99.9 高密度阈值，用于 top 1% 高密度区域筛选。

data/processed/structure_metrics.csv
  结构指标，包括 P99-P01 spread、P99/mean tail amplification、空洞比例、致密比例、log-density 熵、Gini 系数，以及可选连通域指标。

results/01_data_check/
  中心切片与文件尺寸一致性检查。

results/02_histograms/
  代表时间步直方图、叠加对比图、全时间步 log-density 热力图。

results/03_statistics/
  均值标准差曲线、最大密度曲线、百分位曲线、log-density 偏度峰度曲线。

results/04_volume_render/
  自定义 alpha compositing 体绘制结果、关键帧对比图、传递函数对比图。

results/05_high_density/
  P99 top 1% 高密度区域 MIP、P99 等值面、P90/P95/P99 嵌套等值面。

results/06_structure_metrics/
  结构指标曲线与首末时间步 log-density 差分 MIP。

results/07_dashboard/
  交互式联动刷选仪表盘默认截图 dashboard_preview.png。

results/frames/
  所有时间步的视频帧 frame_0000.png、frame_0001.png、...

方法简介
========
1. 原始数据读取
   read_nyx_dat.m 使用 fopen(filename, 'r', 'ieee-le') 与 fread(..., 'single=>single') 读取 little-endian float32 数据。程序自动推断 n，并按 [z,y,x] reshape 后 permute 为 [x,y,z]。

2. log10 变换
   对密度使用 log10(max(density, eps))，压缩动态范围，便于观察空洞、丝状结构与高密度节点。

3. 百分位归一化
   normalize_percentile.m 使用低、高百分位裁剪并归一化到 [0,1]。体绘制默认使用 log-density 的 P5 到 P99.7 范围。

4. 自定义体绘制
   volume_render_alpha_composite.m 沿 z 方向从后向前做 alpha compositing，不依赖 volshow。颜色查找表从深蓝/黑色过渡到紫色、橙色、黄色与白色。

5. 梯度增强
   体绘制中计算三维梯度幅值，并用于增强 alpha 和亮度，使密度边界、丝状结构和团块边缘更清晰。

6. 高密度 P99 筛选
   每个时间步使用原始 density 的 P99 作为 top 1% 高密度阈值。投影显示使用 log-density，以说明直方图右侧高密度尾部在空间中对应宇宙网节点和丝状交汇处。

7. 直方图热力图
   对全部时间步使用统一 bins 计算 log-density histogram，并堆叠为 time-density heatmap，用于展示分布迁移、扩散和高密度尾部增强。

8. 结构指标
   计算 spread_p99_p01、tail_amplification、void/dense fraction、log-density entropy、Gini 系数。如果 Image Processing Toolbox 可用，还会对 P99 mask 做 26 邻域连通域分析。

9. 交互式联动刷选
   step7_interactive_dashboard.m 提供时间步滑条、百分位区间滑条、投影方向选择和显示模式选择。左侧为 log-density histogram，右侧为空间投影视图；调节参数后实时更新所选体素比例。

视频合成命令
============
安装 FFmpeg 后，可在 results/frames/ 目录下运行：

ffmpeg -framerate 12 -i frame_%04d.png -c:v libx264 -pix_fmt yuv420p demo.mp4

报告文件
========
课程报告正文草稿见：

report/大作业技术报告草稿.md

Answer Sheet 简版见：

report/Answer_Sheet_简版.md


进阶可视分析模块
================

本项目在基础流程之后新增了 3 个进阶可视分析模块。它们会在 main.m 的基础步骤完成后以 try/catch 方式运行；如果高级模块失败，不会影响 step1 至 step6 已经生成的基础结果。

1. density-gradient 二维相空间分析
   对 normalized log-density 和 gradient magnitude 建立二维相空间热力图，用于区分空洞背景、丝状边界、节点边界和致密核心。该模块把一维密度直方图扩展为二维特征空间，适合作为二维传递函数和进阶 linked brushing 的基础。

   主要输出目录：
   results/08_density_gradient_phase_space/

   代表性输出：
   - density_gradient_phase_compare.png
   - phase_space_selection_t0099.png

2. Hessian 宇宙网结构分类
   基于 log-density 的 Hessian 特征值，将体素粗略分为 Void、Sheet、Filament 和 Node，用于补充体绘制中的结构观察。程序会先对 log-density 做平滑，并在体数据较大时自动降采样，以降低计算量。

   主要输出目录：
   results/09_hessian_cosmic_web/

   代表性输出：
   - hessian_class_slice_compare.png
   - hessian_class_fraction_curve.png
   - filament_node_mip_t0099.png
   - data/processed/hessian_cosmic_web_fraction.csv

3. 时间步相似性矩阵与阶段划分
   将每个时间步的 log-density histogram 看作概率向量，计算时间步之间的 cosine similarity，得到时间步相似性矩阵和距离矩阵，并基于 distance_from_start 将演化过程粗略划分为 Early、Transition、Structure enhancement 和 Late 四个阶段。

   主要输出目录：
   results/10_time_similarity/

   代表性输出：
   - time_step_similarity_matrix.png
   - time_step_distance_matrix.png
   - adjacent_time_change_curve.png
   - evolution_stage_segmentation.png
   - data/processed/time_similarity_stage.csv

进阶模块注意事项
================

- Hessian 分类属于课程实验中的简化结构识别方法，不是严格天体物理分类结论。
- Hessian 结果依赖高斯平滑尺度、降采样尺度和特征值阈值 tau，不同参数会影响 Void、Sheet、Filament 和 Node 的占比。
- 如果 Hessian 计算较慢，可以在 step9_hessian_cosmic_web_classification.m 中降低 downsample_volume 的 maxSize。
- 如果数据时间步不足 100 个，程序会基于 data/raw/ 中已有的非空 .dat 文件运行，并自动选择最接近的代表时间步。
- 新增核心图会复制到 results/report_figures/，方便插入 Word 技术报告和答辩 PPT。

Web 交互展示系统
================

本项目新增了一个 HTML 单页交互式展示作品，目录为：

Nyx_Web_Visualization/

该 Web 版本用于课程答辩和现场演示。它不会直接把完整 128×128×128×100 原始体数据全部加载进浏览器，而是通过 Python 预处理生成 64×64×64 的 normalized log-density 降采样体数据，并在浏览器端按当前时间步懒加载。

主要功能包括：

- Time Step 滑条和 Play/Pause 播放按钮，用于展示 Nyx 密度场随时间演化。
- Density Percentile Range 刷选，默认 99%-100%，对应 top 1% 高密度体素。
- X/Y/Z 投影方向切换。
- MIP、Mask、Masked MIP、Slice 和简化 Volume Composite 视图。
- log-density histogram 刷选，并联动空间投影视图。
- time-density heatmap 和统计曲线点击跳转时间步。
- 实验迭代路线图、方法体系图和结论卡片。

一键启动方法
============

推荐直接双击项目根目录下的：

start_nyx_web_demo.bat

该脚本会自动：

1. 检查 Web 数据是否已生成。
2. 如果缺少 metadata.json 或 vol_0000.bin，则自动运行 scripts/preprocess_for_web.py。
3. 寻找可用端口。
4. 启动本地 HTTP 服务器。
5. 自动打开浏览器。

如果双击失败，也可以使用命令行：

python start_nyx_web_demo.py

或手动运行：

python scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
cd Nyx_Web_Visualization/web
python -m http.server 8000

然后在浏览器打开：

http://localhost:8000

Web 展示注意事项
================

- 浏览器端展示的是降采样后的 normalized log-density 数据，适合课程展示和交互探索，不替代原始分辨率离线分析。
- 如果播放或 Volume Composite 模式较慢，可以切换为 MIP、Mask 或 Slice 模式。
- Web 页面需要通过本地服务器访问，不建议直接双击 index.html。
- Web 端关于空洞、丝状结构和节点的说明仍属于数据可视化课程实验分析，不作为正式天体物理科学结论。
