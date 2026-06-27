# Nyx 宇宙密度演化可视分析代码说明：迭代过程版

## 1 代码总体结构

本项目采用“主入口 + 分步骤分析模块 + 工具函数 + Web 展示系统”的组织方式。`code/main.m` 负责自动识别项目根目录、添加路径、检查数据文件、创建输出目录，并依次运行基础分析模块和进阶分析模块。每个 `step*.m` 文件对应报告中的一个实验阶段，`code/utils/` 保存通用工具函数。最终展示层位于 `Nyx_Web_Visualization/`，其中 Python 脚本负责生成浏览器可加载的轻量数据，HTML/CSS/JavaScript 负责实现单页交互展示。

## 2 主入口

`code/main.m` 是一键运行入口。基础流程包括：

1. `step1_check_data.m`
2. `step2_statistics_all_frames.m`
3. `step3_histogram_analysis.m`
4. `step4_volume_render_keyframes.m`
5. `step5_high_density_selection.m`
6. `step6_structure_metrics.m`

进阶模块以 `try/catch` 方式追加运行：

1. `step8_density_gradient_phase_space.m`
2. `step9_hessian_cosmic_web_classification.m`
3. `step10_time_similarity_stage_analysis.m`

交互仪表盘 `step7_interactive_dashboard.m` 不默认阻塞运行，可由用户手动调用。

Web 展示系统不由 `main.m` 直接启动，而是通过 `start_nyx_web_demo.bat` 或 `start_nyx_web_demo.py` 一键运行。启动器会检查 `web/assets/data/` 是否存在，必要时自动调用 `scripts/preprocess_for_web.py` 生成 Web 数据，然后启动本地 HTTP 服务器并打开浏览器。

## 3 从无到有的代码演进关系

| 阶段 | 代码文件 | 解决的问题 | 输出结果 | 对应报告章节 |
|---|---|---|---|---|
| 数据读取 | `read_nyx_dat.m` / `infer_grid_size.m` | `.dat` 二进制文件无法直接查看 | 恢复 n×n×n 三维密度体 | 第 2 章 |
| 读取验证 | `step1_check_data.m` | 无法确认读取方向和文件一致性 | 中心切片、文件大小检查 | 第 2 章 |
| 全时间步量化 | `step2_statistics_all_frames.m` | 单帧无法体现演化过程 | `density_stats.csv`、统计曲线 | 第 3 章 |
| 分布展示 | `step3_histogram_analysis.m` | 统计指标不能展示完整分布 | log-density histogram、time-density heatmap | 第 3 章 |
| 三维结构展示 | `step4_volume_render_keyframes.m` | 二维切片空间信息不足 | 体绘制关键帧、传递函数对比 | 第 4 章 |
| 高密度定位 | `step5_high_density_selection.m` | 高密度尾部缺少空间定位 | P99 mask、MIP、等值面 | 第 5 章 |
| 结构演化量化 | `step6_structure_metrics.m` | 视觉结果缺少量化验证 | 结构指标、差分 MIP | 第 5 章 |
| 交互探索 | `step7_interactive_dashboard.m` | 静态图无法探索其他密度区间 | linked brushing dashboard | 第 6 章 |
| 二维相空间 | `step8_density_gradient_phase_space.m` | 单变量密度刷选不足 | density-gradient 相空间和区域 MIP | 第 7 章 |
| 结构识别 | `step9_hessian_cosmic_web_classification.m` | 仅靠视觉观察难以分类结构 | Void/Sheet/Filament/Node 分类 | 第 7 章 |
| 阶段划分 | `step10_time_similarity_stage_analysis.m` | 代表时间步选择缺少依据 | 相似性矩阵和阶段划分 | 第 7 章 |
| Web 展示 | `Nyx_Web_Visualization/` / `start_nyx_web_demo.py` | MATLAB GUI 和静态报告不便于答辩现场演示 | HTML 单页交互系统、时间播放、直方图刷选、top 1% 联动 | 第 7.7 节、第 8.11 节 |

## 4 数据读取相关代码

### `code/read_nyx_dat.m`

功能：读取单个 Nyx `.dat` 文件，并恢复为三维体数据。

输入：`.dat` 文件路径。

输出：`single` 类型三维数组 `V`。

关键逻辑：使用 little-endian float32 读取；自动推断网格尺寸；先 reshape 为 `[z,y,x]`，再 permute 为 `[x,y,z]`。

### `code/infer_grid_size.m`

功能：根据体素总数推断 n，使 `numel(data)=n^3`。若无法构成规则立方体，则报错提示文件尺寸异常。

## 5 分步骤分析代码

### `code/step1_check_data.m`

功能：完成数据完整性检查，生成中心切片和文件大小一致性检查图。

对应问题：读取出的数据是否合理，轴顺序是否基本正确。

### `code/step2_statistics_all_frames.m`

功能：遍历所有时间步并计算 density 和 log-density 统计量。

对应问题：如何从单帧观察扩展到全时间步量化分析。

### `code/step3_histogram_analysis.m`

功能：绘制代表时间步 log-density histogram 和 time-density heatmap。

对应问题：如何展示密度分布形态及其随时间的整体变化。

### `code/step4_volume_render_keyframes.m`

功能：对代表时间步进行自定义 alpha compositing 体绘制，并比较三种传递函数。

对应问题：二维切片无法完整表达三维空间结构。

### `code/step5_high_density_selection.m`

功能：使用原始 density 的 P99 作为 top 1% 阈值，生成高密度 mask、MIP 和多阈值等值面。

对应问题：如何验证直方图右尾是否对应空间中的高密度节点。

### `code/step6_structure_metrics.m`

功能：计算结构指标、连通域指标和首末时间步差分 MIP。

对应问题：如何对结构演化进行量化补充。

### `code/step7_interactive_dashboard.m`

功能：实现 linked brushing 交互仪表盘。

对应问题：静态图像无法灵活探索不同时间步和密度区间。

### `code/step8_density_gradient_phase_space.m`

功能：构建 normalized log-density 与 gradient magnitude 的二维相空间热力图，并输出典型区域空间 MIP。

对应问题：一维 density 刷选不能区分结构边界和致密核心。

### `code/step9_hessian_cosmic_web_classification.m`

功能：基于 Hessian 特征值进行 Void、Sheet、Filament、Node 粗分类，输出分类切片、结构占比 CSV 和占比曲线。

对应问题：仅靠视觉观察难以识别局部结构类型。

### `code/step10_time_similarity_stage_analysis.m`

功能：基于全时间步 log-density histogram 计算时间步相似性矩阵，输出演化阶段划分。

对应问题：代表时间步选择和阶段划分缺少数据依据。

## 6 Web 交互展示代码

### `Nyx_Web_Visualization/scripts/preprocess_for_web.py`

功能：将原始 Nyx `.dat` 文件转换为浏览器可加载的轻量 Web 数据。

输入：`data/raw/` 下的原始 `.dat` 文件，以及可选的 `data/processed/` 统计结果。

输出：`metadata.json`、`density_stats.json`、`histograms.json`、`time_density_heatmap.json`、`time_similarity_stage.json` 和 `vol_0000.bin` 至 `vol_0099.bin` 等降采样体数据。

关键逻辑：读取 little-endian float32；恢复 x-y-z 三维体；计算 log-density；做 P5-P99.7 百分位归一化；降采样到 64×64×64；保存为 Float32Array 二进制文件。

### `Nyx_Web_Visualization/web/index.html`

功能：定义最终 HTML 单页交互展示系统的页面结构。

主要区域：顶部项目说明、左侧控制面板、主空间视图、右侧直方图刷选视图、底部 time-density heatmap、统计指标曲线、路线图、方法图和结论卡片。

### `Nyx_Web_Visualization/web/style.css`

功能：定义深色宇宙主题仪表盘风格。

设计要点：深蓝紫背景、半透明面板、高亮指标卡、Canvas 主视图、适合 1920×1080 课堂录屏展示。

### `Nyx_Web_Visualization/web/app.js`

功能：实现浏览器端数据加载、体数据懒加载、时间步播放、百分位刷选、MIP/Mask/Slice/简化体合成、histogram brush、time-density heatmap 和统计曲线联动。

对应问题：如何把 MATLAB/Python 离线分析结果转化为可以现场演示的 Web 交互作品。

### `start_nyx_web_demo.py` / `start_nyx_web_demo.bat`

功能：一键启动 Web 演示。脚本会检查 Web 数据是否存在，必要时自动运行预处理，然后寻找可用端口、启动本地 HTTP 服务器并打开浏览器。

使用方式：双击 `start_nyx_web_demo.bat`，或在命令行运行 `python start_nyx_web_demo.py`。

## 7 工具函数

| 工具函数 | 功能 |
|---|---|
| `ensure_folder.m` | 若目标目录不存在，则自动创建 |
| `save_figure.m` | 统一保存 MATLAB figure，兼容新旧 MATLAB |
| `normalize_percentile.m` | 百分位裁剪并归一化到 [0,1] |
| `smoothstep.m` | 平滑阶跃函数，用于透明度传递函数 |
| `custom_nyx_colormap.m` | 自定义 Nyx 颜色映射 |
| `volume_render_alpha_composite.m` | 自定义 alpha compositing 体绘制 |
| `gini_coefficient.m` | 计算 density 的 Gini 系数 |
| `compute_gradient_magnitude.m` | 计算三维梯度幅值 |
| `compute_hessian_eigenvalues_3d.m` | 计算三维 Hessian 特征值 |
| `classify_cosmic_web_hessian.m` | 基于 Hessian 特征值进行结构分类 |
| `cosine_similarity_matrix.m` | 计算 histogram 向量之间的余弦相似性 |
| `simple_stage_segmentation.m` | 基于 distance from start 划分演化阶段 |

## 8 答辩讲解顺序

1. 说明 `.dat` 文件不能直接查看，因此首先恢复三维体数据。
2. 展示中心切片，说明读取和轴顺序恢复基本正确。
3. 展示全时间步统计曲线和 time-density heatmap，说明从单帧扩展到演化过程。
4. 说明 log-density 和百分位归一化解决高动态范围显示问题。
5. 展示体绘制结果，说明三维宇宙网结构的整体表达。
6. 展示 P99 筛选和多阈值等值面，说明统计右尾与空间节点对应。
7. 展示 linked brushing dashboard，说明交互探索能力。
8. 展示 density-gradient、Hessian 和 time similarity，说明进阶结构识别和阶段划分。
9. 打开 Web 页面，现场演示 time slider、Play、histogram brush 和 top 1% 高密度空间联动。
10. 最后总结系统优势、局限和后续扩展方向。

## 9 可选功能和降级方案

| 功能 | 首选实现 | 降级方案 |
|---|---|---|
| P99 连通域分析 | `bwconncomp` | 工具箱不可用时跳过并 warning |
| 3D Gaussian smoothing | `imgaussfilt3` | `smooth3` 或 separable convolution |
| 体数据降采样 | `imresize3` | 使用步长抽样 |
| 体绘制 | 自定义 alpha compositing | 如果较慢，可使用 MIP 帧 |
| 视频生成 | FFmpeg | 只保留 `results/frames/` |
| 阶段划分 | distance_from_start 分位划分 | 分位不稳定时按时间均分四段 |
| Web 启动 | `start_nyx_web_demo.bat` | 命令行运行 `python start_nyx_web_demo.py` |
| Web 体绘制 | Canvas 简化 alpha compositing | 切换为 MIP、Mask 或 Slice 模式 |
