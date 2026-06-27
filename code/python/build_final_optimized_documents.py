# -*- coding: utf-8 -*-
"""生成 Nyx 项目正式提交前的“最终优化版”报告和代码说明。

输出：
    report/大作业技术报告_最终优化版.md
    report/代码说明_Web展示最终版.md
    report/Nyx宇宙密度演化可视分析_技术报告_最终优化版.docx
    report/Nyx宇宙密度演化可视分析_代码说明_Web展示最终版.docx
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.font_manager import FontProperties

from build_iteration_process_documents import (
    add_markdown_to_docx,
    create_iteration_roadmap,
    create_web_system_overview,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "report"
FIG_DIR = PROJECT_ROOT / "results" / "report_figures"


def cn_fonts() -> tuple[FontProperties, FontProperties]:
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/simhei.ttf")
    return FontProperties(fname=str(font_path)), FontProperties(fname=str(font_path), weight="bold")


def create_web_dashboard_preview(output_path: Path) -> None:
    """用代码生成 Web 单页作品的界面结构预览图。"""
    cn_font, cn_bold = cn_fonts()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 7.6), dpi=300)
    fig.patch.set_facecolor("#07101f")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7.6)
    ax.axis("off")

    def panel(x, y, w, h, title, color="#0d1a33"):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.025,rounding_size=0.08",
                           facecolor=color, edgecolor="#35507a", linewidth=1.4)
        ax.add_patch(p)
        ax.text(x + 0.18, y + h - 0.28, title, color="#eaf6ff", fontsize=10.5,
                va="center", fontproperties=cn_bold)

    ax.text(7, 7.18, "Nyx Density Explorer HTML Interactive Dashboard",
            ha="center", color="#eaf6ff", fontsize=17, fontproperties=cn_bold)
    ax.text(7, 6.86, "time slider + histogram brushing + top 1% mask + time-density heatmap",
            ha="center", color="#9fb2d0", fontsize=9.5, fontproperties=cn_font)

    panel(0.35, 0.55, 2.45, 5.95, "左侧控制面板", "#101d36")
    controls = ["Time Step", "Play / Pause", "Density 99%-100%", "X/Y/Z 投影", "MIP / Mask / Slice", "Transfer Function"]
    for i, txt in enumerate(controls):
        y = 5.88 - i * 0.75
        ax.add_patch(Rectangle((0.62, y), 1.9, 0.28, facecolor="#193356", edgecolor="#446894", linewidth=0.8))
        ax.text(0.72, y + 0.14, txt, color="#dcecff", va="center", fontsize=8.4, fontproperties=cn_font)

    panel(3.05, 2.05, 5.35, 4.45, "中央空间视图：Nyx Density Spatial View", "#0b1429")
    for r in range(44):
        for c in range(44):
            v = ((r * 13 + c * 7) % 41) / 40
            if (r - 22) ** 2 + (c - 20) ** 2 < 70 or (r - c + 8) ** 2 < 20:
                col = (1.0, 0.58 + 0.28 * v, 0.18)
            elif (r + c) % 17 < 3:
                col = (0.36, 0.18, 0.72)
            else:
                col = (0.02, 0.05 + 0.12 * v, 0.16 + 0.28 * v)
            ax.add_patch(Rectangle((3.42 + c * 0.105, 2.38 + r * 0.082), 0.1, 0.078,
                                   facecolor=col, edgecolor=col, linewidth=0))
    ax.text(3.45, 6.02, "t=0099 · Top 1% high-density cells", color="#ffd56f",
            fontsize=9.3, fontproperties=cn_bold)

    panel(8.65, 4.05, 4.95, 2.45, "右侧直方图刷选", "#101d36")
    for i in range(52):
        h = 0.12 + 1.45 * (0.18 + abs(i - 20) / 52) * (1 if i < 40 else 0.65)
        col = "#48d8ff" if i < 45 else "#ff9d3f"
        ax.add_patch(Rectangle((8.92 + i * 0.084, 4.38), 0.055, h, facecolor=col, edgecolor=col))
    ax.add_patch(Rectangle((12.62, 4.31), 0.62, 1.78, facecolor="#ff9d3f", alpha=0.23, edgecolor="#ffd56f", linewidth=1.2))
    ax.text(12.47, 6.16, "99%-100%", color="#ffd56f", fontsize=8.5, fontproperties=cn_bold)

    panel(8.65, 2.05, 4.95, 1.7, "指标卡片与结论", "#101d36")
    notes = ["Selected Ratio: 1.00%", "Stage: Late", "右尾密度区间与空间节点联动"]
    for i, txt in enumerate(notes):
        ax.text(8.95, 3.25 - i * 0.42, txt, color="#dcecff", fontsize=8.8, fontproperties=cn_font)

    panel(3.05, 0.55, 10.55, 1.15, "底部 time-density heatmap 与统计曲线", "#0d1a33")
    for i in range(90):
        for j in range(9):
            val = (i / 90) * 0.55 + (j / 9) * 0.45
            color = (0.12 + 0.55 * val, 0.18 + 0.35 * (1 - val), 0.55 + 0.35 * val)
            ax.add_patch(Rectangle((3.38 + i * 0.106, 0.85 + j * 0.06), 0.1, 0.055,
                                   facecolor=color, edgecolor=color, linewidth=0))
    ax.plot([3.4, 5.2, 7.1, 9.0, 12.7], [0.78, 0.86, 0.76, 1.1, 1.28],
            color="#ff9d3f", linewidth=2.0)

    fig.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="#07101f")
    plt.close(fig)


def report_markdown() -> str:
    return r"""# 基于体绘制与相空间刷选的 Nyx 宇宙密度演化可视分析

课程名称：数据可视化  
作品类型：科学可视化 / 体数据可视化 / 时序数据可视分析 / Web 交互展示  
数据来源：ChinaVis 2026 赛题 II Nyx 宇宙学模拟密度数据  
姓名：  
学号：  
班级：  
完成日期：  

## 摘要

Nyx 宇宙学模拟数据以连续 `.dat` 二进制文件存储三维时序密度场，不能像普通图像或表格一样直接查看。本实验以 ChinaVis 2026 赛题 II 科学可视化挑战赛中的 Nyx 密度数据为课程大作业对象，围绕“如何读取体数据、如何展示宇宙密度演化、如何验证高密度尾部的空间意义、如何形成最终可交互展示作品”展开。实验首先使用 little-endian float32 方式读取 `.dat` 文件，自动推断 n×n×n 网格尺寸，并将原始 z-y-x 顺序恢复为 x-y-z 三维密度体；随后通过中心切片和文件大小检查验证数据读取正确性。在分析阶段，实验引入 log-density 变换、全时间步统计、代表时间步直方图、time-density heatmap 和统计曲线，用于观察密度分布从集中到分化的变化。空间可视化方面，实验实现 MIP、自定义 alpha compositing 体绘制、传递函数设计和梯度增强，用于展示宇宙网结构。为了回答高密度尾部是否具有空间意义，实验使用 P99 top 1% mask、多阈值等值面、差分 MIP 和结构指标，将直方图右尾与丝状结构交汇处及致密节点联系起来。进一步地，实验实现 linked brushing 仪表盘和 HTML Web 单页交互系统，使用户可以通过 histogram brush 和密度百分位滑条选择密度区间，并实时查看对应空间投影。最后，项目扩展 density-gradient 二维相空间、Hessian 结构分类和时间步相似性矩阵，为结构识别和阶段划分提供补充。实验表明，体绘制、统计图、阈值筛选和交互刷选能够从不同角度解释 Nyx 密度演化；Web 展示系统则将离线分析结果转化为适合答辩演示的交互式科学可视化作品。本文结论服务于数据可视化课程实验，不作为正式天体物理科学结论。

## 1 问题描述

### 1.1 赛题背景

ChinaVis 2026 赛题 II 科学可视化挑战赛关注 Nyx 宇宙学模拟数据的可视分析。宇宙大尺度结构形成是现代天体物理中的重要问题，模拟数据通过三维密度场描述物质在空间中的分布及其随时间的演化。对于课程作业而言，该赛题提供了典型的科学体数据场景：数据规模较大、维度高、动态范围宽，并且同时具有空间结构和时间演化特征。

本项目不是正式参赛作品，而是基于该赛题数据完成的数据可视化课程大作业。项目重点不在于给出严格天体物理结论，而在于展示如何使用体绘制、统计图表、阈值筛选和交互刷选等可视化技术，帮助理解 Nyx 密度场从相对均匀到空洞、丝状结构和高密度节点逐渐显现的过程。

### 1.2 Nyx 数据特点

原始数据由 `0000.dat` 至 `0099.dat` 等文件组成，每个文件表示一个时间步。每个 `.dat` 文件内部是 little-endian float32 连续数值序列，可自动推断为 n×n×n 三维体数据，例如 128×128×128。原始线性顺序为 z 轴最快、y 轴其次、x 轴最慢，读取后必须恢复为 MATLAB 和 Web 显示中更直观的 x-y-z 三维体。

Nyx 密度数据具有三个重要特点。第一，它是二进制体数据，无法直接查看，需要先恢复空间结构。第二，density 动态范围较大，直接线性显示会使高密度体素主导视觉结果。第三，它是时序体数据，单个时间步不能完整回答密度演化问题，必须结合统计分析、空间可视化和交互探索。

### 1.3 赛题任务与本项目实现对应关系

表 1 总结了赛题任务与本项目实现之间的对应关系。该表说明本项目并不是简单堆叠图像，而是围绕体数据渲染、传递函数、光照增强、时序统计、相空间刷选和最终交互展示逐步完成赛题要求。

表 1：赛题任务与本项目实现对应关系

| 赛题要求 | 本项目实现 | 对应结果或模块 |
|---|---|---|
| 采用体数据渲染技术 | 自定义 alpha compositing 体绘制 | `step4_volume_render_keyframes.m`、`volume_keyframes_compare.png` |
| 设计合适的传递函数 | Balanced / Void / Filament / Node 传递函数 | `transfer_function_design.png` |
| 设计光照效果 | 梯度增强与类光照处理 | `volume_render_alpha_composite.m` |
| 展示宇宙演化中密度信息变化 | 体绘制关键帧、MIP、动画帧 | `volume_t0000.png` 至 `volume_t0099.png`、`results/frames/` |
| 宇宙密度时序统计特征分析 | 全时间步 density 统计、统计曲线、time-density heatmap | `step2_statistics_all_frames.m`、`step3_histogram_analysis.m` |
| 构建密度对数直方图 | log-density histogram | `histogram_compare_keyframes.png` |
| 量化追踪全域密度分布演化 | P99/mean、P99-P01、std、entropy、Gini | `structure_metrics.csv` |
| 相空间交互式刷选 | linked brushing dashboard | `step7_interactive_dashboard.m` |
| 筛选占比 1% 的极高密度区间 | P99 top 1% mask | `step5_high_density_selection.m` |
| 联动三维空间视图 | HTML Web 空间投影联动 | `Nyx_Web_Visualization/web/app.js` |
| 最终交互展示作品 | Nyx Density Explorer HTML 单页交互系统 | `index.html`、`style.css`、`app.js` |

### 1.4 本实验的可视化目标

本实验的目标可以概括为五个问题。第一，如何从不可直接查看的 `.dat` 文件恢复 Nyx 三维密度体。第二，如何通过统计图和 heatmap 描述密度分布随时间变化。第三，如何设计体绘制和传递函数展示三维宇宙网结构。第四，如何验证直方图右侧高密度尾部是否对应空间中的致密节点。第五，如何将离线分析结果转化为最终可交互展示作品，支持答辩现场演示。

### 1.5 从无到有的实验迭代思路

本实验采用“问题驱动—方法改进—结果验证—继续优化”的开发路线。首先解决数据读取问题，然后通过中心切片验证轴顺序；接着从单帧观察扩展到全时间步统计；再通过 log-density 和百分位归一化解决高动态范围显示问题；随后加入 MIP、体绘制、P99 筛选和结构指标；在静态结果基础上实现 linked brushing；最后将成果整理为 HTML Web 交互展示系统。

![图 1：Nyx 可视化项目从无到有的实验迭代路线图](../results/report_figures/iteration_roadmap.png)

图 1 展示了本项目的实验迭代路线。该图强调每个模块都对应前一阶段暴露出的不足：数据读取之后需要验证，统计分析之后需要空间表达，体绘制之后需要阈值验证，静态图之后需要交互探索，最终再通过 Web 系统形成可展示作品。其局限是路线图只表达开发逻辑，不直接展示数据结果，因此需要后续结果图进行支撑。

![图 2：Nyx 宇宙密度演化可视分析总体流程图](../results/report_figures/overall_workflow.png)

图 2 从系统角度总结了最终流程。Nyx 原始数据经过二进制解析、轴顺序恢复、log-density 变换和百分位归一化后，分别进入统计分析、体绘制、高密度结构验证和交互展示路线。该图说明本项目最终形成的是完整可视分析系统，而不是单一图表。

![图 3：项目关键词词云](../results/report_figures/nyx_keyword_wordcloud.png)

图 3 展示项目关键词。Nyx、Density、Volume Rendering、Linked Brushing、P99 等词权重较高，说明本实验核心围绕体数据、密度分布、高密度筛选和交互刷选展开。词云适合展示项目概貌，但不能替代定量分析。

![图 4：方法亮点气泡标签图](../results/report_figures/nyx_method_bubble_tags.png)

图 4 将方法分为数据解析、统计分析、体绘制、空间结构和交互等类别。它说明本项目的方法体系具有层次关系：底层是数据恢复，中层是统计和空间可视化，上层是交互展示与解释。

## 2 数据读取与验证

### 2.1 `.dat` 二进制格式分析

在项目初始阶段，`.dat` 文件本身无法直接查看，因此首要任务不是绘图，而是恢复数据结构。每个文件保存一个时间步的三维密度场，内部没有表头和尺寸信息，只有连续 float32 数值。文件大小可以用于反推体素数量，再由体素数量推断立方体网格边长。

### 2.2 little-endian float32 数据读取

读取时使用 little-endian float32 格式。MATLAB 端使用 `fopen(filename,'r','ieee-le')` 和 `fread(...,'single=>single')`，Python Web 预处理端使用 `np.fromfile(path, dtype='<f4')`。统一读取方式保证 MATLAB 离线分析和 Web 数据生成使用同一数据解释规则。

### 2.3 网格尺寸自动推断

读取一维数组后，程序根据 `numel(data)=n^3` 自动推断 n。如果 n 的三次方不等于体素数量，则说明文件尺寸异常或数据不完整，程序会报错或跳过该文件。该步骤避免将网格尺寸写死，使代码能够适应不同分辨率的 Nyx 数据。

### 2.4 z-y-x 到 x-y-z 的轴顺序恢复

原始线性顺序为 z 轴最快、y 轴其次、x 轴最慢。程序先将一维数组 reshape 为 `[z,y,x]`，再 permute 为 `[x,y,z]`。如果轴顺序恢复错误，后续切片和投影会出现条纹、错位或不连续纹理。

### 2.5 中心切片验证

![图 5：数据读取检查中心切片图](../results/01_data_check/center_slices_0000.png)

图 5 展示读取第一个时间步后提取的 XY、XZ、YZ 三个中心切片。三个方向均呈现连续密度纹理，没有明显断裂、条纹或规则错位，说明 little-endian 读取、reshape 和 permute 过程基本正确。该图解决了“数据能否正确读出”的问题，但它只能观察局部截面，不能完整展示三维结构，因此后续需要 MIP 和体绘制。

### 2.6 文件大小一致性检查

![图 6：文件大小一致性检查图](../results/01_data_check/file_size_check.png)

图 6 检查所有 `.dat` 文件大小是否一致。若所有时间步文件大小一致，说明每个时间步具有相同网格规模，后续全时间步统计和动画播放才具有可比性。该图与中心切片图相互印证：中心切片验证单帧读取方向，文件大小检查验证时序数据完整性。其局限是文件大小一致不能保证数值内容完全正确，因此仍需 NaN、Inf、负值和统计范围检查。

### 2.7 本阶段小结

本阶段完成了从不可见二进制文件到三维密度体的恢复，并通过切片和文件大小检查验证读取结果。它为后续统计分析、体绘制、高密度筛选和 Web 预处理提供了数据基础。

## 3 宇宙密度时序统计分析

### 3.1 为什么需要全时间步统计

单个时间步只能显示某一瞬间的密度状态，不能回答“密度分布如何随时间演化”。因此，本实验遍历所有非空 `.dat` 文件，逐帧计算密度统计量，并将结果保存为 `density_stats.csv` 和 `statistics.mat`。

### 3.2 统计指标设计

统计指标包括 mean、std、min、max、P01、P05、P50、P95、P99、P99.7、P99.9，以及 log-density 的均值、标准差、偏度和峰度。其中 mean 反映整体水平，std 和 max 反映波动与极端值，P95/P99 等高百分位用于观察高密度尾部，P99/mean 和 P99-P01 用于量化密度分化程度。

### 3.3 log-density 变换

原始 density 动态范围较大，直接线性显示会使高密度区域占据主要视觉范围，中低密度结构不明显。因此实验使用 `log10(max(density, eps))` 压缩动态范围。需要注意的是，统计阈值如 P99 仍基于原始 density 计算，而显示和直方图主要使用 log-density。

### 3.4 代表时间步对数密度直方图

![图 7：代表时间步对数密度直方图对比图](../results/02_histograms/histogram_compare_keyframes.png)

图 7 对比 t=0000、0030、0060、0099 的 log-density 直方图。直方图展示了单帧密度分布的中心、宽度和右尾变化。若后期直方图变宽且右尾增强，说明高密度体素比例和极端密度值增加。该图说明密度分布从集中向分化发展，但它不包含空间位置信息，因此需要 P99 mask 和 linked brushing 补充。

### 3.5 time-density heatmap

![图 8：时间-密度热力图](../results/02_histograms/time_density_heatmap.png)

图 8 将所有时间步的 log-density histogram 按时间堆叠为二维热力图。横轴为 time step，纵轴为 log-density，颜色表示 probability。该图从全局角度展示密度分布随时间迁移、扩散和高密度尾部增强的趋势。它与图 7 相互印证：图 7 展示代表帧，图 8 展示完整时序。但 heatmap 仍然是统计分布图，不能直接定位空间结构。

### 3.6 统计曲线分析

![图 9：密度统计曲线](../results/report_figures/combined_statistics_curves.png)

图 9 展示 mean、std、max、百分位和结构指标随时间的变化。mean density 可能变化不明显，因此不应作为唯一判断依据；std、P95、P99、P99/mean 和 P99-P01 更能体现密度波动增强和高密度尾部拉长。统计曲线为体绘制中观察到的结构增强提供量化支撑，但它们仍缺少空间位置信息。

### 3.7 本阶段小结

本阶段将分析对象从单帧图像扩展到全时间步统计，说明 Nyx 密度场不仅在空间上具有结构，也在时间上呈现分布扩散和尾部增强。下一步需要将统计变化映射回三维空间。

## 4 三维体数据可视化

### 4.1 二维切片的局限

中心切片只能观察体数据的局部截面，可能遗漏三维空间中的丝状结构和节点。因此实验进一步使用 MIP 和体绘制方法，从二维截面扩展到三维整体结构表达。

### 4.2 MIP 最大强度投影

MIP 沿某一方向取最大密度值，可以突出高密度结构的二维投影。它适合快速观察高密度区域的大致空间分布，但会丢失深度信息，因此不能完全替代三维体绘制和交互探索。

### 4.3 自定义 alpha compositing 体绘制

本实验实现了不依赖 `volshow` 的自定义 alpha compositing。归一化 log-density 体数据沿 z 方向从后向前逐层合成，颜色由 LUT 决定，透明度由 smoothstep 函数控制。低密度区域较透明，中密度区域用于显示丝状结构，高密度区域更不透明以突出节点。

### 4.4 传递函数设计

![图 10：三种体绘制传递函数设计对比](../results/report_figures/transfer_function_design.png)

图 10 展示 Void、Filament、Node 等传递函数的透明度设计。空洞型强调低密度区域，丝状结构型增强中密度连续结构，节点型突出高密度尾部。该图说明传递函数不是单纯美化图像，而是针对不同分析任务设计视觉映射。其局限是不同传递函数会影响观察重点，因此体绘制结果需要统计曲线和阈值分析支撑。

### 4.5 梯度增强与类光照

为了突出密度边界和丝状结构边缘，体绘制中计算归一化体数据的三维梯度幅值，并用梯度增强 alpha 或亮度。这种方法不是物理真实光照，但可以增强边界感和空间层次，使宇宙网节点和丝状结构更容易观察。

### 4.6 代表时间步体绘制结果

![图 11：代表时间步体绘制对比图](../results/04_volume_render/volume_keyframes_compare.png)

图 11 展示 t=0000、0030、0060、0099 的体绘制结果。早期密度结构相对均匀，局部高密度结构不突出；中期开始出现局部聚集和丝状结构；后期高密度节点和宇宙网形态更加明显。该图回答了“如何展示三维密度演化”的问题，并与图 9 中 std、P99 等指标的变化相互印证。其局限是体绘制依赖传递函数，仍需 P99 筛选验证高亮区域是否具有统计意义。

### 4.7 本阶段小结

本阶段通过 MIP、体绘制、传递函数和梯度增强，将 Nyx 密度场从二维截面提升为三维空间结构表达。下一步需要验证体绘制中高亮结构是否对应统计意义上的高密度尾部。

## 5 高密度结构验证分析

### 5.1 为什么需要 P99 高密度筛选

体绘制能够展示“看起来像宇宙网”的结构，但视觉结果会受到传递函数影响。为了避免只依赖视觉判断，实验使用原始 density 的 P99 作为 top 1% 高密度阈值，提取极高密度体素并观察其空间分布。

### 5.2 Top 1% 高密度区域提取

P99 表示 99% 体素密度低于该值，P99 到 P100 区间对应密度最高的 1% 体素。实验对每个时间步计算 P99 阈值，生成三维 mask，并统计被选体素数量和比例。

### 5.3 X/Y/Z 空间投影

![图 12：Top 1% 高密度筛选图](../results/report_figures/combined_top1_percent_mips.png)

图 12 展示代表时间步 top 1% 高密度体素的空间投影。P99 以上体素并非随机散布，而是集中于高密度节点和丝状结构交汇区域。该图直接验证直方图右侧尾部具有空间结构意义，并与体绘制中后期节点增强现象相互印证。其局限是 MIP 会丢失深度关系，因此还需要等值面和交互视图辅助。

### 5.4 P90/P95/P99 多阈值等值面

![图 13：多阈值等值面图](../results/05_high_density/nested_isosurfaces_t0099.png)

图 13 展示 P90、P95、P99 三个阈值的嵌套等值面。P90 覆盖较大范围的中高密度丝状外壳，P95 更集中，P99 只保留最致密节点。该图说明密度结构具有层级性：从大尺度丝状区域逐渐收缩到高密度核心。其局限是等值面结果对阈值选择敏感，因此需要结合结构指标和交互刷选分析。

### 5.5 结构指标与差分 MIP

![图 14：首末时间步差分 MIP](../results/06_structure_metrics/difference_mip_first_last.png)

图 14 展示最后时间步与第一个时间步的 log-density 差分 MIP。正值区域表示密度增强，负值区域表示相对降低。该图用于观察哪些区域在演化中变得更致密，哪些区域可能形成低密度空洞。它与 P99/mean、P99-P01、entropy、Gini 等结构指标共同说明密度分布逐渐分化。局限是差分 MIP 同样会压缩深度信息。

### 5.6 高密度尾部与宇宙网节点的对应关系

综合图 7、图 12 和图 13 可以看到，直方图右尾增强并不是单纯数值噪声，而是在空间中表现为高密度节点和丝状结构交汇区域。P99 top 1% 筛选将统计尾部与空间结构联系起来，是本项目回答赛题中“极高密度区间筛选与空间联动”的关键环节。

### 5.7 本阶段小结

本阶段从“看起来像宇宙网”推进到“统计阈值验证宇宙网节点”。P99 mask、多阈值等值面和差分 MIP 共同说明高密度尾部具有明确空间结构意义。

## 6 相空间交互式刷选分析

### 6.1 静态图像分析的局限

静态图只能展示预设时间步和预设阈值，无法让用户自由探索不同密度区间。为了建立统计分布与空间结构之间的双向关联，实验实现 linked brushing 仪表盘。

### 6.2 linked brushing 仪表盘设计

![图 15：交互式刷选仪表盘截图](../results/07_dashboard/dashboard_preview.png)

图 15 展示 MATLAB linked brushing dashboard。界面左侧为当前时间步 log-density histogram，右侧为空间投影视图。用户调整时间步、密度百分位区间、投影方向和显示模式后，直方图、mask 和空间视图同步更新。该图说明交互系统不是单纯展示最终结果，而是用于探索“某个密度区间在哪里”。其局限是 MATLAB GUI 依赖 MATLAB 环境，答辩展示迁移性较弱。

### 6.3 密度直方图刷选

直方图刷选允许用户从统计分布中选择密度范围。选择低密度区间时，空间投影更容易显示背景或空洞区域；选择中密度区间时，更容易观察连续丝状结构；选择高密度区间时，投影集中于节点和团块。该操作将统计图从“被动展示”转为“主动查询”。

### 6.4 空间视图联动

刷选区间变化后，系统实时生成 mask 并更新空间投影。这样用户可以从 histogram 中选择一个数值区间，再立即看到该区间在三维空间中的位置，实现统计特征和空间结构之间的双向联动。

### 6.5 Top 1% 高密度交互验证

当用户将密度区间设置为 99%-100% 时，仪表盘显示 top 1% 高密度体素。若这些体素集中在丝状结构交汇处和节点区域，则说明直方图右尾对应宇宙网致密结构。该交互过程是对图 12 静态 P99 结果的动态验证。

### 6.6 本阶段小结

本阶段将静态结果展示升级为可探索分析。linked brushing 的核心价值在于让用户从统计分布出发定位空间结构，也可以从空间结构反推对应密度区间。

## 7 Web 最终交互式可视化作品

### 7.1 为什么需要 Web 展示系统

MATLAB 图像和静态报告适合整理实验结果，但答辩现场需要更直观、更易运行的交互展示。因此项目进一步构建 `Nyx_Web_Visualization/` HTML 单页系统，将离线分析结果转化为可播放、可刷选、可联动的最终可视化作品。

### 7.2 Web 数据预处理与轻量化

由于浏览器不适合直接加载完整 100 帧 128×128×128 原始体数据，项目使用 `preprocess_for_web.py` 将 `.dat` 转换为轻量 Web 数据。脚本生成 `metadata.json`、`density_stats.json`、`histograms.json`、`time_density_heatmap.json`、`time_similarity_stage.json`，以及降采样后的 `vol_0000.bin` 至 `vol_0099.bin`。每个体数据默认为 64×64×64 Float32Array，浏览器端按时间步懒加载。

![图 16：Nyx Web 交互展示系统概览图](../results/report_figures/web_system_overview.png)

图 16 展示 Web 系统的数据流。原始 Nyx 数据经过预处理变成轻量体数据和 JSON 统计文件，再由浏览器端按需读取。该图说明 Web 作品不是直接读取原始大体数据，而是建立在离线预处理和懒加载策略之上。其局限是 Web 端使用降采样体数据，适合展示和探索，不替代原始分辨率分析。

### 7.3 HTML 页面结构设计

Web 页面包括顶部项目说明、左侧控制面板、中央空间视图、右侧 log-density histogram、底部 time-density heatmap、统计指标曲线和结论卡片。整体采用深色宇宙主题，适合课堂展示和录屏答辩。

![图 17：Nyx Density Explorer Web 最终交互式可视化系统运行截图](../results/report_figures/web_dashboard_actual_screenshot.png)

图 17 展示 Web 页面在浏览器中运行后的实际界面。中央空间视图用于显示 MIP、Mask、Slice 或简化体合成；右侧直方图用于 brush；底部 heatmap 和指标曲线用于时序分析。该图体现最终作品的界面组织方式和默认交互状态，但具体的时间播放、histogram brush 和视图切换仍需在浏览器中运行体验。

### 7.4 时间步播放与空间视图联动

用户拖动 time slider 或点击 Play/Pause 后，Web 页面会加载对应 `vol_xxxx.bin`，更新空间视图、直方图、统计指标和阶段标签。该交互用于展示宇宙密度场随时间从相对均匀到结构增强的过程。

### 7.5 histogram brush 与 Top 1% 一键筛选

用户可通过 density percentile slider 或 histogram brush 选择密度区间。默认 99%-100% 对应 top 1% 高密度体素。系统根据当前体数据计算百分位阈值，生成 mask，并在空间视图中显示被选区域。

### 7.6 time-density heatmap 与统计曲线联动

Web 页面底部提供 time-density heatmap 和统计指标曲线。点击 heatmap 或曲线上的时间位置，会同步切换主视图时间步。这使用户可以从全局时序趋势快速跳转到具体空间结构。

### 7.7 Web 作品答辩演示流程

答辩时可以先打开首页介绍 Nyx 数据，再展示迭代路线图，随后点击 Play 播放演化过程；切换 t=0000、0030、0060、0099 对比结构变化；将 density range 设为 99%-100% 展示 top 1% 高密度体素；切换 X/Y/Z 方向验证高密度体素是否集中于节点和丝状交汇区域；最后展示 heatmap、统计曲线和结论卡片，说明统计分布与空间结构的对应关系。

### 7.8 本阶段小结

Web 系统使最终作品从静态报告升级为可交互展示的科学可视化系统。它直接对应赛题中相空间刷选和空间联动展示的要求，也提高了课程答辩的可演示性。

## 8 进阶可视分析扩展

### 8.1 density-gradient 二维相空间

![图 18：density-gradient 二维相空间对比图](../results/report_figures/density_gradient_phase_compare.png)

图 18 将 normalized log-density 与 gradient magnitude 组成二维相空间。低密度低梯度区域通常对应背景或空洞，高梯度区域对应结构边界，高密度低梯度区域可能对应致密核心。该图扩展了一维 density brush，使用户能够区分边界和核心。其局限是二维相空间仍需要空间投影辅助解释。

### 8.2 Hessian Void / Sheet / Filament / Node 分类

![图 19：Hessian 宇宙网分类切片对比图](../results/report_figures/hessian_class_slice_compare.png)

图 19 使用 Hessian 特征值对局部结构进行 Void、Sheet、Filament、Node 粗分类。该方法不只关注极高密度体素，也尝试识别中密度连续结构。它补充了体绘制和 P99 筛选，但分类结果依赖平滑尺度和阈值，不应视为严格天体物理分类。

![图 20：Hessian 结构占比曲线](../results/report_figures/hessian_class_fraction_curve.png)

图 20 展示不同结构类别占比随时间变化。若 Filament 或 Node 相关比例和空间连续性增强，可与体绘制中的宇宙网结构相互印证。其局限是不同参数会影响类别占比。

### 8.3 时间步相似性矩阵与演化阶段划分

![图 21：时间步相似性矩阵](../results/report_figures/time_step_similarity_matrix.png)

图 21 将每个时间步的 log-density histogram 看作向量，计算时间步之间的 cosine similarity。矩阵对角线附近相似度较高，说明相邻时间步连续变化；若出现块状结构，则说明演化过程可以粗略划分阶段。该图为代表时间步选择提供数据依据，但它基于统计分布，不包含完整空间对应关系。

![图 22：演化阶段划分图](../results/report_figures/evolution_stage_segmentation.png)

图 22 根据 distance from start 将时间序列划分为 Early、Transition、Structure Enhancement 和 Late 等阶段。该图使 t=0000、0030、0060、0099 等代表帧选择更有依据。其局限是阶段划分是课程实验中的可解释近似，而不是严格物理分期。

### 8.4 进阶模块与基础方法的关系

进阶模块不是替代基础方法，而是对基础流程的深化。density-gradient 相空间扩展了 brush 维度，Hessian 分类补充结构识别，时间相似性矩阵组织时序阶段。它们共同增强了项目的分析深度。

## 9 实验结果综合分析

### 9.1 密度分布从集中到分化的演化特征

直方图和 time-density heatmap 显示，早期 log-density 分布较集中，随着时间推进分布逐渐扩散。统计曲线中的 std、P99 和 P99-P01 也支持这一观察，说明密度场从相对均匀逐渐走向分化。

### 9.2 高密度尾部增强与团块化趋势

P99、P99/mean 和 max density 的变化反映高密度尾部增强。体绘制中后期高亮节点增加，P99 mask 中高密度体素更加集中，说明统计尾部增强与空间团块化趋势相互印证。

### 9.3 空洞、丝状结构和节点的形成特征

体绘制和多阈值等值面显示，后期密度场中出现更明显的丝状结构和节点。差分 MIP 显示部分区域密度增强，部分区域相对降低，说明低密度空洞和高密度结构逐渐分化。

### 9.4 统计分布与空间结构的双向关联

本项目最重要的分析链条是：直方图显示高密度右尾，P99 mask 提取右尾体素，MIP 和等值面显示其空间位置，linked brushing 和 Web histogram brush 允许用户交互验证该对应关系。由此，统计分布不再是脱离空间的曲线，而是可以回到三维空间中解释。

### 9.5 可视化技术在宇宙学数据分析中的应用价值

体绘制负责三维结构感知，统计图负责数值分布分析，MIP 和等值面负责空间定位，交互刷选负责探索验证，Web 系统负责最终展示和答辩演示。它们共同体现科学可视化在高维时序体数据理解中的价值。

## 10 实验过程反思与总结

### 10.1 从无到有的开发路线

项目从不可直接查看的二进制数据开始，逐步完成数据恢复、读取验证、全时序统计、体绘制、高密度验证、交互刷选、进阶结构识别和 Web 展示。每一步都针对前一阶段的不足继续改进，最终形成完整可视分析链条。

### 10.2 实验过程中遇到的问题与解决方法

表 2 总结了实验过程中的主要问题和解决方法。

表 2：实验过程中遇到的问题与解决方法

| 遇到的问题 | 产生原因 | 解决方法 | 对应模块 |
|---|---|---|---|
| `.dat` 文件无法直接查看 | 原始数据为二进制体数据 | little-endian float32 读取 | `read_nyx_dat.m` |
| 无法确认轴顺序是否正确 | 原始数据按 z-y-x 顺序存储 | 中心切片验证 | `step1_check_data.m` |
| 原始 density 动态范围大 | 高密度值压缩中低密度结构 | log-density + 百分位归一化 | `normalize_percentile.m` |
| 二维切片空间信息不足 | 体数据具有三维结构 | MIP 和体绘制 | `step4_volume_render_keyframes.m` |
| 体绘制结果缺少统计依据 | 传递函数会影响视觉效果 | P99 mask、统计曲线、结构指标 | `step5`、`step6` |
| 静态图无法灵活探索 | 固定时间步和固定阈值 | linked brushing 仪表盘 | `step7_interactive_dashboard.m` |
| MATLAB GUI 不便于答辩展示 | 依赖 MATLAB 环境，现场操作不方便 | HTML Web 展示系统 | `Nyx_Web_Visualization/` |
| 浏览器加载完整体数据会卡顿 | 原始 100 帧体数据体量大 | Python 预处理、降采样、懒加载 | `preprocess_for_web.py` |

### 10.3 当前系统优势

当前系统覆盖数据读取、统计分析、三维空间可视化、结构验证、交互刷选、进阶分析和 Web 展示。它既能生成报告图，也能在浏览器中进行答辩演示，具有较好的完整性和可复现性。

### 10.4 当前系统局限

体绘制主要为固定方向合成，缺少自由三维旋转；MIP 会丢失深度信息；Hessian 分类依赖平滑尺度和阈值；Web 端使用降采样体数据和 CPU Canvas 简化渲染，不能替代原始分辨率分析；当前分析主要基于 density 单变量，尚未结合 velocity、temperature 等变量。

### 10.5 后续扩展方向

后续可以引入 WebGL 或 Three.js 实现真正可旋转的体绘制；加入 density-gradient 二维传递函数刷选；结合速度、温度等多变量数据；使用更稳健的拓扑或多尺度方法分析宇宙网结构。

## 11 结论

第一，关于“如何展示密度信息变化”，本实验使用 log-density 压缩动态范围，通过体绘制展示三维结构，通过 time-density heatmap 和统计曲线展示全时间步分布变化，并在 Web 页面中通过 time slider 和 Play/Pause 播放密度场演化。

第二，关于“宇宙密度演化有什么可视化特征”，实验观察到早期密度分布相对集中，后期密度波动增强，高密度尾部逐渐拉长，低密度空洞与高密度节点逐渐分化，丝状结构和团块化特征增强。

第三，关于“高密度尾部是否有空间意义”，P99 top 1% 体素在空间中并非随机分布，而是集中在丝状结构交汇处和节点区域，说明 log-density 直方图右侧高密度尾部与宇宙网致密结构存在对应关系。

第四，关于“相空间刷选有什么作用”，linked brushing 和 Web histogram brush 允许用户从统计直方图选择密度区间，并实时查看对应空间位置，实现统计特征与空间结构的双向关联。选择 99%-100% 区间时，系统可以直接验证 top 1% 高密度区域的空间分布。

第五，关于“可视化技术有什么应用价值”，体绘制负责三维结构感知，统计图负责数值分布分析，MIP 和等值面负责空间定位，交互刷选负责探索验证，Web 系统负责最终展示和答辩演示。综合这些方法，本实验形成了从 Nyx 二进制数据恢复到最终 HTML 交互作品的完整科学可视化流程。需要强调的是，本文结论用于数据可视化课程实验展示，不作为正式天体物理科学结论。

## 附录：核心代码与运行说明

Code Listing 1：Nyx 二进制体数据读取核心代码  
对应模块：`read_nyx_dat.m` / `infer_grid_size.m`

```matlab
fid = fopen(filename, 'r', 'ieee-le');
data = fread(fid, inf, 'single=>single');
fclose(fid);
n = infer_grid_size(numel(data));
Vzyx = reshape(data, [n, n, n]);
V = permute(Vzyx, [3, 2, 1]);
```

Code Listing 2：log-density 与百分位归一化核心代码  
对应模块：`normalize_percentile.m`

```matlab
logV = log10(max(V, eps('single')));
Vn = normalize_percentile(logV, 5, 99.7);
```

Code Listing 3：P99 高密度筛选核心代码  
对应模块：`step5_high_density_selection.m`

```matlab
threshold = prctile(double(V(:)), 99);
mask = V >= threshold;
selectedRatio = nnz(mask) / numel(mask);
```

Code Listing 4：Web 体数据预处理核心代码  
对应模块：`Nyx_Web_Visualization/scripts/preprocess_for_web.py`

```python
density = read_nyx_dat(path)
log_v = np.log10(np.maximum(density, EPS)).astype(np.float32)
norm_v, low, high = normalize_percentile(log_v, 5, 99.7)
small = downsample_volume(norm_v, target_size)
small.astype("<f4", copy=False).tofile(volume_dir / f"vol_{t:04d}.bin")
```

Code Listing 5：Web 端体数据懒加载核心代码  
对应模块：`Nyx_Web_Visualization/web/app.js`

```javascript
async function loadVolume(timeIndex) {
  if (state.volumeCache.has(timeIndex)) return state.volumeCache.get(timeIndex);
  const step = state.metadata.steps[timeIndex];
  const res = await fetch(DATA_BASE + step.volume_file);
  const volume = new Float32Array(await res.arrayBuffer());
  state.volumeCache.set(timeIndex, volume);
  return volume;
}
```

运行 Web 展示系统：

```bash
python scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
python start_nyx_web_demo.py
```

也可以直接双击：

```text
start_nyx_web_demo.bat
```
"""


def code_markdown() -> str:
    return r"""# Nyx 宇宙密度演化可视分析代码说明：Web 展示最终版

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
"""


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    create_iteration_roadmap(FIG_DIR / "iteration_roadmap.png")
    create_web_system_overview(FIG_DIR / "web_system_overview.png")
    create_web_dashboard_preview(FIG_DIR / "web_dashboard_preview_generated.png")

    report_md = REPORT_DIR / "大作业技术报告_最终优化版.md"
    code_md = REPORT_DIR / "代码说明_Web展示最终版.md"
    report_md.write_text(report_markdown(), encoding="utf-8")
    code_md.write_text(code_markdown(), encoding="utf-8")

    add_markdown_to_docx(
        report_md,
        REPORT_DIR / "Nyx宇宙密度演化可视分析_技术报告_最终优化版.docx",
    )
    add_markdown_to_docx(
        code_md,
        REPORT_DIR / "Nyx宇宙密度演化可视分析_代码说明_Web展示最终版.docx",
    )

    print("已生成最终优化版文档：")
    print(report_md.relative_to(PROJECT_ROOT))
    print(code_md.relative_to(PROJECT_ROOT))
    print((REPORT_DIR / "Nyx宇宙密度演化可视分析_技术报告_最终优化版.docx").relative_to(PROJECT_ROOT))
    print((REPORT_DIR / "Nyx宇宙密度演化可视分析_代码说明_Web展示最终版.docx").relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
