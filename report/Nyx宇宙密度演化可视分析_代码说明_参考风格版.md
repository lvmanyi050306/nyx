# Nyx 宇宙密度演化可视分析代码说明：参考风格版

## 1 项目代码结构

本项目代码分为四类：MATLAB 分步骤分析模块、MATLAB 工具函数、Python Web 数据预处理脚本、HTML/CSS/JavaScript Web 展示系统。MATLAB 负责离线科学可视化分析，Python 负责生成浏览器可加载的数据，Web 端负责最终交互展示。

## 2 MATLAB 主流程

主入口为 `code/main.m`。运行后依次执行数据检查、统计分析、直方图分析、体绘制、高密度筛选、结构指标计算，并以 try/catch 方式运行进阶模块。该设计保证基础流程优先跑通，高级模块失败时不会影响已有结果。

## 3 Web 展示系统运行流程

Web 展示系统位于 `Nyx_Web_Visualization/`。首先运行 `preprocess_for_web.py` 生成 `metadata.json`、`density_stats.json`、`histograms.json`、`time_density_heatmap.json` 和 `vol_0000.bin` 至 `vol_0099.bin`。随后双击 `start_nyx_web_demo.bat` 或运行 `python start_nyx_web_demo.py`，浏览器会打开 `http://localhost:8000`。答辩时可演示 time slider、Play、Top 1% brush 和 X/Y/Z 投影。

## 4 模块与报告章节对应关系

表 1：模块与报告章节对应关系

| 模块 | 功能 | 对应章节 |
|---|---|---|
| `read_nyx_dat.m` | Nyx 二进制读取 | 第 2 章 |
| `step1_check_data.m` | 中心切片和文件大小检查 | 第 2 章 |
| `step2_statistics_all_frames.m` | 全时间步统计 | 第 3 章 |
| `step3_histogram_analysis.m` | 直方图和 heatmap | 第 3、4 章 |
| `step4_volume_render_keyframes.m` | 体绘制与传递函数 | 第 3、4 章 |
| `step5_high_density_selection.m` | P99 高密度筛选 | 第 3、4 章 |
| `step6_structure_metrics.m` | 结构指标和差分 MIP | 第 4 章 |
| `step7_interactive_dashboard.m` | linked brushing | 第 3、4 章 |
| `step8_density_gradient_phase_space.m` | density-gradient 相空间 | 第 3、4 章 |
| `step9_hessian_cosmic_web_classification.m` | Hessian 分类 | 第 3、4 章 |
| `step10_time_similarity_stage_analysis.m` | 时间步相似性 | 第 3、4 章 |
| `Nyx_Web_Visualization/` | Web 交互展示 | 第 3、4 章 |

## 5 答辩讲解顺序

建议先说明数据是不可直接查看的 `.dat` 体数据，再展示读取验证结果；随后讲统计分析和 log-density，展示体绘制关键帧；接着用 P99 筛选说明高密度尾部与空间节点的对应关系；最后打开 Web 页面演示时间播放、histogram brush 和 top 1% 高密度联动。
