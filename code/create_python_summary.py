from pathlib import Path
import csv

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUT_DIR = RESULTS / "06_python_summary"
STATS = ROOT / "data" / "processed" / "density_stats.csv"


def font(size, bold=False):
    path = "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc"
    return ImageFont.truetype(path, size)


def load_stats():
    with STATS.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows[0], rows[-1]


def fit_image(path, size):
    img = Image.open(path).convert("RGB")
    img.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (248, 250, 252))
    x = (size[0] - img.width) // 2
    y = (size[1] - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def card(draw, xy, title, body):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=10, fill=(255, 255, 255), outline=(210, 218, 230), width=2)
    draw.text((x0 + 18, y0 + 14), title, font=font(28, True), fill=(25, 53, 90))
    draw.multiline_text((x0 + 18, y0 + 58), body, font=font(21), fill=(58, 67, 82), spacing=8)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    first, last = load_stats()

    canvas = Image.new("RGB", (1800, 1200), (242, 246, 251))
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 36), "Nyx 科学可视化联合制作流程与结果汇总", font=font(44, True), fill=(14, 37, 67))
    draw.text((60, 96), "MATLAB 负责体数据读取、渲染、统计与交互；Python 负责结果汇总、报告排版、PDF 生成与提交归档。", font=font(24), fill=(72, 80, 92))

    card(draw, (60, 150, 520, 350), "软件 1：MATLAB R2024b",
         "• little-endian float32 读取\n• 128×128×128 体数据重建\n• 传递函数与梯度光照体绘制\n• 相空间刷选仪表盘")
    card(draw, (560, 150, 1020, 350), "软件 2：Python",
         "• 读取统计 CSV\n• 拼接结果总览图\n• python-docx 生成 DOCX\n• ReportLab 生成 PDF 与提交包")
    card(draw, (1060, 150, 1740, 350), "关键统计变化",
         f"t0000 标准差：{float(first['std_density']):.4f}\n"
         f"t0099 标准差：{float(last['std_density']):.4f}\n"
         f"t0000 最大密度：{float(first['max_density']):.4f}\n"
         f"t0099 最大密度：{float(last['max_density']):.4f}")

    image_slots = [
        (RESULTS / "02_volume_render" / "volume_t0000.png", "t0000 体绘制", (60, 410)),
        (RESULTS / "02_volume_render" / "volume_t0099.png", "t0099 体绘制", (650, 410)),
        (RESULTS / "04_statistics" / "percentile_curve.png", "分位数演化", (1240, 410)),
        (RESULTS / "05_interaction_selection" / "top1_percent_t0099.png", "前 1% 高密度刷选", (650, 810)),
    ]
    for path, title, pos in image_slots:
        x, y = pos
        draw.rounded_rectangle((x, y, x + 500, y + 330), radius=8, fill=(255, 255, 255), outline=(211, 218, 230), width=2)
        img = fit_image(path, (470, 250))
        canvas.paste(img, (x + 15, y + 18))
        draw.text((x + 20, y + 282), title, font=font(22, True), fill=(35, 63, 98))

    draw.line((520, 250, 560, 250), fill=(37, 99, 160), width=5)
    draw.line((1020, 250, 1060, 250), fill=(37, 99, 160), width=5)
    draw.text((60, 1120), "图：由 Python/Pillow 基于 MATLAB 输出结果二次整合，用于说明多软件联合制作流程。", font=font(22), fill=(80, 89, 105))

    out = OUT_DIR / "software_workflow_summary.png"
    canvas.save(out)
    print(out)


if __name__ == "__main__":
    main()
