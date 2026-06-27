#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Nyx Web 可视化数据预处理脚本。

功能：
1. 从原项目 data/raw/ 读取 Nyx little-endian float32 二进制体数据。
2. 自动推断 n x n x n 网格尺寸，并从 z-y-x 线性顺序恢复到 x-y-z。
3. 计算 log-density、百分位阈值、统计量和统一 bins 直方图。
4. 将每个时间步降采样后保存为浏览器可懒加载的 Float32Array 二进制文件。
5. 复制报告图像到 Web assets/images，生成 metadata/stats/histogram/heatmap 等 JSON。

运行示例：
python Nyx_Web_Visualization/scripts/preprocess_for_web.py --input data/raw --output Nyx_Web_Visualization/web/assets/data --size 64
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import warnings
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np


EPS = np.finfo(np.float32).eps
HIST_BINS = 120


def find_project_root() -> Path:
    """根据脚本位置推断项目根目录。"""
    return Path(__file__).resolve().parents[2]


def ensure_dir(path: Path) -> None:
    """确保目录存在。"""
    path.mkdir(parents=True, exist_ok=True)


def infer_grid_size(num_values: int) -> int:
    """根据体素数量自动推断立方体网格边长。"""
    n = round(num_values ** (1.0 / 3.0))
    if n ** 3 != num_values:
        raise ValueError(f"文件体素数量 {num_values} 不能构成立方体网格。")
    return int(n)


def read_nyx_dat(path: Path) -> np.ndarray:
    """读取 Nyx .dat 文件，并从 z-y-x 存储顺序恢复为 x-y-z 三维体。"""
    data = np.fromfile(path, dtype="<f4")
    if data.size == 0:
        raise ValueError(f"{path.name} 为空文件。")
    n = infer_grid_size(int(data.size))
    v_zyx = data.reshape((n, n, n), order="C")
    volume = np.transpose(v_zyx, (2, 1, 0)).astype(np.float32, copy=False)
    return volume


def downsample_volume(volume: np.ndarray, target_size: int) -> np.ndarray:
    """
    将三维体降采样到 target_size^3。

    若原始尺寸可被目标尺寸整除，则使用块平均；否则使用最近邻采样。
    块平均更平滑，最近邻作为通用降级方案。
    """
    n = volume.shape[0]
    if n == target_size:
        return volume.astype(np.float32, copy=False)
    if n > target_size and n % target_size == 0:
        f = n // target_size
        v = volume.reshape(target_size, f, target_size, f, target_size, f)
        return v.mean(axis=(1, 3, 5), dtype=np.float32).astype(np.float32)
    idx = np.linspace(0, n - 1, target_size).round().astype(np.int64)
    return volume[np.ix_(idx, idx, idx)].astype(np.float32, copy=False)


def normalize_percentile(values: np.ndarray, lower_pct: float = 5, upper_pct: float = 99.7) -> Tuple[np.ndarray, float, float]:
    """按百分位裁剪并归一化到 [0, 1]。"""
    low = float(np.percentile(values, lower_pct))
    high = float(np.percentile(values, upper_pct))
    if high <= low:
        return np.zeros_like(values, dtype=np.float32), low, high
    clipped = np.clip(values, low, high)
    normalized = (clipped - low) / (high - low)
    return normalized.astype(np.float32), low, high


def percentile_dict(density: np.ndarray) -> Dict[str, float]:
    """计算网页和报告中需要使用的密度百分位。"""
    pcts = [1, 5, 50, 95, 99, 99.7, 99.9]
    vals = np.percentile(density.astype(np.float64).ravel(), pcts)
    return {
        "P01": float(vals[0]),
        "P05": float(vals[1]),
        "P50": float(vals[2]),
        "P95": float(vals[3]),
        "P99": float(vals[4]),
        "P997": float(vals[5]),
        "P999": float(vals[6]),
    }


def stats_from_density(time_index: int, filename: str, density: np.ndarray) -> Dict[str, Any]:
    """计算单个时间步的统计量。"""
    flat = density.astype(np.float64).ravel()
    p = percentile_dict(density)
    mean_density = float(np.mean(flat))
    row: Dict[str, Any] = {
        "time_index": int(time_index),
        "filename": filename,
        "mean_density": mean_density,
        "std_density": float(np.std(flat)),
        "min_density": float(np.min(flat)),
        "max_density": float(np.max(flat)),
        **p,
        "P99_over_mean": float(p["P99"] / mean_density) if mean_density != 0 else None,
        "P99_minus_P01": float(p["P99"] - p["P01"]),
    }
    return row


def read_density_stats_csv(csv_path: Path) -> Dict[str, Dict[str, Any]]:
    """读取已有 density_stats.csv，用文件名作为索引，缺失时返回空字典。"""
    if not csv_path.exists():
        return {}
    rows: Dict[str, Dict[str, Any]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            filename = row.get("filename", "")
            if not filename:
                continue
            cleaned: Dict[str, Any] = {}
            for k, v in row.items():
                if k == "filename":
                    cleaned[k] = v
                elif k == "time_index":
                    cleaned[k] = int(float(v))
                else:
                    try:
                        cleaned[k] = float(v)
                    except (TypeError, ValueError):
                        cleaned[k] = v
            # 兼容 MATLAB 导出的字段命名
            if "p99_density" in cleaned and "P99" not in cleaned:
                cleaned["P99"] = cleaned["p99_density"]
            if "p01_density" in cleaned and "P01" not in cleaned:
                cleaned["P01"] = cleaned["p01_density"]
            if "p05_density" in cleaned and "P05" not in cleaned:
                cleaned["P05"] = cleaned["p05_density"]
            if "p50_density" in cleaned and "P50" not in cleaned:
                cleaned["P50"] = cleaned["p50_density"]
            if "p95_density" in cleaned and "P95" not in cleaned:
                cleaned["P95"] = cleaned["p95_density"]
            if "max_density" in cleaned and "max_density" not in cleaned:
                cleaned["max_density"] = cleaned["max_density"]
            if "mean_density" in cleaned and "P99" in cleaned:
                mean = float(cleaned["mean_density"])
                cleaned["P99_over_mean"] = float(cleaned["P99"] / mean) if mean != 0 else None
            if "P99" in cleaned and "P01" in cleaned:
                cleaned["P99_minus_P01"] = float(cleaned["P99"] - cleaned["P01"])
            rows[filename] = cleaned
    return rows


def read_simple_csv(csv_path: Path) -> List[Dict[str, Any]]:
    """读取通用 CSV，用于 hessian_fraction 和 stage 信息。"""
    if not csv_path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned: Dict[str, Any] = {}
            for k, v in row.items():
                if v is None:
                    cleaned[k] = None
                    continue
                try:
                    fv = float(v)
                    cleaned[k] = int(fv) if fv.is_integer() and k.endswith("index") else fv
                except ValueError:
                    cleaned[k] = v
            out.append(cleaned)
    return out


def save_json(path: Path, data: Any) -> None:
    """保存浏览器可直接 fetch 的 JSON。"""
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def copy_report_images(project_root: Path, web_root: Path) -> None:
    """复制报告和结果图片到 Web assets/images。"""
    image_dir = web_root / "assets" / "images"
    ensure_dir(image_dir)
    candidates = [
        project_root / "results" / "report_figures",
        project_root / "results" / "04_volume_render",
        project_root / "results" / "02_histograms",
        project_root / "results" / "05_high_density",
        project_root / "results" / "06_structure_metrics",
        project_root / "results" / "07_dashboard",
    ]
    wanted = {
        "iteration_roadmap.png",
        "overall_workflow.png",
        "nyx_keyword_wordcloud.png",
        "nyx_method_bubble_tags.png",
        "volume_keyframes_compare.png",
        "transfer_function_design.png",
        "time_density_heatmap.png",
        "nested_isosurfaces_t0099.png",
        "dashboard_preview.png",
        "combined_statistics_curves.png",
        "combined_top1_percent_mips.png",
        "density_gradient_phase_compare.png",
        "hessian_class_slice_compare.png",
        "time_step_similarity_matrix.png",
        "evolution_stage_segmentation.png",
    }
    copied = set()
    for directory in candidates:
        if not directory.exists():
            continue
        for src in directory.glob("*.png"):
            if src.name in wanted or src.name not in copied:
                dst = image_dir / src.name
                shutil.copy2(src, dst)
                copied.add(src.name)


def build_web_data(input_dir: Path, output_dir: Path, target_size: int, max_steps: int | None = None) -> List[Path]:
    """主预处理流程。"""
    project_root = find_project_root()
    web_root = project_root / "Nyx_Web_Visualization" / "web"
    volume_dir = output_dir / "volumes"
    ensure_dir(output_dir)
    ensure_dir(volume_dir)
    copy_report_images(project_root, web_root)

    dat_files = sorted([p for p in input_dir.glob("*.dat") if p.stat().st_size > 0])
    if max_steps is not None:
        dat_files = dat_files[:max_steps]
    if not dat_files:
        raise FileNotFoundError(f"未在 {input_dir} 找到非空 .dat 文件。")

    processed_dir = project_root / "data" / "processed"
    existing_stats = read_density_stats_csv(processed_dir / "density_stats.csv")
    valid_records: List[Tuple[Path, np.ndarray, np.ndarray, Dict[str, Any], float, float]] = []
    log_min_global = math.inf
    log_max_global = -math.inf
    original_grid_size = None

    print(f"发现 {len(dat_files)} 个候选 .dat 文件，开始读取和统计。")
    for i, path in enumerate(dat_files):
        try:
            density = read_nyx_dat(path)
        except Exception as exc:
            warnings.warn(f"跳过 {path.name}: {exc}")
            continue
        if original_grid_size is None:
            original_grid_size = int(density.shape[0])
        log_v = np.log10(np.maximum(density, EPS)).astype(np.float32)
        log_min_global = min(log_min_global, float(log_v.min()))
        log_max_global = max(log_max_global, float(log_v.max()))
        if path.name in existing_stats:
            stats = existing_stats[path.name]
            stats.setdefault("time_index", len(valid_records))
            stats.setdefault("filename", path.name)
            if "P99_over_mean" not in stats and "P99" in stats and "mean_density" in stats:
                mean = float(stats["mean_density"])
                stats["P99_over_mean"] = float(stats["P99"] / mean) if mean != 0 else None
            if "P99_minus_P01" not in stats and "P99" in stats and "P01" in stats:
                stats["P99_minus_P01"] = float(stats["P99"] - stats["P01"])
        else:
            stats = stats_from_density(len(valid_records), path.name, density)
        _, norm_low, norm_high = normalize_percentile(log_v, 5, 99.7)
        stats["log_norm_P5"] = norm_low
        stats["log_norm_P997"] = norm_high
        valid_records.append((path, density, log_v, stats, norm_low, norm_high))
        print(f"  [{len(valid_records):03d}] {path.name} 读取完成。")

    if not valid_records:
        raise RuntimeError("没有可用的 .dat 文件。")

    hist_edges = np.linspace(log_min_global, log_max_global, HIST_BINS + 1, dtype=np.float64)
    hist_centers = ((hist_edges[:-1] + hist_edges[1:]) * 0.5).astype(float)
    stats_rows: List[Dict[str, Any]] = []
    hist_rows: List[Dict[str, Any]] = []
    heatmap_values: List[List[float]] = []
    metadata_steps: List[Dict[str, Any]] = []
    output_paths: List[Path] = []

    for t, (path, density, log_v, stats, norm_low, norm_high) in enumerate(valid_records):
        norm_v, _, _ = normalize_percentile(log_v, 5, 99.7)
        small = downsample_volume(norm_v, target_size)
        vol_path = volume_dir / f"vol_{t:04d}.bin"
        small.astype("<f4", copy=False).tofile(vol_path)
        output_paths.append(vol_path)

        counts, _ = np.histogram(log_v.ravel(), bins=hist_edges)
        prob = counts.astype(np.float64)
        if prob.sum() > 0:
            prob = prob / prob.sum()

        row = {
            "time_index": int(t),
            "source_filename": path.name,
            "volume_file": f"volumes/vol_{t:04d}.bin",
            "bins": hist_centers.tolist(),
            "probability": prob.astype(float).tolist(),
        }
        hist_rows.append(row)
        heatmap_values.append(prob.astype(float).tolist())

        clean_stats = {
            "time_index": int(t),
            "filename": path.name,
            "mean_density": float(stats.get("mean_density", np.mean(density))),
            "std_density": float(stats.get("std_density", np.std(density))),
            "max_density": float(stats.get("max_density", np.max(density))),
            "P01": float(stats.get("P01", np.percentile(density, 1))),
            "P05": float(stats.get("P05", np.percentile(density, 5))),
            "P50": float(stats.get("P50", np.percentile(density, 50))),
            "P95": float(stats.get("P95", np.percentile(density, 95))),
            "P99": float(stats.get("P99", np.percentile(density, 99))),
            "P99_over_mean": float(stats.get("P99_over_mean", np.percentile(density, 99) / max(np.mean(density), EPS))),
            "P99_minus_P01": float(stats.get("P99_minus_P01", np.percentile(density, 99) - np.percentile(density, 1))),
        }
        stats_rows.append(clean_stats)
        metadata_steps.append({
            "time_index": int(t),
            "filename": path.name,
            "volume_file": f"volumes/vol_{t:04d}.bin",
            "density_min": float(np.min(density)),
            "density_max": float(np.max(density)),
            "density_mean": float(np.mean(density)),
            "density_std": float(np.std(density)),
            "log_density_min": float(np.min(log_v)),
            "log_density_max": float(np.max(log_v)),
            "log_norm_P5": float(norm_low),
            "log_norm_P997": float(norm_high),
        })

    hessian_fraction = read_simple_csv(processed_dir / "hessian_cosmic_web_fraction.csv")
    time_stage = read_simple_csv(processed_dir / "time_similarity_stage.csv")
    if not time_stage:
        n_steps = len(valid_records)
        labels = ["Early", "Transition", "Structure Enhancement", "Late"]
        time_stage = []
        for i in range(n_steps):
            stage_idx = min(3, int(i / max(n_steps, 1) * 4))
            time_stage.append({
                "time_index": i,
                "filename": valid_records[i][0].name,
                "distance_from_start": float(i / max(n_steps - 1, 1)),
                "adjacent_distance": 0.0,
                "stage_label": labels[stage_idx],
            })

    metadata = {
        "project": "Nyx Density Explorer",
        "description": "Web 展示使用降采样 normalized log-density 体数据；统计结论用于数据可视化课程实验。",
        "original_grid_size": int(original_grid_size or 0),
        "web_grid_size": int(target_size),
        "time_steps": len(valid_records),
        "file_names": [r[0].name for r in valid_records],
        "volume_dtype": "float32",
        "volume_value_range": [0.0, 1.0],
        "histogram_bins": HIST_BINS,
        "histogram_log_density_range": [float(log_min_global), float(log_max_global)],
        "steps": metadata_steps,
    }

    save_json(output_dir / "metadata.json", metadata)
    save_json(output_dir / "density_stats.json", stats_rows)
    save_json(output_dir / "histograms.json", {"bins": hist_centers.tolist(), "items": hist_rows})
    save_json(output_dir / "time_density_heatmap.json", {
        "x": [int(i) for i in range(len(valid_records))],
        "y": hist_centers.tolist(),
        "values": heatmap_values,
    })
    save_json(output_dir / "hessian_fraction.json", hessian_fraction)
    save_json(output_dir / "time_similarity_stage.json", time_stage)

    output_paths.extend([
        output_dir / "metadata.json",
        output_dir / "density_stats.json",
        output_dir / "histograms.json",
        output_dir / "time_density_heatmap.json",
        output_dir / "hessian_fraction.json",
        output_dir / "time_similarity_stage.json",
    ])
    return output_paths


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="为 Nyx Web 可视化生成轻量数据。")
    parser.add_argument("--input", default="data/raw", help="原始 .dat 数据目录。")
    parser.add_argument("--output", default="Nyx_Web_Visualization/web/assets/data", help="Web 数据输出目录。")
    parser.add_argument("--size", type=int, default=64, help="Web 降采样网格边长，默认 64。")
    parser.add_argument("--max-steps", type=int, default=None, help="可选：最多处理多少个时间步，调试时可使用。")
    return parser.parse_args()


def main() -> None:
    """脚本入口。"""
    project_root = find_project_root()
    args = parse_args()
    input_dir = (project_root / args.input).resolve() if not Path(args.input).is_absolute() else Path(args.input)
    output_dir = (project_root / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    paths = build_web_data(input_dir, output_dir, args.size, args.max_steps)
    print("\nWeb 数据生成完成，输出文件如下：")
    for path in paths:
        try:
            print(" -", path.relative_to(project_root))
        except ValueError:
            print(" -", path)


if __name__ == "__main__":
    main()
