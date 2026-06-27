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


常见问题
========

没有 .dat 文件怎么办？
  请先将 Nyx 原始数据文件放入 data/raw/。至少需要一个非空 .dat 文件才能运行数据检查；如果要复现实验报告中的完整时序结果，建议放入 0000.dat 至 0099.dat。

图片没有生成怎么办？
  请先确认 MATLAB 当前目录为项目根目录，并运行 run('code/main.m')。如果某一步失败，可以单独运行对应 step 文件，例如 step3_histogram_analysis(pwd) 或 step4_volume_render_keyframes(pwd)。

Image Processing Toolbox 不可用怎么办？
  主流程仍可运行。程序会跳过 bwconncomp 连通域分析，并在结构指标表中保留 NaN 或警告信息。切片、统计、直方图、体绘制、P99 MIP 和仪表盘不依赖该工具箱。

体绘制太慢怎么办？
  可先使用 results/frames/ 中的 MIP 帧图进行视频展示。main.m 默认生成 MIP 视频帧，比完整体绘制更快。若需要加速体绘制，可减少关键帧数量或降低输入体数据分辨率。

FFmpeg 不可用怎么办？
  不影响 MATLAB 分析和图片生成。FFmpeg 只用于将 results/frames/frame_*.png 合成为 demo.mp4。若未安装 FFmpeg，可以直接提交帧图或在其他视频软件中合成。

快速检查清单
============

- data/raw/ 是否包含 0000.dat 至 0099.dat 或至少一个非空 .dat 文件。
- code/main.m 是否能在 MATLAB 中完整运行。
- data/processed/ 是否生成 density_stats.csv 和 structure_metrics.csv。
- results/ 是否生成各类 PNG 图片。
- report/ 技术报告中是否没有图片缺失提示等异常标记。
- results/frames/ 是否生成 frame_0000.png 至 frame_0099.png。
- 如需视频，是否已使用 FFmpeg 生成 demo.mp4。
