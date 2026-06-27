# Answer Sheet

## 1. 作品信息

作品名称：基于体绘制与相空间刷选的 Nyx 宇宙密度演化可视分析  
课程名称：数据可视化  
作品类型：科学可视化 / 体数据可视化 / 时序数据可视分析  
数据来源：Nyx 宇宙学模拟密度数据  
实现工具：MATLAB、Python、FFmpeg  

## 2. 问题与目标

本作品以 Nyx 宇宙学模拟密度数据为对象，围绕三维密度场随时间演化的可视分析展开。数据由 0000.dat 至 0099.dat 等二进制文件组成，每个文件对应一个时间步，每个时间步为 n×n×n 的三维密度体。作品目标是从二进制数据中恢复三维体数据，利用体绘制、统计图表、高密度区域筛选和交互式 linked brushing 分析宇宙密度从相对均匀到团块化、网络化的演化过程。

## 3. 数据处理方法

程序使用 fopen(filename,'r','ieee-le') 和 fread 读取 little-endian float32 数据，根据 numel(data) 自动推断网格尺寸 n，并将原始 z-y-x 存储顺序重排为 MATLAB 中更直观的 x-y-z 三维体数据。显示阶段使用 log10(max(density,eps)) 压缩动态范围，并采用 P5 到 P99.7 的百分位裁剪和归一化；统计分析和 P99 高密度阈值筛选仍基于原始 density。

## 4. 主要可视化方法

1. 数据完整性检查：输出中心切片和文件大小一致性检查图。  
2. 时序统计分析：计算 mean、std、min、max、P01、P05、P50、P95、P99、P99.7、P99.9，以及 log-density 偏度和峰度。  
3. 直方图分析：绘制 t=0000、0030、0060、0099 的 log-density histogram，并构建时间-密度热力图。  
4. 自定义体绘制：实现 alpha compositing，不依赖 volshow，结合自定义 LUT、smoothstep 透明度函数和梯度增强。  
5. 高密度区域筛选：使用每帧原始 density 的 P99 作为 top 1% 阈值，输出三方向 MIP 和等值面。  
6. 多阈值等值面：使用 P90、P95、P99 展示宇宙网结构从丝状外壳到致密节点的层次。  
7. 交互式刷选：左侧显示 log-density histogram，右侧显示空间投影，用户可通过百分位滑条联动选择密度区间。

## 5. 主要发现

实验结果显示，早期时间步的密度分布较集中，体绘制中结构较弱；随着时间推进，密度标准差、高百分位和最大值增强，高密度尾部逐渐拉长。P99 以上体素在空间中集中于丝状结构交汇处和高密度节点，而低密度区域逐渐扩张为空洞。多阈值等值面显示 P90 形成较大尺度丝状外壳，P95 更集中，P99 仅保留最致密节点，体现出宇宙网结构的层级性。

## 6. 创新点与技术亮点

本作品的主要亮点包括：  
1. 完整实现 Nyx 二进制体数据读取和轴顺序恢复；  
2. 使用 log-density 与百分位归一化解决高动态范围显示问题；  
3. 自定义 alpha compositing 体绘制与多种传递函数设计；  
4. 使用梯度增强突出丝状结构和团块边界；  
5. 将 P99 高密度统计阈值与三维空间 MIP、等值面结合；  
6. 构建 linked brushing 仪表盘，将统计分布与空间结构实时联动。

## 7. 输出文件

主要输出包括：

- data/processed/density_stats.csv
- data/processed/high_density_threshold.csv
- data/processed/structure_metrics.csv
- results/01_data_check/center_slices_0000.png
- results/02_histograms/time_density_heatmap.png
- results/03_statistics/percentile_curve.png
- results/04_volume_render/volume_keyframes_compare.png
- results/05_high_density/nested_isosurfaces_t0099.png
- results/06_structure_metrics/difference_mip_first_last.png
- results/07_dashboard/dashboard_preview.png
- results/frames/frame_0000.png 至 frame_0099.png

## 8. 运行方法

将 .dat 文件放入 data/raw/，在 MATLAB 中进入项目根目录，运行：

```matlab
run('code/main.m')
```

如需打开交互式仪表盘，运行：

```matlab
step7_interactive_dashboard(pwd)
```
