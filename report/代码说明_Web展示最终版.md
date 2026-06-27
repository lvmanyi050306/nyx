# Nyx 宇宙密度演化可视分析代码说明：Web 展示最终版

## 1 代码总体结构

项目采用“MATLAB 分步骤分析模块 + 工具函数 + Python Web 预处理 + HTML/CSS/JavaScript 交互展示”的结构。MATLAB 负责离线分析和结果图生成，Python 负责将原始体数据转换为 Web 轻量数据，Web 前端负责最终交互展示。

## 2 主入口与运行方式

MATLAB 主入口为：

```matlab
run('code/main.m')
```

Web 一键启动入口为：

```text
start_nyx_web_demo.bat
```

或命令行：

```bash
python start_nyx_web_demo.py
```

## 3 从无到有的代码演进关系

表 1 展示了代码模块与实验问题之间的对应关系。

表 1：从无到有的代码演进关系

| 阶段 | 代码文件 | 解决的问题 | 输出结果 | 对应报告章节 |
|---|---|---|---|---|
| 数据读取 | `read_nyx_dat.m` / `infer_grid_size.m` | `.dat` 二进制文件无法直接查看 | 三维密度体 | 第 2 章 |
| 读取验证 | `step1_check_data.m` | 无法确认轴顺序 | 中心切片、文件大小图 | 第 2 章 |
| 时序统计 | `step2_statistics_all_frames.m` | 单帧无法体现演化 | `density_stats.csv`、统计曲线 | 第 3 章 |
| 分布分析 | `step3_histogram_analysis.m` | 需要观察密度分布变化 | histogram、time-density heatmap | 第 3 章 |
| 三维可视化 | `step4_volume_render_keyframes.m` | 二维切片空间信息不足 | 体绘制关键帧 | 第 4 章 |
| 高密度验证 | `step5_high_density_selection.m` | 体绘制缺少统计验证 | P99 mask、MIP、等值面 | 第 5 章 |
| 结构指标 | `step6_structure_metrics.m` | 需要量化结构演化 | entropy、Gini、差分 MIP | 第 5 章 |
| 交互刷选 | `step7_interactive_dashboard.m` | 静态图无法探索 | linked brushing dashboard | 第 6 章 |
| Web 展示 | `preprocess_for_web.py` / `app.js` | MATLAB GUI 不便答辩展示 | HTML 单页交互系统 | 第 7 章 |
| 进阶分析 | `step8` / `step9` / `step10` | 需要结构识别和阶段划分 | 相空间、Hessian、相似性矩阵 | 第 8 章 |

## 4 MATLAB 分步骤分析模块

### `read_nyx_dat.m`

功能：读取 Nyx `.dat` 文件，自动推断 n×n×n 网格尺寸，并恢复 x-y-z 三维体。

### `step1_check_data.m`

功能：读取首个时间步，生成 XY/XZ/YZ 中心切片和文件大小一致性检查图。

### `step2_statistics_all_frames.m`

功能：遍历全部时间步，计算 mean、std、max、P01、P05、P50、P95、P99 等统计量。

### `step3_histogram_analysis.m`

功能：生成代表时间步 log-density histogram 和全时间步 time-density heatmap。

### `step4_volume_render_keyframes.m`

功能：使用自定义 alpha compositing 进行体绘制，并输出传递函数对比图。

### `step5_high_density_selection.m`

功能：使用原始 density 的 P99 阈值筛选 top 1% 高密度体素，输出 MIP 和多阈值等值面。

### `step6_structure_metrics.m`

功能：计算结构指标，包括 P99-P01、P99/mean、entropy、Gini、void/dense fraction 和差分 MIP。

### `step7_interactive_dashboard.m`

功能：实现 MATLAB linked brushing 仪表盘，支持时间步、密度区间和投影方向联动。

## 5 进阶分析模块

### `step8_density_gradient_phase_space.m`

功能：构建 normalized log-density 与 gradient magnitude 的二维相空间，用于区分空洞背景、丝状边界、节点边界和致密核心。

### `step9_hessian_cosmic_web_classification.m`

功能：基于 Hessian 特征值粗略分类 Void、Sheet、Filament 和 Node。

### `step10_time_similarity_stage_analysis.m`

功能：基于 log-density histogram 计算时间步相似性矩阵，并划分演化阶段。

## 6 Web 展示系统运行流程

Web 展示系统位于 `Nyx_Web_Visualization/`。推荐流程如下：

1. 运行 `preprocess_for_web.py`。
2. 生成 `metadata.json`、`density_stats.json`、`histograms.json`、`time_density_heatmap.json` 和 `vol_0000.bin` 至 `vol_0099.bin`。
3. 双击 `start_nyx_web_demo.bat`，或运行 `python start_nyx_web_demo.py`。
4. 浏览器打开 `http://localhost:8000`。
5. 演示 time slider、Play、Top 1% brush、X/Y/Z 投影和 time-density heatmap。

## 7 Web 文件说明

表 2 展示 Web 展示系统主要文件。

表 2：Web 展示系统文件说明

| 文件 | 功能 | 说明 |
|---|---|---|
| `Nyx_Web_Visualization/scripts/preprocess_for_web.py` | Web 数据预处理 | 读取 `.dat`、log-density、归一化、降采样、输出 JSON/bin |
| `Nyx_Web_Visualization/web/index.html` | 页面结构 | 定义控制面板、空间视图、直方图、heatmap 和结论区 |
| `Nyx_Web_Visualization/web/style.css` | 页面样式 | 深色宇宙主题仪表盘风格 |
| `Nyx_Web_Visualization/web/app.js` | 前端交互逻辑 | 懒加载体数据、渲染 MIP/Mask/Slice、histogram brush |
| `start_nyx_web_demo.py` | Python 启动器 | 自动检查数据、启动服务器、打开浏览器 |
| `start_nyx_web_demo.bat` | Windows 一键启动 | 双击运行 Web 作品 |

## 8 工具函数

表 3 展示 MATLAB 工具函数。

表 3：工具函数说明

| 工具函数 | 功能 |
|---|---|
| `ensure_folder.m` | 自动创建输出目录 |
| `save_figure.m` | 统一保存图像 |
| `normalize_percentile.m` | 百分位裁剪与归一化 |
| `smoothstep.m` | 平滑透明度控制 |
| `custom_nyx_colormap.m` | 自定义 Nyx colormap |
| `volume_render_alpha_composite.m` | 自定义体绘制 |
| `gini_coefficient.m` | 计算 Gini 系数 |
| `compute_gradient_magnitude.m` | 计算三维梯度幅值 |
| `compute_hessian_eigenvalues_3d.m` | 计算 Hessian 特征值 |
| `classify_cosmic_web_hessian.m` | Hessian 结构分类 |
| `cosine_similarity_matrix.m` | 时间步 histogram 相似性 |
| `simple_stage_segmentation.m` | 简单阶段划分 |

## 9 答辩讲解顺序

1. 说明 `.dat` 文件无法直接查看，因此首先恢复三维体数据。
2. 展示中心切片和文件大小检查，说明数据读取正确。
3. 展示 histogram、time-density heatmap 和统计曲线，说明密度分布演化。
4. 展示体绘制关键帧和传递函数，说明三维结构表达。
5. 展示 P99 top 1% MIP 和多阈值等值面，说明高密度尾部具有空间意义。
6. 展示 linked brushing dashboard，说明统计区间与空间位置联动。
7. 打开 Web 页面，演示 time slider、Play、Top 1% brush 和 X/Y/Z 投影。
8. 总结可视化技术在 Nyx 宇宙密度演化分析中的价值。

## 10 可选功能和降级方案

表 4 展示可选功能和降级方案。

表 4：可选功能和降级方案

| 功能 | 首选实现 | 降级方案 |
|---|---|---|
| P99 连通域分析 | `bwconncomp` | 工具箱不可用时跳过 |
| 3D Gaussian smoothing | `imgaussfilt3` | `smooth3` 或简单卷积 |
| 体数据降采样 | `imresize3` | 步长抽样或块平均 |
| 离线体绘制 | alpha compositing | 使用 MIP |
| Web 展示 | `start_nyx_web_demo.bat` | 命令行运行 `python start_nyx_web_demo.py` |
| Web 体绘制 | Canvas 简化合成 | 切换 MIP、Mask 或 Slice |
