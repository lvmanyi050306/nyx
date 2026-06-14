Nyx Scientific Visualization Project

Project structure:
- data/raw: raw Nyx .dat files, named 0000.dat to 0099.dat.
- data/processed: generated statistics, threshold tables, and structure metrics.
- code: MATLAB scripts for data checking, statistics, rendering, histograms, and high-density selection.
- results: generated figures grouped by task.
- report: technical report and answer sheet.
- video: demonstration video.
- final_submit: final compressed submission package.

Recommended MATLAB entry point:
1. Open MATLAB in this project root.
2. Run code/main.m.
3. Run interactive_dashboard(fullfile(pwd, "data", "raw"), "0099") for linked brushing.

Multi-software workflow:
- MATLAB R2024b: reads Nyx float32 little-endian volumes, computes statistics, renders volumes and histograms, and opens the linked brushing dashboard.
- Python: combines MATLAB outputs into story images, creates DOCX/PDF reports, computes extra structure metrics, and prepares video frames.
- FFmpeg: encodes the 100-frame evolution storyboard into video/demo.mp4.

Important generated assets:
- results/07_visual_story/cosmic_web_atlas.png
- results/07_visual_story/histogram_temporal_heatmap.png
- results/07_visual_story/structure_metrics_dashboard.png
- results/07_visual_story/transfer_function_design.png
- results/07_visual_story/interaction_storyboard.png
- video/demo.mp4
