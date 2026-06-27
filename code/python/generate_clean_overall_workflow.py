# -*- coding: utf-8 -*-
"""重新生成箭头更规整的 Nyx 总体流程图。"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path as MplPath


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_FILE = PROJECT_ROOT / "results" / "report_figures" / "overall_workflow.png"


def get_fonts() -> tuple[FontProperties, FontProperties]:
    font_path = Path("C:/Windows/Fonts/msyh.ttc")
    if not font_path.exists():
        font_path = Path("C:/Windows/Fonts/simhei.ttf")
    return FontProperties(fname=str(font_path)), FontProperties(fname=str(font_path), weight="bold")


def box(ax, x, y, w, h, text, face, edge, font, bold_font, size=10.5):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.35,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=size,
        color="#172235",
        linespacing=1.25,
        fontproperties=bold_font if "\n" not in text else font,
    )


def arrow(ax, pts, color="#314463", lw=1.55):
    """绘制折线箭头，箭头只出现在末端。"""
    codes = [MplPath.MOVETO] + [MplPath.LINETO] * (len(pts) - 1)
    path = MplPath(pts, codes)
    patch = FancyArrowPatch(
        path=path,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=lw,
        color=color,
        shrinkA=0,
        shrinkB=0,
        joinstyle="round",
        capstyle="round",
    )
    ax.add_patch(patch)


def main() -> None:
    font, bold = get_fonts()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(13.8, 7.4), dpi=300)
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    edge = "#344B6D"
    input_face = "#EAF2FB"
    norm_face = "#F1EEFF"
    route_face = "#FFF7E8"
    dash_face = "#EAFBF0"
    final_face = "#FFF1F1"

    ax.text(
        0.5,
        0.955,
        "Nyx 宇宙密度演化可视分析总体流程图",
        ha="center",
        va="center",
        fontsize=18,
        color="#17324D",
        fontproperties=bold,
    )

    # Top data recovery pipeline.
    top_y, top_h = 0.80, 0.075
    xs = [0.055, 0.295, 0.535, 0.775]
    ws = [0.18, 0.19, 0.18, 0.18]
    labels = [
        "Nyx .dat 原始数据",
        "little-endian float32 读取",
        "自动推断 n×n×n",
        "z-y-x 到 x-y-z 恢复",
    ]
    for x, w, label in zip(xs, ws, labels):
        box(ax, x, top_y, w, top_h, label, input_face, edge, font, bold, 10.2)

    for i in range(3):
        arrow(ax, [(xs[i] + ws[i] + 0.012, top_y + top_h / 2), (xs[i + 1] - 0.012, top_y + top_h / 2)])

    # Normalization.
    norm_x, norm_y, norm_w, norm_h = 0.34, 0.64, 0.32, 0.075
    box(ax, norm_x, norm_y, norm_w, norm_h, "log10 密度变换与百分位归一化", norm_face, edge, font, bold, 11.0)

    # Orthogonal connector from recovery pipeline to normalization.
    last_center = (xs[-1] + ws[-1] / 2, top_y)
    norm_top = (norm_x + norm_w / 2, norm_y + norm_h)
    arrow(ax, [last_center, (last_center[0], 0.755), (norm_top[0], 0.755), norm_top])

    # Three analysis routes.
    route_y, route_h, route_w = 0.405, 0.13, 0.275
    route_xs = [0.045, 0.3625, 0.68]
    route_labels = [
        "路线一：体绘制与传递函数设计\n输出：关键帧体绘制图、传递函数对比图",
        "路线二：统计分析与直方图热力图\n输出：统计曲线、histogram、heatmap",
        "路线三：高密度筛选与结构分析\n输出：P99 MIP、等值面、结构指标",
    ]
    for x, label in zip(route_xs, route_labels):
        box(ax, x, route_y, route_w, route_h, label, route_face, edge, font, bold, 9.4)

    norm_bottom = (norm_x + norm_w / 2, norm_y)
    junction_y = 0.585
    targets = [(route_xs[0] + route_w / 2, route_y + route_h),
               (route_xs[1] + route_w / 2, route_y + route_h),
               (route_xs[2] + route_w / 2, route_y + route_h)]
    for tx, ty in targets:
        arrow(ax, [norm_bottom, (norm_bottom[0], junction_y), (tx, junction_y), (tx, ty)])

    # Linked brushing summary.
    dash_x, dash_y, dash_w, dash_h = 0.295, 0.235, 0.41, 0.082
    box(ax, dash_x, dash_y, dash_w, dash_h, "交互式 linked brushing 仪表盘", dash_face, edge, font, bold, 11)

    route_bottom_y = route_y
    dash_top_y = dash_y + dash_h
    merge_y = 0.355
    dash_targets = [
        (dash_x + 0.08, dash_top_y),
        (dash_x + dash_w / 2, dash_top_y),
        (dash_x + dash_w - 0.08, dash_top_y),
    ]
    for source_x, target in zip([t[0] for t in targets], dash_targets):
        arrow(ax, [(source_x, route_bottom_y), (source_x, merge_y), (target[0], merge_y), target])

    # Final conclusion.
    final_x, final_y, final_w, final_h = 0.325, 0.08, 0.35, 0.082
    box(ax, final_x, final_y, final_w, final_h, "宇宙密度演化规律总结", final_face, edge, font, bold, 11)
    arrow(ax, [(dash_x + dash_w / 2, dash_y), (dash_x + dash_w / 2, final_y + final_h)])

    ax.text(
        0.5,
        0.025,
        "说明：箭头表示数据处理与分析结果的依赖关系，三条分析路线最终汇入交互式刷选与规律总结。",
        ha="center",
        va="center",
        fontsize=8.8,
        color="#5B677A",
        fontproperties=font,
    )

    fig.savefig(OUT_FILE, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(OUT_FILE)


if __name__ == "__main__":
    main()
