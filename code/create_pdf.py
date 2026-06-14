from pathlib import Path
import csv

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "report"
RESULTS_DIR = ROOT / "results"
STORY_DIR = RESULTS_DIR / "07_visual_story"
PROCESSED_DIR = ROOT / "data" / "processed"
STATS_PATH = PROCESSED_DIR / "density_stats.csv"
METRICS_PATH = PROCESSED_DIR / "structure_metrics.csv"
FONT = "SimHei"


def setup_font():
    pdfmetrics.registerFont(TTFont(FONT, "C:/Windows/Fonts/simhei.ttf"))


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleCN", parent=base["Title"], fontName=FONT, fontSize=22, leading=31, alignment=TA_CENTER, spaceAfter=12),
        "subtitle": ParagraphStyle("SubtitleCN", parent=base["Normal"], fontName=FONT, fontSize=12, leading=19, alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=7),
        "h1": ParagraphStyle("H1CN", parent=base["Heading1"], fontName=FONT, fontSize=15.5, leading=22, textColor=colors.HexColor("#1A4470"), spaceBefore=8, spaceAfter=6),
        "h2": ParagraphStyle("H2CN", parent=base["Heading2"], fontName=FONT, fontSize=12.5, leading=18, textColor=colors.HexColor("#2E74B5"), spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("BodyCN", parent=base["BodyText"], fontName=FONT, fontSize=10.5, leading=16.2, firstLineIndent=18, spaceAfter=6),
        "plain": ParagraphStyle("PlainCN", parent=base["BodyText"], fontName=FONT, fontSize=10, leading=14.5, spaceAfter=4),
        "caption": ParagraphStyle("CaptionCN", parent=base["BodyText"], fontName=FONT, fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#666666"), spaceAfter=6),
        "toc": ParagraphStyle("TocCN", parent=base["BodyText"], fontName=FONT, fontSize=11, leading=18, spaceAfter=3),
        "bullet": ParagraphStyle("BulletCN", parent=base["BodyText"], fontName=FONT, fontSize=10.2, leading=15.5, leftIndent=12, firstLineIndent=-8, spaceAfter=4),
    }


def para(text, sty):
    return Paragraph(text, sty["body"])


def bullet(text, sty):
    return Paragraph("• " + text, sty["bullet"])


def table(data, col_widths=None):
    if col_widths is None:
        usable = 174 * mm
        col_widths = [usable / len(data[0])] * len(data[0])
    wrapped = [[Paragraph(str(cell), styles()["plain"]) for cell in row] for row in data]
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), FONT),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7DEE8")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def image(path, caption, sty, width=165 * mm):
    path = Path(path)
    if not path.exists():
        return []
    with PILImage.open(path) as im:
        ratio = im.height / im.width
    return [Image(str(path), width=width, height=width * ratio), Paragraph(caption, sty["caption"])]


def build_report_pdf():
    sty = styles()
    stats = read_csv(STATS_PATH)
    metrics = read_csv(METRICS_PATH)
    first, mid, last = stats[0], stats[49], stats[-1]
    mf, mmid, ml = metrics[0], metrics[49], metrics[-1]

    story = [
        Spacer(1, 34 * mm),
        Paragraph("数据可视化课程大作业实验报告", sty["title"]),
        Paragraph("赛题 II：科学可视化挑战赛", sty["subtitle"]),
        Paragraph("Nyx 宇宙学模拟密度场可视分析", sty["subtitle"]),
        Paragraph("作品主题：从暗雾到宇宙网骨架", sty["subtitle"]),
        Paragraph("联合制作软件：MATLAB R2024b + Python + FFmpeg", sty["subtitle"]),
        Paragraph("报告结构参考往期优秀模板：封面、目录、环境、方法、结果、创新与总结", sty["subtitle"]),
        PageBreak(),
        Paragraph("目录", sty["h1"]),
    ]
    for item in [
        "1 赛题理解与作品定位",
        "2 多软件联合制作流程",
        "3 数据读取、质量检查与预处理",
        "4 体绘制方案：传递函数、光照与视觉编码",
        "5 宇宙网视觉叙事：从暗雾到骨架",
        "6 时序统计：100 步密度分布如何偏移",
        "7 相空间交互刷选：从统计尾部回到空间结构",
        "8 演示视频、作品创新点与提交说明",
        "9 总结、局限与进一步改进",
    ]:
        story.append(Paragraph(item, sty["toc"]))

    story += [
        PageBreak(),
        Paragraph("1 赛题理解与作品定位", sty["h1"]),
        para("本作品选择赛题 II：科学可视化挑战赛。Nyx 数据描述宇宙学模拟中气体密度随时间的演化，核心问题不是简单画出一张漂亮图片，而是把三维标量场、时间序列统计和可交互阈值筛选连接起来。", sty),
        para("我将作品定位为一个“宇宙网形成观测台”：第一层通过体绘制观察空间形态，第二层通过 100 个时间步统计曲线观察分布迁移，第三层通过相空间刷选验证高密度尾部是否对应真实的三维节点结构。", sty),
        para("视觉叙事上，报告把宇宙密度演化概括为四个阶段：暗雾、丝束、节点、空洞。暗雾代表早期近均匀背景；丝束代表物质被引力牵引形成连续结构；节点代表高密度峰值抬升；空洞代表低密度区域在结构分化中扩张。", sty),
        Paragraph("2 多软件联合制作流程", sty["h1"]),
        table([
            ["软件/工具", "承担任务", "形成成果"],
            ["MATLAB R2024b", "体数据读取、统计计算、体绘制、直方图、相空间交互仪表盘", "PNG 图像、CSV/MAT 统计文件、interactive_dashboard.m"],
            ["Python + Pillow", "基于 MATLAB 输出二次视觉设计，生成图谱、热力图、指标仪表盘、视频帧", "07_visual_story 作品图谱"],
            ["Python + python-docx / ReportLab", "自动生成 DOCX 与 PDF 报告，保证报告和数据结果同步", "技术报告、Answer Sheet"],
            ["FFmpeg", "将 100 帧数据驱动分镜合成为演示视频", "video/demo.mp4"],
        ], [34 * mm, 72 * mm, 68 * mm]),
        Spacer(1, 5 * mm),
        para("与单一软件截图不同，本项目让 MATLAB 负责科学计算与交互，Python 负责视觉叙事包装与文档生成，FFmpeg 负责视频化展示。三者形成从数据、图像、报告到视频的制作链路。", sty),
    ]
    story += image(RESULTS_DIR / "06_python_summary" / "software_workflow_summary.png", "图 1  MATLAB + Python 联合制作流程与结果汇总", sty, 170 * mm)

    story += [
        PageBreak(),
        Paragraph("3 数据读取、质量检查与预处理", sty["h1"]),
        para("每个 Nyx 文件以 little-endian float32 保存，大小为 8,388,608 字节，对应 128×128×128 个体素。题目说明数据线性顺序为先 z、再 y、最后 x，因此读取时先 reshape 为 z-y-x，再转换为 x-y-z 空间。", sty),
        para("数据预处理坚持“只用给定数据”。没有引入任何外部天文数据或纹理。所有图像、曲线和视频帧都来自 data/raw 中 100 个时间步。为了让高密度峰值与主体分布同时可见，对密度采用 log10 动态范围压缩。", sty),
    ]
    story += image(RESULTS_DIR / "01_data_check" / "slice_0000.png", "图 2  t0000 中央切片质量检查：密度场连续，无明显读取错位", sty, 135 * mm)
    story += [
        Paragraph("4 体绘制方案：传递函数、光照与视觉编码", sty["h1"]),
        para("体绘制采用前向 alpha 合成。传递函数的关键思想是：低密度空洞不完全隐藏，而是以深色暗雾保留背景；中等密度结构用青蓝色显示连续丝束；极高密度节点用金色到暖白色突出。", sty),
        para("光照并不追求真实天文照明，而是使用梯度幅值近似“结构边界强度”。密度变化越剧烈的区域越亮，视觉上更容易识别空洞边界、丝状结构和团块节点。", sty),
    ]
    story += image(STORY_DIR / "transfer_function_design.png", "图 3  传递函数设计图：颜色、透明度与梯度光照的联合编码", sty, 170 * mm)

    story += [
        PageBreak(),
        Paragraph("5 宇宙网视觉叙事：从暗雾到骨架", sty["h1"]),
        para("优秀的科学可视化不只是把数据画出来，还要让读者看到数据背后的过程。因此我额外制作了“宇宙网演化图谱”，用同一视觉语法比较 t0000、t0030、t0060、t0099 四个代表时间步。", sty),
        para("图谱显示早期物质分布像弥散暗雾，之后沿引力势阱被拉成丝束，最终高密度节点逐渐发亮，低密度区域退成大尺度空洞。这个过程与宇宙大尺度结构形成的基本图景一致。", sty),
    ]
    story += image(STORY_DIR / "cosmic_web_atlas.png", "图 4  Nyx 宇宙网演化图谱：从暗雾到骨架", sty, 170 * mm)
    story += image(RESULTS_DIR / "02_volume_render" / "volume_t0000.png", "图 5  t0000 体绘制：密度背景较均匀，结构边界较弱", sty, 130 * mm)
    story += image(RESULTS_DIR / "02_volume_render" / "volume_t0099.png", "图 6  t0099 体绘制：高密度节点和丝状连接更加突出", sty, 130 * mm)

    story += [
        PageBreak(),
        Paragraph("6 时序统计：100 步密度分布如何偏移", sty["h1"]),
        table([
            ["指标", "t0000", "t0049", "t0099", "变化含义"],
            ["均值", f"{float(first['mean_density']):.4f}", f"{float(mid['mean_density']):.4f}", f"{float(last['mean_density']):.4f}", "全域平均密度缓慢变化"],
            ["标准差", f"{float(first['std_density']):.4f}", f"{float(mid['std_density']):.4f}", f"{float(last['std_density']):.4f}", "密度波动增强"],
            ["最大值", f"{float(first['max_density']):.4f}", f"{float(mid['max_density']):.4f}", f"{float(last['max_density']):.4f}", "高密度峰值抬升"],
            ["P99-P01", f"{float(mf['spread_p99_p01']):.4f}", f"{float(mmid['spread_p99_p01']):.4f}", f"{float(ml['spread_p99_p01']):.4f}", "分布跨度增大"],
            ["低密度空洞占比", f"{float(mf['void_fraction_vs_t0000_p05'])*100:.2f}%", f"{float(mmid['void_fraction_vs_t0000_p05'])*100:.2f}%", f"{float(ml['void_fraction_vs_t0000_p05'])*100:.2f}%", "相对早期阈值的空洞扩张"],
        ], [28 * mm, 25 * mm, 25 * mm, 25 * mm, 71 * mm]),
        Spacer(1, 5 * mm),
        para(f"从统计量看，标准差由 {float(first['std_density']):.4f} 增加到 {float(last['std_density']):.4f}，最大密度由 {float(first['max_density']):.4f} 增加到 {float(last['max_density']):.4f}。这说明演化后期物质分布更不均匀，极端高密度区域更强。", sty),
    ]
    story += image(STORY_DIR / "structure_metrics_dashboard.png", "图 7  结构形成统计指纹：波动、峰值、空洞占比和分布复杂度", sty, 170 * mm)
    story += [
        PageBreak(),
        para("热力图把 100 张直方图压缩到一张图里。横向看是时间推进，纵向看是密度区间。高密度尾部在后期保持并略微增强，低密度端也逐步展开，形成两极分化。", sty),
    ]
    story += image(STORY_DIR / "histogram_temporal_heatmap.png", "图 8  100 个时间步密度对数直方图热力图", sty, 170 * mm)

    story += [
        PageBreak(),
        Paragraph("7 相空间交互刷选：从统计尾部回到空间结构", sty["h1"]),
        para("交互仪表盘 interactive_dashboard.m 的目标是把统计空间和物理空间打通。用户在直方图中选择密度百分位区间，例如 99% 到 100% 的前 1% 高密度尾部，右侧三维空间视图会实时显示满足阈值的体素。", sty),
        para("这个设计回答了一个关键问题：直方图中的尾部数据到底是什么？结果表明，高密度尾部不是随机散点，而是集中出现在宇宙网节点与致密丝束附近。统计异常因此获得了空间物理解释。", sty),
    ]
    story += image(STORY_DIR / "interaction_storyboard.png", "图 9  相空间刷选故事板：从直方图尾部定位三维节点结构", sty, 170 * mm)
    story += image(RESULTS_DIR / "05_interaction_selection" / "top1_percent_t0099.png", "图 10  t0099 前 1% 高密度区域刷选结果", sty, 130 * mm)

    story += [
        PageBreak(),
        Paragraph("8 演示视频、作品创新点与提交说明", sty["h1"]),
        para("为了让宇宙演化过程更直观，项目额外生成 video/demo.mp4。视频不是图片轮播，而是逐帧读取 100 个原始时间步，在每一帧同时展示空间投影、当前统计指标和直方图热力图中的时间位置。", sty),
        bullet("创新点 1：同一套传递函数贯穿所有时间步，避免每张图单独调色导致的对比误差。", sty),
        bullet("创新点 2：用 100 步直方图热力图展示全域分布迁移，比只放 4 张直方图更完整。", sty),
        bullet("创新点 3：把前 1% 高密度尾部与三维空间结构联动，完成统计特征到物理结构的解释闭环。", sty),
        bullet("创新点 4：MATLAB、Python、FFmpeg 多软件协作，覆盖计算、交互、视觉叙事、报告和视频生成。", sty),
        para("最终提交包包含核心代码、处理数据、结果图、DOCX/PDF 报告、Answer Sheet 与演示视频。原始 data/raw 数据约 800MB，默认不重复放入 zip，避免超过课程电子材料大小限制。", sty),
        Paragraph("9 总结、局限与进一步改进", sty["h1"]),
        para("本项目用体绘制、统计曲线、时序热力图和交互刷选共同说明：Nyx 密度场在 100 个时间步内由相对均匀的分布逐步发展出更明显的高密度节点、丝状连接和低密度空洞。可视化技术的价值在于让抽象的三维标量场同时具备空间形态、统计证据和交互验证。", sty),
        para("局限性在于当前体绘制采用 CPU 前向合成与投影近似，未实现真正的 GPU 射线投射；交互仪表盘侧重密度阈值筛选，尚未加入温度、速度或暗物质粒子的多变量联动。后续可以加入 WebGL/Volume Viewer、等值面提取、连通域跟踪和节点生命周期分析。", sty),
    ]

    out = REPORT_DIR / "技术报告.pdf"
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm).build(story)
    return out


def build_answer_pdf():
    sty = styles()
    story = [
        Paragraph("Answer Sheet", sty["title"]),
        Paragraph("Nyx 科学可视化挑战赛", sty["subtitle"]),
        Paragraph("作品信息", sty["h1"]),
        table([
            ["项目", "内容"],
            ["赛题", "赛题 II：科学可视化挑战赛"],
            ["作品", "Nyx 宇宙学模拟密度场可视分析"],
            ["主题", "从暗雾到宇宙网骨架"],
            ["联合制作软件", "MATLAB R2024b + Python + FFmpeg"],
            ["核心成果", "体绘制、时序热力图、结构指标仪表盘、相空间交互刷选、演示视频"],
        ], [45 * mm, 120 * mm]),
        Spacer(1, 5 * mm),
        Paragraph("提交清单", sty["h1"]),
    ]
    for item in [
        "code：MATLAB 主程序、交互仪表盘、Python 视觉故事/报告/视频生成脚本。",
        "results：体绘制、直方图、统计曲线、高密度刷选、联合流程图、视觉故事图谱。",
        "data/processed：density_stats.csv、high_density_threshold.csv、structure_metrics.csv、statistics.mat。",
        "report：技术报告 DOCX/PDF 与 Answer Sheet DOCX/PDF。",
        "video：demo.mp4 演示视频。",
    ]:
        story.append(bullet(item, sty))
    out = REPORT_DIR / "Answer_Sheet.pdf"
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm).build(story)
    return out


if __name__ == "__main__":
    setup_font()
    print(build_report_pdf())
    print(build_answer_pdf())
