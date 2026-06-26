from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
OUT_ZIP = ROOT / "final_submit" / "学号_姓名_Nyx科学可视化.zip"

REQUIRED_FILES = [
    "README.txt",
    "code/main.m",
    "code/interactive_dashboard.m",
    "code/read_nyx_dat.m",
    "data/processed/density_stats.csv",
    "data/processed/high_density_threshold.csv",
    "data/processed/statistics.mat",
    "data/processed/structure_metrics.csv",
    "results/02_volume_render/volume_t0000.png",
    "results/02_volume_render/volume_t0099.png",
    "results/03_histograms/histogram_t0099.png",
    "results/05_interaction_selection/top1_percent_t0099.png",
    "results/07_visual_story/cosmic_web_atlas.png",
    "results/07_visual_story/histogram_temporal_heatmap.png",
    "results/07_visual_story/interaction_storyboard.png",
    "results/07_visual_story/structure_metrics_dashboard.png",
    "results/07_visual_story/transfer_function_design.png",
    "report/Answer_Sheet.docx",
    "report/Answer_Sheet.pdf",
    "report/技术报告.docx",
    "report/技术报告.pdf",
    "video/demo.mp4",
]

OPTIONAL_FILES = [
    "任务要求.txt",
]

EXCLUDED_DIRS = {
    "__pycache__",
    "rendered_report",
    "frames",
}


def require_outputs():
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        raise FileNotFoundError("Missing required submission files:\n" + "\n".join(missing))


def should_include(path):
    if any(part in EXCLUDED_DIRS for part in path.parts):
        return False
    if path.name.startswith("~$"):
        return False
    return path.is_file()


def add_tree(zf, source_dir, archive_prefix):
    for path in sorted(source_dir.rglob("*")):
        if not should_include(path):
            continue
        arcname = Path(archive_prefix) / path.relative_to(source_dir)
        zf.write(path, arcname.as_posix())


def add_file(zf, rel_path):
    path = ROOT / rel_path
    if path.is_file():
        zf.write(path, Path(rel_path).as_posix())


def validate_zip(path):
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())

    missing = [p.replace("\\", "/") for p in REQUIRED_FILES if p.replace("\\", "/") not in names]
    if missing:
        raise RuntimeError("Zip is missing required paths:\n" + "\n".join(missing))

    stale = [name for name in names if name.startswith("processed/") or name == "demo.mp4" or name.startswith("report/rendered_report/")]
    if stale:
        raise RuntimeError("Zip contains stale paths:\n" + "\n".join(sorted(stale)))


def build_zip():
    require_outputs()
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)
    tmp_zip = OUT_ZIP.with_suffix(".tmp")
    if tmp_zip.exists():
        tmp_zip.unlink()

    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        add_tree(zf, ROOT / "code", "code")
        add_tree(zf, ROOT / "data" / "processed", "data/processed")
        add_tree(zf, ROOT / "results", "results")
        add_tree(zf, ROOT / "report", "report")
        add_file(zf, "video/demo.mp4")
        add_file(zf, "README.txt")
        for rel_path in OPTIONAL_FILES:
            add_file(zf, rel_path)

    validate_zip(tmp_zip)
    tmp_zip.replace(OUT_ZIP)
    return OUT_ZIP


if __name__ == "__main__":
    out = build_zip()
    with zipfile.ZipFile(out) as zf:
        print(out)
        print(f"{len(zf.infolist())} files, {out.stat().st_size} bytes")
