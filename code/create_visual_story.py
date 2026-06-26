from pathlib import Path
import csv
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
RESULTS_DIR = ROOT / "results"
STORY_DIR = RESULTS_DIR / "07_visual_story"
VIDEO_DIR = ROOT / "video"
FRAME_DIR = VIDEO_DIR / "frames"
FFMPEG = "ffmpeg"


def font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT = font(22)
FONT_B = font(28, True)
FONT_L = font(42, True)
FONT_S = font(16)


def text_width(draw, text, font_obj):
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    return bbox[2] - bbox[0]


def wrap_text(draw, text, font_obj, max_width):
    lines = []
    current = ""
    for char in text:
        candidate = current + char
        if current and text_width(draw, candidate, font_obj) > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def draw_wrapped_text(draw, xy, text, font_obj, fill, max_width, spacing=8):
    x, y = xy
    for line in wrap_text(draw, text, font_obj, max_width):
        draw.text((x, y), line, font=font_obj, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font_obj)
        y += bbox[3] - bbox[1] + spacing
    return y


def read_volume(index):
    path = RAW_DIR / f"{index:04d}.dat"
    raw = np.fromfile(path, dtype="<f4")
    n = round(raw.size ** (1 / 3))
    zyx = raw.reshape((n, n, n))
    return np.transpose(zyx, (2, 1, 0))


def color_lut(n=256):
    anchors_x = np.array([0.00, 0.18, 0.42, 0.68, 0.88, 1.00])
    anchors_c = np.array([
        [6, 10, 26],
        [16, 53, 96],
        [34, 139, 156],
        [239, 180, 70],
        [255, 108, 79],
        [255, 248, 214],
    ], dtype=np.float32)
    x = np.linspace(0, 1, n)
    lut = np.zeros((n, 3), dtype=np.uint8)
    for c in range(3):
        lut[:, c] = np.interp(x, anchors_x, anchors_c[:, c])
    return lut


LUT = color_lut()


def normalize_log(values, lo=None, hi=None):
    logv = np.log10(np.maximum(values.astype(np.float32), np.finfo(np.float32).eps))
    if lo is None:
        lo = np.percentile(logv, 2)
    if hi is None:
        hi = np.percentile(logv, 99.8)
    norm = np.clip((logv - lo) / max(hi - lo, 1e-6), 0, 1)
    return norm, logv


def projection_image(volume, size=(460, 460)):
    norm, _ = normalize_log(volume)
    proj = np.max(norm, axis=2)
    edge_y, edge_x = np.gradient(proj)
    shade = np.clip(0.72 + 1.2 * np.sqrt(edge_x * edge_x + edge_y * edge_y), 0, 1.35)
    idx = np.clip((proj * 255).astype(np.int32), 0, 255)
    rgb = LUT[idx].astype(np.float32) * shade[..., None]
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    return img.rotate(90, expand=True).resize(size, Image.Resampling.LANCZOS)


def read_stats():
    with (PROCESSED_DIR / "density_stats.csv").open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def raw_sequence_available():
    return all((RAW_DIR / f"{i:04d}.dat").is_file() and (RAW_DIR / f"{i:04d}.dat").stat().st_size > 0 for i in range(100))


def read_existing_metrics():
    metrics_path = PROCESSED_DIR / "structure_metrics.csv"
    if not metrics_path.exists():
        raise FileNotFoundError("Missing structure_metrics.csv and raw Nyx data; cannot rebuild visual story assets.")
    with metrics_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    metrics = []
    for row in rows:
        metrics.append({
            key: (int(value) if key == "time_index" else float(value) if key != "timestep" else value)
            for key, value in row.items()
        })
    return metrics


def compute_histograms_and_metrics():
    STORY_DIR.mkdir(parents=True, exist_ok=True)
    rows = read_stats()
    all_logs = []
    volumes_cache = {}
    for i in range(100):
        v = read_volume(i)
        if i in [0, 30, 60, 99]:
            volumes_cache[i] = v
        all_logs.append(np.log10(np.maximum(v.ravel(), np.finfo(np.float32).eps)))

    global_min = min(float(x.min()) for x in all_logs)
    global_max = max(float(x.max()) for x in all_logs)
    bins = np.linspace(global_min, global_max, 121)
    hist = np.vstack([np.histogram(x, bins=bins, density=True)[0] for x in all_logs])
    hist = hist / np.maximum(hist.max(axis=1, keepdims=True), 1e-9)

    base_p05 = float(rows[0]["p05_density"])
    base_p95 = float(rows[0]["p95_density"])
    metrics = []
    for i, (row, logs) in enumerate(zip(rows, all_logs)):
        values = np.power(10, logs)
        void_fraction = float(np.mean(values <= base_p05))
        dense_fraction = float(np.mean(values >= base_p95))
        entropy = float(-np.sum((hist[i] / hist[i].sum()) * np.log2((hist[i] / hist[i].sum()) + 1e-12)))
        metrics.append({
            "timestep": f"{i:04d}",
            "time_index": i,
            "std_density": float(row["std_density"]),
            "max_density": float(row["max_density"]),
            "p01_density": float(row["p01_density"]),
            "p99_density": float(row["p99_density"]),
            "spread_p99_p01": float(row["p99_density"]) - float(row["p01_density"]),
            "tail_amplification": float(row["p99_density"]) / float(row["mean_density"]),
            "void_fraction_vs_t0000_p05": void_fraction,
            "dense_fraction_vs_t0000_p95": dense_fraction,
            "log_density_entropy": entropy,
        })

    with (PROCESSED_DIR / "structure_metrics.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics[0].keys()))
        writer.writeheader()
        writer.writerows(metrics)

    return bins, hist, metrics, volumes_cache


def draw_heatmap(bins, hist):
    w, h = 1500, 860
    img = Image.new("RGB", (w, h), (246, 249, 252))
    draw = ImageDraw.Draw(img)
    draw.text((55, 35), "100 个时间步密度对数直方图热力图", font=FONT_L, fill=(16, 40, 72))
    draw.text((55, 90), "横轴为时间步，纵轴为 log10(density)。颜色越亮，表示该密度区间出现概率越高。", font=FONT, fill=(70, 80, 95))

    x0, y0, x1, y1 = 120, 155, 1420, 760
    draw.rectangle((x0, y0, x1, y1), fill=(14, 24, 44), outline=(170, 180, 195))
    for t in range(hist.shape[0]):
        for b in range(hist.shape[1]):
            v = hist[t, hist.shape[1] - 1 - b]
            color = tuple(LUT[min(255, int(v * 255))])
            xx0 = x0 + int(t / hist.shape[0] * (x1 - x0))
            xx1 = x0 + int((t + 1) / hist.shape[0] * (x1 - x0)) + 1
            yy0 = y0 + int(b / hist.shape[1] * (y1 - y0))
            yy1 = y0 + int((b + 1) / hist.shape[1] * (y1 - y0)) + 1
            draw.rectangle((xx0, yy0, xx1, yy1), fill=color)

    for t in [0, 25, 50, 75, 99]:
        x = x0 + int(t / 99 * (x1 - x0))
        draw.line((x, y1, x, y1 + 8), fill=(45, 55, 70), width=2)
        draw.text((x - 18, y1 + 14), str(t), font=FONT_S, fill=(45, 55, 70))
    for label, val in [("低密度", bins[0]), ("中位区", (bins[0] + bins[-1]) / 2), ("高密度", bins[-1])]:
        y = y1 - int((val - bins[0]) / (bins[-1] - bins[0]) * (y1 - y0))
        draw.text((30, y - 10), label, font=FONT_S, fill=(45, 55, 70))
    draw.text((680, 810), "Time step", font=FONT, fill=(45, 55, 70))
    draw.text((55, 120), "log10(density)", font=FONT_S, fill=(45, 55, 70))
    img.save(STORY_DIR / "histogram_temporal_heatmap.png")


def line_plot(draw, box, series, colors_, labels, title, y_label=""):
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=12, fill=(255, 255, 255), outline=(215, 222, 232), width=2)
    draw.text((x0 + 20, y0 + 14), title, font=FONT_B, fill=(24, 55, 92))
    plot = (x0 + 65, y0 + 70, x1 - 25, y1 - 50)
    px0, py0, px1, py1 = plot
    draw.rectangle(plot, outline=(210, 218, 230))
    vals = np.concatenate([np.asarray(s, dtype=float) for s in series])
    vmin, vmax = float(vals.min()), float(vals.max())
    pad = (vmax - vmin) * 0.08 + 1e-9
    vmin -= pad
    vmax += pad
    for k in range(5):
        y = py0 + int(k / 4 * (py1 - py0))
        draw.line((px0, y, px1, y), fill=(235, 239, 245))
    for s, col in zip(series, colors_):
        points = []
        for i, v in enumerate(s):
            x = px0 + int(i / (len(s) - 1) * (px1 - px0))
            y = py1 - int((float(v) - vmin) / (vmax - vmin) * (py1 - py0))
            points.append((x, y))
        draw.line(points, fill=col, width=4)
    lx = px0
    for label, col in zip(labels, colors_):
        draw.rectangle((lx, y1 - 34, lx + 18, y1 - 16), fill=col)
        draw.text((lx + 26, y1 - 38), label, font=FONT_S, fill=(55, 65, 80))
        lx += 170
    if y_label:
        draw.text((x0 + 16, py0 + 6), y_label, font=FONT_S, fill=(90, 98, 112))


def draw_metrics_dashboard(metrics):
    w, h = 1600, 1050
    img = Image.new("RGB", (w, h), (242, 246, 251))
    draw = ImageDraw.Draw(img)
    draw.text((60, 36), "宇宙结构形成的统计指纹", font=FONT_L, fill=(16, 40, 72))
    draw.text((60, 92), "从均匀背景到团块化宇宙网：用多指标追踪密度分布的扩散、尾部增强和空洞发展。", font=FONT, fill=(70, 80, 95))

    std = [m["std_density"] for m in metrics]
    maxd = [m["max_density"] for m in metrics]
    spread = [m["spread_p99_p01"] for m in metrics]
    void = [m["void_fraction_vs_t0000_p05"] for m in metrics]
    dense = [m["dense_fraction_vs_t0000_p95"] for m in metrics]
    entropy = [m["log_density_entropy"] for m in metrics]

    line_plot(draw, (60, 150, 760, 560), [std, spread], [(45, 118, 183), (234, 154, 53)], ["标准差", "P99-P01"], "密度波动幅度持续增大")
    line_plot(draw, (840, 150, 1540, 560), [maxd], [(218, 80, 74)], ["最大密度"], "高密度峰值不断抬升")
    line_plot(draw, (60, 610, 760, 1000), [void, dense], [(88, 145, 92), (141, 91, 168)], ["低密度空洞占比", "高密度单元占比"], "相对 t0000 阈值的两极化")
    line_plot(draw, (840, 610, 1540, 1000), [entropy], [(78, 121, 167)], ["log 密度熵"], "分布形态复杂度变化")
    img.save(STORY_DIR / "structure_metrics_dashboard.png")


def draw_transfer_function():
    w, h = 1500, 900
    img = Image.new("RGB", (w, h), (245, 248, 252))
    draw = ImageDraw.Draw(img)
    draw.text((65, 40), "传递函数设计：把看不见的密度差异翻译成可见结构", font=FONT_L, fill=(16, 40, 72))
    draw.text((65, 98), "低密度背景像暗雾，高密度丝状结构逐渐发光，极高密度节点以暖色突出。", font=FONT, fill=(70, 80, 95))

    x0, y0, x1, y1 = 120, 210, 1380, 320
    for i in range(x0, x1):
        t = (i - x0) / (x1 - x0)
        draw.line((i, y0, i, y1), fill=tuple(LUT[int(t * 255)]))
    draw.rectangle((x0, y0, x1, y1), outline=(170, 180, 195), width=2)
    draw.text((x0, y1 + 18), "低密度空洞", font=FONT, fill=(55, 65, 80))
    draw.text((660, y1 + 18), "丝状结构", font=FONT, fill=(55, 65, 80))
    draw.text((x1 - 130, y1 + 18), "团块节点", font=FONT, fill=(55, 65, 80))

    px0, py0, px1, py1 = 120, 470, 1380, 740
    draw.rectangle((px0, py0, px1, py1), fill=(255, 255, 255), outline=(210, 218, 230), width=2)
    opacity_points = []
    light_points = []
    for i in range(260):
        t = i / 259
        opacity = 0.02 * smoothstep(t, 0.20, 0.55) + 0.20 * smoothstep(t, 0.62, 0.95)
        light = 0.55 + 0.45 * smoothstep(t, 0.30, 0.90)
        x = px0 + int(t * (px1 - px0))
        opacity_points.append((x, py1 - int(opacity / 0.23 * (py1 - py0 - 30))))
        light_points.append((x, py1 - int((light - 0.5) / 0.55 * (py1 - py0 - 30))))
    draw.line(opacity_points, fill=(217, 83, 79), width=5)
    draw.line(light_points, fill=(45, 118, 183), width=5)
    draw.text((px0 + 20, py0 + 20), "红线：不透明度，蓝线：梯度光照增强", font=FONT, fill=(55, 65, 80))
    draw.text((px0 + 20, py1 + 18), "归一化 log10(density)", font=FONT, fill=(55, 65, 80))
    img.save(STORY_DIR / "transfer_function_design.png")


def smoothstep(x, edge0, edge1):
    t = min(max((x - edge0) / (edge1 - edge0), 0), 1)
    return t * t * (3 - 2 * t)


def draw_atlas(volumes_cache, metrics):
    w, h = 1800, 1300
    img = Image.new("RGB", (w, h), (241, 245, 250))
    draw = ImageDraw.Draw(img)
    draw.text((65, 40), "Nyx 宇宙网演化图谱：从雾到骨架", font=FONT_L, fill=(16, 40, 72))
    draw.text((65, 98), "四个代表时间步展示密度结构如何由弥散背景收缩为节点、丝束和空洞边界。", font=FONT, fill=(70, 80, 95))
    slots = [(70, 170), (500, 170), (930, 170), (1360, 170)]
    for idx, pos in zip([0, 30, 60, 99], slots):
        x, y = pos
        draw.rounded_rectangle((x, y, x + 370, y + 485), radius=12, fill=(255, 255, 255), outline=(210, 218, 230), width=2)
        pimg = representative_panel_image(idx, volumes_cache, (330, 330))
        img.paste(pimg, (x + 20, y + 20))
        m = metrics[idx]
        draw.text((x + 22, y + 365), f"t{idx:04d}", font=FONT_B, fill=(24, 55, 92))
        draw.text((x + 22, y + 405), f"std {m['std_density']:.4f}", font=FONT, fill=(65, 74, 90))
        draw.text((x + 22, y + 438), f"max {m['max_density']:.4f}", font=FONT, fill=(65, 74, 90))
    narrative = [
        ("阶段 1：微弱扰动", "密度整体集中，结构像尚未成形的暗雾。"),
        ("阶段 2：丝状牵引", "物质向势阱聚集，丝状连接开始变得稳定。"),
        ("阶段 3：节点增强", "高密度节点抬升，空洞边界更清楚。"),
        ("阶段 4：宇宙网显影", "高密度尾部对应致密节点，低密度区扩张为空洞。"),
    ]
    for i, (title, body) in enumerate(narrative):
        x = 120 + i * 420
        y = 750
        draw.rounded_rectangle((x, y, x + 350, y + 220), radius=10, fill=(255, 255, 255), outline=(210, 218, 230), width=2)
        draw.text((x + 18, y + 18), title, font=FONT_B, fill=(34, 74, 118))
        draw_wrapped_text(draw, (x + 18, y + 70), body, FONT, (65, 74, 90), 310)
    draw.text((65, 1080), "设计意图：用同一传递函数对比不同时间步，避免每帧自适应调色造成的视觉误判。", font=FONT, fill=(70, 80, 95))
    draw.text((65, 1125), "分析指向：体绘制给空间证据，直方图给统计证据，刷选把二者在同一阈值下联动。", font=FONT, fill=(70, 80, 95))
    img.save(STORY_DIR / "cosmic_web_atlas.png")


def representative_panel_image(index, volumes_cache, size):
    if index in volumes_cache:
        return projection_image(volumes_cache[index], size)

    rendered = RESULTS_DIR / "02_volume_render" / f"volume_t{index:04d}.png"
    if rendered.exists():
        with Image.open(rendered).convert("RGB") as src:
            w, h = src.size
            crop_top = min(70, h // 8)
            crop = src.crop((0, crop_top, w, h))
            crop.thumbnail(size, Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", size, (248, 250, 252))
            canvas.paste(crop, ((size[0] - crop.width) // 2, (size[1] - crop.height) // 2))
            return canvas

    raise FileNotFoundError(f"Missing raw volume and rendered fallback for timestep {index:04d}.")


def draw_interaction_storyboard():
    w, h = 1600, 960
    img = Image.new("RGB", (w, h), (242, 246, 251))
    draw = ImageDraw.Draw(img)
    draw.text((60, 38), "相空间刷选仪表盘：从一段直方图尾部找到三维宇宙网节点", font=FONT_L, fill=(16, 40, 72))
    draw.text((60, 96), "用户框选密度区间，系统实时联动空间视图，验证统计异常是否对应物理结构。", font=FONT, fill=(70, 80, 95))
    draw.rounded_rectangle((70, 165, 760, 790), radius=12, fill=(255, 255, 255), outline=(210, 218, 230), width=2)
    hist = Image.open(RESULTS_DIR / "03_histograms" / "histogram_t0099.png").convert("RGB").resize((620, 430), Image.Resampling.LANCZOS)
    img.paste(hist, (105, 205))
    draw.rectangle((565, 228, 690, 600), outline=(220, 80, 70), width=5)
    draw.text((115, 670), "框选：99% - 100% 高密度尾部", font=FONT_B, fill=(170, 55, 50))

    draw.rounded_rectangle((840, 165, 1530, 790), radius=12, fill=(255, 255, 255), outline=(210, 218, 230), width=2)
    sel = Image.open(RESULTS_DIR / "05_interaction_selection" / "top1_percent_t0099.png").convert("RGB").resize((620, 430), Image.Resampling.LANCZOS)
    img.paste(sel, (875, 205))
    draw.text((900, 670), "联动：只渲染匹配阈值的高密度体素", font=FONT_B, fill=(34, 74, 118))

    draw.line((760, 475, 840, 475), fill=(37, 99, 160), width=8)
    draw.polygon([(840, 475), (815, 458), (815, 492)], fill=(37, 99, 160))
    draw.text((110, 840), "结论：直方图尾部的 1% 单元格集中落在宇宙网节点和致密丝束上，统计特征可被空间结构解释。", font=FONT, fill=(70, 80, 95))
    img.save(STORY_DIR / "interaction_storyboard.png")


def draw_video_frame(index, volume, metrics, all_metrics, hist_image):
    w, h = 1280, 720
    img = Image.new("RGB", (w, h), (9, 14, 28))
    draw = ImageDraw.Draw(img)
    proj = projection_image(volume, (520, 520))
    img.paste(proj, (45, 115))
    draw.text((45, 36), "Nyx Cosmic Web Evolution", font=FONT_L, fill=(238, 244, 255))
    draw.text((45, 82), f"timestep {index:04d} / 0099", font=FONT, fill=(185, 200, 220))
    draw.text((615, 70), "density field -> statistics -> selected structure", font=FONT, fill=(185, 200, 220))

    panel = (615, 125, 1225, 625)
    draw.rounded_rectangle(panel, radius=14, fill=(248, 250, 252), outline=(80, 100, 130), width=2)
    m = metrics[index]
    lines = [
        f"std density: {m['std_density']:.4f}",
        f"max density: {m['max_density']:.4f}",
        f"P99 - P01: {m['spread_p99_p01']:.4f}",
        f"void fraction vs t0000 P05: {m['void_fraction_vs_t0000_p05']*100:.2f}%",
        f"dense fraction vs t0000 P95: {m['dense_fraction_vs_t0000_p95']*100:.2f}%",
    ]
    y = 155
    for line in lines:
        draw.text((645, y), line, font=FONT, fill=(30, 45, 65))
        y += 38
    mini = hist_image.resize((520, 210), Image.Resampling.LANCZOS)
    img.paste(mini, (660, 375))
    x = 660 + int(index / 99 * 520)
    draw.line((x, 375, x, 585), fill=(255, 85, 75), width=4)
    return img


def create_video(metrics):
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    hist_image = Image.open(STORY_DIR / "histogram_temporal_heatmap.png").convert("RGB")
    for i in range(100):
        v = read_volume(i)
        frame = draw_video_frame(i, v, metrics, metrics, hist_image)
        frame.save(FRAME_DIR / f"frame_{i:04d}.png")
    out = VIDEO_DIR / "demo.mp4"
    cmd = [
        FFMPEG, "-y", "-framerate", "12", "-i", str(FRAME_DIR / "frame_%04d.png"),
        "-vf", "format=yuv420p", "-movflags", "+faststart", str(out)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    STORY_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(exist_ok=True)
    if raw_sequence_available():
        bins, hist, metrics, volumes_cache = compute_histograms_and_metrics()
        draw_heatmap(bins, hist)
        create_video(metrics)
    else:
        metrics = read_existing_metrics()
        volumes_cache = {}
        print("Raw data files are not present; rebuilding static story images from existing results.")

    draw_metrics_dashboard(metrics)
    draw_transfer_function()
    draw_atlas(volumes_cache, metrics)
    draw_interaction_storyboard()
    print(STORY_DIR)
    print(VIDEO_DIR / "demo.mp4")


if __name__ == "__main__":
    main()
